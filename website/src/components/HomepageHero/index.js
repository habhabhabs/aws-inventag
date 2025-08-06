import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';

function HomepageHero() {
  const {siteConfig} = useDocusaurusContext();
  
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroText}>
            <h1 className="hero__title">
              🏷️ {siteConfig.title}
            </h1>
            <p className="hero__subtitle">
              {siteConfig.tagline}
            </p>
            <div className={styles.heroFeatures}>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🛡️</span>
                <span>Production Safety & Security</span>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>📊</span>
                <span>Professional BOM Generation</span>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🔍</span>
                <span>Multi-Account Discovery</span>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🌐</span>
                <span>Advanced Analysis Suite</span>
              </div>
            </div>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg"
                to="/getting-started/quick-start">
                🚀 Quick Start Guide
              </Link>
              <Link
                className="button button--outline button--secondary button--lg"
                to="/user-guides/cli-user-guide">
                📖 User Guide
              </Link>
            </div>
          </div>
          <div className={styles.heroVisual}>
            <div className={styles.tagIcon}>
              <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="heroTagGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{stopColor: '#60a5fa', stopOpacity: 1}} />
                    <stop offset="100%" style={{stopColor: '#3b82f6', stopOpacity: 1}} />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge> 
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                
                {/* Tag shape with glow effect */}
                <path 
                  d="M20 20h40l30 30-30 30H20V20z" 
                  fill="url(#heroTagGradient)" 
                  stroke="white" 
                  strokeWidth="3"
                  filter="url(#glow)"
                />
                {/* Tag hole */}
                <circle cx="40" cy="60" r="8" fill="white"/>
                
                {/* AWS cloud elements */}
                <circle cx="75" cy="35" r="4" fill="rgba(255,255,255,0.8)"/>
                <circle cx="85" cy="40" r="3" fill="rgba(255,255,255,0.6)"/>
                <circle cx="95" cy="35" r="3.5" fill="rgba(255,255,255,0.7)"/>
                
                {/* Animated particles */}
                <circle cx="30" cy="30" r="2" fill="#93c5fd" opacity="0.6">
                  <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite"/>
                </circle>
                <circle cx="70" cy="70" r="1.5" fill="#93c5fd" opacity="0.4">
                  <animate attributeName="opacity" values="0.4;0.8;0.4" dur="3s" repeatCount="indefinite"/>
                </circle>
                <circle cx="85" cy="25" r="1" fill="#93c5fd" opacity="0.5">
                  <animate attributeName="opacity" values="0.5;0.9;0.5" dur="2.5s" repeatCount="indefinite"/>
                </circle>
              </svg>
            </div>
            <div className={styles.badges}>
              <div className={styles.badge}>
                <span className={styles.badgeIcon}>⚡</span>
                <span>CI/CD Ready</span>
              </div>
              <div className={styles.badge}>
                <span className={styles.badgeIcon}>🏢</span>
                <span>Enterprise Grade</span>
              </div>
              <div className={styles.badge}>
                <span className={styles.badgeIcon}>☁️</span>
                <span>AWS Native</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default HomepageHero;