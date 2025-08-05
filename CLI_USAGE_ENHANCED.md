# InvenTag CLI - Complete Usage Guide

## Quick Start

```bash
# Quick demo with default credentials
./examples/quick_start.sh

# Basic single account BOM generation
python -m inventag.cli.main --create-excel --create-word
```

## Core BOM Generation Commands

### Single Account Operations
```bash
# Basic BOM generation with Excel and Word formats
python -m inventag.cli.main --create-excel --create-word

# BOM with comprehensive analysis enabled
python -m inventag.cli.main --create-excel --create-word \
  --enable-network-analysis --enable-security-analysis --enable-cost-analysis

# BOM with custom output directory and verbose logging
python -m inventag.cli.main --create-excel --create-word \
  --output-directory ./custom-reports --verbose

# BOM with specific regions and services
python -m inventag.cli.main --create-excel \
  --account-regions us-east-1,us-west-2,eu-west-1 \
  --account-services ec2,s3,rds,lambda
```

### Multi-Account Operations
```bash
# Multi-account BOM from configuration file
python -m inventag.cli.main --accounts-file examples/accounts_basic.json \
  --create-excel --create-word --verbose

# Interactive multi-account setup
python -m inventag.cli.main --accounts-prompt \
  --create-excel --create-word --verbose

# Cross-account role assumption
python -m inventag.cli.main --cross-account-role InvenTagCrossAccountRole \
  --create-excel --account-regions us-east-1,us-west-2

# Multi-account with parallel processing control
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --max-concurrent-accounts 6 \
  --account-processing-timeout 3600
```

## Production Safety and Security Commands

### Security Validation
```bash
# Enable comprehensive security validation
python -m inventag.cli.main --create-excel \
  --enable-production-safety --security-validation \
  --enforce-read-only --risk-threshold HIGH

# Compliance-specific BOM generation
python -m inventag.cli.main --create-excel \
  --compliance-standard soc2 --audit-output compliance-audit.json

# Validate specific AWS operations before BOM generation
python -m inventag.cli.main --create-excel \
  --validate-operations ec2:describe_instances s3:list_buckets iam:list_users

# Production safety with custom risk threshold
python -m inventag.cli.main --create-excel \
  --enable-production-safety --risk-threshold CRITICAL \
  --audit-output production-safety-audit.json
```

### Production Monitoring Scripts
```bash
# Real-time production safety monitoring
python scripts/production_monitor.py \
  --operations ec2:describe_instances s3:list_buckets \
  --report-output production-monitor-report.json --verbose

# Security validation for inventory operations
python scripts/security_validator.py --validate-inventory \
  --enforce-read-only --risk-threshold HIGH \
  --audit-output security-validation.json

# Multi-account security scanning
python scripts/multi_account_scanner.py \
  --accounts-file examples/accounts_basic.json \
  --enable-security-analysis --enable-network-analysis \
  --output-format excel json --verbose
```

## Advanced Analysis Commands

### Network and Security Analysis
```bash
# Comprehensive network analysis
python -m inventag.cli.main --create-excel \
  --enable-network-analysis --enable-security-analysis \
  --service-descriptions config/service_descriptions_example.yaml

# VPC and subnet utilization analysis
python -m inventag.cli.main --create-excel \
  --enable-network-analysis --account-services vpc,ec2 \
  --account-regions us-east-1,us-west-2

# Security group and NACL analysis
python -m inventag.cli.main --create-excel \
  --enable-security-analysis --account-services vpc,ec2 \
  --tag-mappings config/tag_mappings_example.yaml
```

### Cost Analysis and Optimization
```bash
# Cost analysis with optimization recommendations
python -m inventag.cli.main --create-excel \
  --enable-cost-analysis --create-word \
  --output-directory cost-analysis-reports

# Multi-account cost analysis
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --enable-cost-analysis \
  --max-concurrent-accounts 8
```

## CI/CD Integration Commands

### S3 Upload and Automation
```bash
# CI/CD with S3 upload
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --s3-bucket my-bom-reports \
  --s3-key-prefix "bom-reports/$(date +%Y-%m-%d)/" \
  --s3-encryption aws:kms --s3-kms-key-id alias/bom-encryption

# Automated BOM generation with state management
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --enable-state-management \
  --enable-delta-detection --generate-changelog

# GitHub Actions compatible command
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --create-word --verbose \
  --s3-bucket $BOM_REPORTS_BUCKET \
  --s3-key-prefix "github-actions/$(date +%Y-%m-%d)/"
```

### Configuration Management
```bash
# BOM with comprehensive configuration
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --create-word \
  --service-descriptions config/service_descriptions_example.yaml \
  --tag-mappings config/tag_mappings_example.yaml \
  --bom-config config/complete_configuration_example.yaml

# Configuration validation only
python -m inventag.cli.main --validate-config \
  --accounts-file accounts.json \
  --service-descriptions config/service_descriptions_example.yaml \
  --tag-mappings config/tag_mappings_example.yaml
```

## State Management and Change Tracking

### Delta Detection and Changelog
```bash
# Full state management with change tracking
python -m inventag.cli.main --create-excel \
  --enable-state-management --enable-delta-detection \
  --generate-changelog --output-directory state-tracking

# Compare with previous state
python -m inventag.cli.main --create-excel \
  --enable-delta-detection --generate-changelog \
  --per-account-reports

# Disable state management for one-time scans
python -m inventag.cli.main --create-excel \
  --disable-state-management --disable-delta-detection
```

## Debug and Troubleshooting Commands

### Logging and Debug
```bash
# Debug mode with comprehensive logging
python -m inventag.cli.main --create-excel --debug \
  --log-file inventag-debug.log --verbose

# Credential validation before processing
python -m inventag.cli.main --validate-credentials \
  --accounts-file accounts.json --credential-timeout 60

# Account-specific debug
python -m inventag.cli.main --create-excel --debug \
  --accounts-file accounts.json --disable-parallel-processing
```

### Performance Optimization
```bash
# High-performance multi-account processing
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --max-concurrent-accounts 10 \
  --account-processing-timeout 3600 \
  --enable-parallel-processing

# Memory-optimized processing
python -m inventag.cli.main --create-excel \
  --disable-delta-detection --disable-state-management \
  --account-services ec2,s3,rds
```

## Specialized Use Cases

### Compliance and Audit
```bash
# SOC 2 compliance BOM
python -m inventag.cli.main --create-excel \
  --compliance-standard soc2 --enable-production-safety \
  --security-validation --audit-output soc2-compliance.json

# HIPAA compliance with enhanced security
python -m inventag.cli.main --create-excel \
  --compliance-standard hipaa --risk-threshold CRITICAL \
  --enforce-read-only --enable-security-analysis

# PCI compliance with network analysis
python -m inventag.cli.main --create-excel \
  --compliance-standard pci --enable-network-analysis \
  --enable-security-analysis --audit-output pci-audit.json
```

### Enterprise Multi-Account
```bash
# Enterprise-scale multi-account BOM
python -m inventag.cli.main --accounts-file enterprise-accounts.json \
  --create-excel --create-word --create-google-docs \
  --enable-network-analysis --enable-security-analysis --enable-cost-analysis \
  --max-concurrent-accounts 12 --per-account-reports \
  --s3-bucket enterprise-bom-reports

# Multi-region enterprise scan
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --account-regions us-east-1,us-west-2,eu-west-1,ap-southeast-1 \
  --enable-network-analysis --enable-security-analysis \
  --output-directory multi-region-enterprise
```

### DevOps and Infrastructure Teams
```bash
# Infrastructure team BOM with network focus
python -m inventag.cli.main --create-excel \
  --account-services vpc,ec2,elb,rds,elasticache \
  --enable-network-analysis --enable-security-analysis \
  --tag-mappings config/infrastructure-tags.yaml

# Security team BOM with compliance focus
python -m inventag.cli.main --create-excel \
  --account-services iam,kms,secrets-manager,cloudtrail \
  --enable-security-analysis --compliance-standard soc2 \
  --risk-threshold HIGH --audit-output security-team-audit.json

# Cost optimization team BOM
python -m inventag.cli.main --create-excel \
  --enable-cost-analysis --account-services ec2,rds,s3,lambda \
  --create-word --output-directory cost-optimization
```

## Legacy Script Usage (Deprecated but Supported)

```bash
# Basic resource inventory (use CLI instead)
python scripts/aws_resource_inventory.py

# Tag compliance check (use CLI with --compliance-standard instead)
python scripts/tag_compliance_checker.py --config config/tag_policy_example.yaml

# Convert to Excel (use CLI --create-excel instead)
python scripts/bom_converter.py --input examples/basic_inventory_*.json --output report.xlsx
```

## Configuration Files

### Account Configuration Examples
- `examples/accounts_basic.json` - Basic multi-account setup
- `examples/accounts_with_profiles.json` - AWS profile-based authentication
- `examples/accounts_cross_account_roles.json` - Cross-account role assumption
- `examples/accounts_cicd_environment.json` - CI/CD optimized configuration

### Service Configuration Examples
- `config/service_descriptions_example.yaml` - Custom service descriptions
- `config/tag_mappings_example.yaml` - Tag attribute mappings
- `config/complete_configuration_example.yaml` - Comprehensive BOM configuration

## Environment Variables

```bash
# AWS credentials (if not using profiles or roles)
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials

# InvenTag configuration
export INVENTAG_OUTPUT_DIR=./custom-output
export INVENTAG_LOG_LEVEL=DEBUG
export INVENTAG_S3_BUCKET=my-bom-reports
export INVENTAG_COMPLIANCE_STANDARD=soc2
```

## Best Practices

### Production Safety
1. **Always use `--enable-production-safety`** for production environments
2. **Set appropriate `--risk-threshold`** based on your security requirements
3. **Use `--enforce-read-only`** to prevent accidental modifications
4. **Enable `--security-validation`** for comprehensive operation validation
5. **Generate `--audit-output`** for compliance documentation

### Performance Optimization
1. **Use `--max-concurrent-accounts`** to optimize for your infrastructure
2. **Set `--account-processing-timeout`** based on account size
3. **Specify `--account-services`** to limit scope when possible
4. **Use `--account-regions`** to focus on relevant regions

### CI/CD Integration
1. **Use configuration files** instead of command-line arguments
2. **Enable S3 upload** for automated report distribution
3. **Use `--verbose`** for troubleshooting in CI/CD logs
4. **Enable state management** for change tracking over time

### Security and Compliance
1. **Choose appropriate `--compliance-standard`** for your requirements
2. **Use `--enable-security-analysis`** for security posture assessment
3. **Enable `--enable-network-analysis`** for network security review
4. **Generate audit outputs** for compliance documentation