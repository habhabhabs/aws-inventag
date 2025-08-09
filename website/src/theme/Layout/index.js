import React from 'react';
import Layout from '@theme-original/Layout';
import { useEffect } from 'react';

export default function LayoutWrapper(props) {
  useEffect(() => {
    // Get current version dynamically
    const getCurrentVersion = async () => {
      try {
        const response = await fetch('/inventag-aws/version.json');
        const data = await response.json();
        return `v${data.version}`;
      } catch (error) {
        return 'v4.2.6'; // fallback
      }
    };

    // Replace "current" text in sidebar with actual version number
    const replaceVersionText = async () => {
      const currentVersion = await getCurrentVersion();
      
      // Target sidebar menu links that contain "current"
      const menuLinks = document.querySelectorAll('.menu__link');
      menuLinks.forEach(link => {
        if (link.textContent.trim() === 'current') {
          link.textContent = `${currentVersion} (Current)`;
        }
      });
      
      // Also target version switcher dropdown
      const versionSwitcher = document.querySelectorAll('.menu__link--sublist-caret');
      versionSwitcher.forEach(link => {
        if (link.textContent.trim() === 'current' || link.textContent.includes('current')) {
          link.textContent = `${currentVersion} (Current)`;
        }
      });
    };

    // Run immediately and after a short delay
    replaceVersionText();
    setTimeout(replaceVersionText, 500);
    
    // Run after navigation changes
    const observer = new MutationObserver(() => {
      setTimeout(replaceVersionText, 100);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    return () => observer.disconnect();
  }, []);

  return <Layout {...props} />;
}