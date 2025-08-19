/**
 * Main application JavaScript
 * This file contains core functionality for the Vigtra application
 */

// Import polyfills for older browsers
import 'core-js/stable';

// Import styles
import '../css/main.css';

// Utility functions
import { debounce, throttle } from '@utils/performance';
import { initializeComponents } from '@components/index';

// Application initialization
class VigraApp {
  constructor() {
    this.initialized = false;
    this.components = new Map();
  }

  async init() {
    if (this.initialized) return;

    try {
      // Initialize performance monitoring
      this.initPerformanceMonitoring();

      // Initialize components
      await initializeComponents();

      // Set up event listeners
      this.setupEventListeners();

      // Mark as initialized
      this.initialized = true;

      console.log('Vigtra application initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Vigtra application:', error);
    }
  }

  initPerformanceMonitoring() {
    // Monitor page load performance
    if ('performance' in window && 'getEntriesByType' in window.performance) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const navigation = performance.getEntriesByType('navigation')[0];
          const paintEntries = performance.getEntriesByType('paint');
          
          console.log('Performance Metrics:', {
            domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
            loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
            firstPaint: paintEntries.find(entry => entry.name === 'first-paint')?.startTime,
            firstContentfulPaint: paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime
          });
        }, 0);
      });
    }
  }

  setupEventListeners() {
    // Debounced scroll handler
    const handleScroll = debounce(() => {
      this.updateScrollPosition();
    }, 16); // 60fps

    // Throttled resize handler
    const handleResize = throttle(() => {
      this.updateViewport();
    }, 250);

    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('resize', handleResize);

    // Form optimization
    this.optimizeForms();
  }

  updateScrollPosition() {
    // Update scroll-dependent UI elements
    document.body.style.setProperty('--scroll-y', `${window.scrollY}px`);
  }

  updateViewport() {
    // Update viewport-dependent UI elements
    document.body.style.setProperty('--viewport-width', `${window.innerWidth}px`);
    document.body.style.setProperty('--viewport-height', `${window.innerHeight}px`);
  }

  optimizeForms() {
    // Add performance optimizations to forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
      // Debounce form validation
      const inputs = form.querySelectorAll('input, textarea, select');
      
      inputs.forEach(input => {
        const validateInput = debounce(() => {
          // Trigger validation
          if (input.checkValidity) {
            input.checkValidity();
          }
        }, 300);

        input.addEventListener('input', validateInput);
      });
    });
  }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const app = new VigraApp();
    app.init();
  });
} else {
  const app = new VigraApp();
  app.init();
}