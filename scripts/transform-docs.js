#!/usr/bin/env node

/**
 * Documentation Transformation Pipeline
 * 
 * This script handles GitHub → Docusaurus format transformations
 * with comprehensive validation and fallback strategies.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Configuration
const CONFIG = {
  docsDir: 'docs',
  backupDir: '.docs-backup',
  logFile: 'transform.log',
  validationEnabled: true,
  fallbackEnabled: true,
  dryRun: process.env.DRY_RUN === 'true' || process.argv.includes('--dry-run'),
  verbose: process.env.VERBOSE === 'true' || process.argv.includes('--verbose')
};

// Logging utility
class Logger {
  constructor(logFile) {
    this.logFile = logFile;
    this.logs = [];
  }

  log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data
    };
    
    this.logs.push(logEntry);
    
    if (CONFIG.verbose || level === 'ERROR') {
      console.log(`[${timestamp}] ${level}: ${message}`);
      if (data && CONFIG.verbose) {
        console.log('  Data:', JSON.stringify(data, null, 2));
      }
    }
  }

  info(message, data) { this.log('INFO', message, data); }
  warn(message, data) { this.log('WARN', message, data); }
  error(message, data) { this.log('ERROR', message, data); }
  debug(message, data) { this.log('DEBUG', message, data); }

  writeLogs() {
    const logContent = this.logs.map(entry => 
      `[${entry.timestamp}] ${entry.level}: ${entry.message}` +
      (entry.data ? `\n  Data: ${JSON.stringify(entry.data, null, 2)}` : '')
    ).join('\n');
    
    fs.writeFileSync(CONFIG.logFile, logContent);
  }
}

// File utilities
class FileUtils {
  static createBackup(filePath, backupDir) {
    const relativePath = path.relative(CONFIG.docsDir, filePath);
    const backupPath = path.join(backupDir, relativePath);
    const backupDirPath = path.dirname(backupPath);
    
    if (!fs.existsSync(backupDirPath)) {
      fs.mkdirSync(backupDirPath, { recursive: true });
    }
    
    fs.copyFileSync(filePath, backupPath);
    return backupPath;
  }

  static restoreFromBackup(filePath, backupDir) {
    const relativePath = path.relative(CONFIG.docsDir, filePath);
    const backupPath = path.join(backupDir, relativePath);
    
    if (fs.existsSync(backupPath)) {
      fs.copyFileSync(backupPath, filePath);
      return true;
    }
    return false;
  }

  static calculateChecksum(content) {
    return crypto.createHash('md5').update(content).digest('hex');
  }

  static findMarkdownFiles(dir) {
    const files = [];
    
    function traverse(currentDir) {
      const items = fs.readdirSync(currentDir);
      
      for (const item of items) {
        const fullPath = path.join(currentDir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          // Skip hidden directories and node_modules
          if (!item.startsWith('.') && item !== 'node_modules') {
            traverse(fullPath);
          }
        } else if (item.endsWith('.md') || item.endsWith('.mdx')) {
          files.push(fullPath);
        }
      }
    }
    
    traverse(dir);
    return files;
  }
}

// Transformation engine
class TransformationEngine {
  constructor(logger) {
    this.logger = logger;
    this.transformations = [];
    this.stats = {
      filesProcessed: 0,
      filesTransformed: 0,
      transformationsApplied: 0,
      errors: 0,
      warnings: 0
    };
  }

  // Register transformation functions
  registerTransformation(name, fn, options = {}) {
    this.transformations.push({
      name,
      fn,
      enabled: options.enabled !== false,
      priority: options.priority || 0
    });
    
    // Sort by priority (higher priority first)
    this.transformations.sort((a, b) => b.priority - a.priority);
  }

  // Apply all transformations to content
  transform(content, filePath) {
    let transformedContent = content;
    let hasChanges = false;
    const appliedTransformations = [];

    for (const transformation of this.transformations) {
      if (!transformation.enabled) continue;

      try {
        const result = transformation.fn(transformedContent, filePath);
        
        if (result.hasChanges) {
          transformedContent = result.content;
          hasChanges = true;
          appliedTransformations.push(transformation.name);
          this.stats.transformationsApplied++;
          
          this.logger.debug(`Applied transformation: ${transformation.name}`, {
            file: filePath,
            transformation: transformation.name
          });
        }
      } catch (error) {
        this.logger.error(`Transformation failed: ${transformation.name}`, {
          file: filePath,
          transformation: transformation.name,
          error: error.message
        });
        this.stats.errors++;
        
        if (!CONFIG.fallbackEnabled) {
          throw error;
        }
      }
    }

    return {
      content: transformedContent,
      hasChanges,
      appliedTransformations
    };
  }

  // Process a single file
  async processFile(filePath) {
    this.stats.filesProcessed++;
    
    try {
      const originalContent = fs.readFileSync(filePath, 'utf8');
      const originalChecksum = FileUtils.calculateChecksum(originalContent);
      
      this.logger.debug(`Processing file: ${filePath}`, {
        originalSize: originalContent.length,
        originalChecksum
      });

      const result = this.transform(originalContent, filePath);
      
      if (result.hasChanges) {
        this.stats.filesTransformed++;
        
        if (!CONFIG.dryRun) {
          // Create backup before modifying
          const backupPath = FileUtils.createBackup(filePath, CONFIG.backupDir);
          this.logger.debug(`Created backup: ${backupPath}`);
          
          // Write transformed content
          fs.writeFileSync(filePath, result.content);
          
          // Validate transformation
          if (CONFIG.validationEnabled) {
            const validationResult = await this.validateTransformation(filePath, originalContent, result.content);
            if (!validationResult.isValid) {
              this.logger.warn(`Validation failed for ${filePath}`, validationResult);
              this.stats.warnings++;
              
              if (CONFIG.fallbackEnabled) {
                this.logger.info(`Restoring from backup: ${filePath}`);
                FileUtils.restoreFromBackup(filePath, CONFIG.backupDir);
              }
            }
          }
        }
        
        this.logger.info(`Transformed: ${filePath}`, {
          appliedTransformations: result.appliedTransformations,
          newSize: result.content.length,
          dryRun: CONFIG.dryRun
        });
      } else {
        this.logger.debug(`No changes needed: ${filePath}`);
      }
      
      return result;
    } catch (error) {
      this.stats.errors++;
      this.logger.error(`Failed to process file: ${filePath}`, {
        error: error.message,
        stack: error.stack
      });
      
      if (!CONFIG.fallbackEnabled) {
        throw error;
      }
      
      return { content: null, hasChanges: false, appliedTransformations: [] };
    }
  }

  // Validate transformation results
  async validateTransformation(filePath, originalContent, transformedContent) {
    const validation = {
      isValid: true,
      issues: []
    };

    try {
      // Check if content is still valid markdown
      if (transformedContent.trim().length === 0) {
        validation.isValid = false;
        validation.issues.push('Transformed content is empty');
      }

      // Check for broken frontmatter
      if (transformedContent.startsWith('---')) {
        const frontmatterEnd = transformedContent.indexOf('---', 3);
        if (frontmatterEnd === -1) {
          validation.isValid = false;
          validation.issues.push('Broken frontmatter structure');
        }
      }

      // Check for broken links (basic validation)
      const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
      let match;
      while ((match = linkRegex.exec(transformedContent)) !== null) {
        const linkUrl = match[2];
        
        // Check for obviously broken links
        if (linkUrl.includes('undefined') || linkUrl.includes('null')) {
          validation.isValid = false;
          validation.issues.push(`Broken link detected: ${match[0]}`);
        }
      }

      // Check content length change (shouldn't be drastically different)
      const lengthDiff = Math.abs(transformedContent.length - originalContent.length);
      const lengthChangePercent = (lengthDiff / originalContent.length) * 100;
      
      if (lengthChangePercent > 50) {
        validation.isValid = false;
        validation.issues.push(`Content length changed by ${lengthChangePercent.toFixed(1)}%`);
      }

    } catch (error) {
      validation.isValid = false;
      validation.issues.push(`Validation error: ${error.message}`);
    }

    return validation;
  }

  // Get transformation statistics
  getStats() {
    return { ...this.stats };
  }
}

// Define specific transformations
function createTransformations(logger) {
  const transformations = [];

  // 1. Fix relative markdown links for Docusaurus routing
  transformations.push({
    name: 'fix-markdown-links',
    fn: (content, filePath) => {
      let transformed = content;
      let hasChanges = false;
      
      // Convert [text](../other-file.md) to [text](../other-file)
      // But preserve external links and anchors
      const linkRegex = /\[([^\]]+)\]\(([^)]+\.md)(#[^)]+)?\)/g;
      
      transformed = transformed.replace(linkRegex, (match, text, link, anchor) => {
        // Skip external links
        if (link.startsWith('http') || link.startsWith('mailto:') || link.startsWith('//')) {
          return match;
        }
        
        hasChanges = true;
        const newLink = link.replace(/\.md$/, '');
        return `[${text}](${newLink}${anchor || ''})`;
      });
      
      return { content: transformed, hasChanges };
    },
    priority: 10
  });

  // 2. Ensure proper frontmatter exists
  transformations.push({
    name: 'ensure-frontmatter',
    fn: (content, filePath) => {
      let transformed = content;
      let hasChanges = false;
      
      // Only add frontmatter if it doesn't exist
      if (!transformed.trim().startsWith('---')) {
        const fileName = path.basename(filePath, '.md');
        const title = fileName
          .replace(/[-_]/g, ' ')
          .replace(/\b\w/g, l => l.toUpperCase());
        
        const frontmatter = `---
title: ${title}
---

`;
        transformed = frontmatter + transformed;
        hasChanges = true;
      }
      
      return { content: transformed, hasChanges };
    },
    priority: 5
  });

  // 3. Fix asset paths for dual compatibility
  transformations.push({
    name: 'fix-asset-paths',
    fn: (content, filePath) => {
      let transformed = content;
      let hasChanges = false;
      
      // Fix image paths to be relative to docs root
      const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
      
      transformed = transformed.replace(imageRegex, (match, alt, src) => {
        // Skip external images
        if (src.startsWith('http') || src.startsWith('//')) {
          return match;
        }
        
        // Ensure assets are referenced correctly
        if (src.startsWith('assets/') || src.startsWith('./assets/') || src.startsWith('../assets/')) {
          // Normalize to relative path from current file to assets
          const currentDir = path.dirname(filePath);
          const docsDir = path.resolve(CONFIG.docsDir);
          const relativePath = path.relative(currentDir, docsDir);
          const normalizedPath = path.join(relativePath, 'assets', path.basename(src)).replace(/\\/g, '/');
          
          if (normalizedPath !== src) {
            hasChanges = true;
            return `![${alt}](${normalizedPath})`;
          }
        }
        
        return match;
      });
      
      return { content: transformed, hasChanges };
    },
    priority: 8
  });

  // 4. Clean up common markdown issues
  transformations.push({
    name: 'cleanup-markdown',
    fn: (content, filePath) => {
      let transformed = content;
      let hasChanges = false;
      
      // Fix multiple consecutive empty lines
      const cleanedContent = transformed.replace(/\n{3,}/g, '\n\n');
      if (cleanedContent !== transformed) {
        transformed = cleanedContent;
        hasChanges = true;
      }
      
      // Ensure file ends with single newline
      if (!transformed.endsWith('\n')) {
        transformed += '\n';
        hasChanges = true;
      }
      
      return { content: transformed, hasChanges };
    },
    priority: 1
  });

  return transformations;
}

// Main execution
async function main() {
  const logger = new Logger(CONFIG.logFile);
  
  try {
    logger.info('Starting documentation transformation pipeline', CONFIG);
    
    // Initialize transformation engine
    const engine = new TransformationEngine(logger);
    
    // Register transformations
    const transformations = createTransformations(logger);
    transformations.forEach(t => engine.registerTransformation(t.name, t.fn, { priority: t.priority }));
    
    logger.info(`Registered ${transformations.length} transformations`);
    
    // Create backup directory
    if (!CONFIG.dryRun && !fs.existsSync(CONFIG.backupDir)) {
      fs.mkdirSync(CONFIG.backupDir, { recursive: true });
      logger.info(`Created backup directory: ${CONFIG.backupDir}`);
    }
    
    // Find all markdown files
    const markdownFiles = FileUtils.findMarkdownFiles(CONFIG.docsDir);
    logger.info(`Found ${markdownFiles.length} markdown files to process`);
    
    // Process each file
    for (const filePath of markdownFiles) {
      await engine.processFile(filePath);
    }
    
    // Report statistics
    const stats = engine.getStats();
    logger.info('Transformation completed', stats);
    
    console.log('\n=== Transformation Summary ===');
    console.log(`Files processed: ${stats.filesProcessed}`);
    console.log(`Files transformed: ${stats.filesTransformed}`);
    console.log(`Transformations applied: ${stats.transformationsApplied}`);
    console.log(`Errors: ${stats.errors}`);
    console.log(`Warnings: ${stats.warnings}`);
    console.log(`Dry run: ${CONFIG.dryRun}`);
    
    if (stats.errors > 0) {
      console.log(`\nCheck ${CONFIG.logFile} for detailed error information.`);
      process.exit(1);
    }
    
  } catch (error) {
    logger.error('Pipeline failed', {
      error: error.message,
      stack: error.stack
    });
    console.error('Transformation pipeline failed:', error.message);
    process.exit(1);
  } finally {
    logger.writeLogs();
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
}

module.exports = {
  TransformationEngine,
  FileUtils,
  Logger,
  CONFIG
};