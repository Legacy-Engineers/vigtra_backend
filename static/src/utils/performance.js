/**
 * Performance utility functions
 */

/**
 * Debounce function to limit the rate of function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @param {boolean} immediate - Whether to execute immediately
 * @returns {Function} Debounced function
 */
export function debounce(func, wait, immediate = false) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(this, args);
  };
}

/**
 * Throttle function to limit the rate of function execution
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Lazy load images when they enter the viewport
 * @param {string} selector - CSS selector for images to lazy load
 */
export function lazyLoadImages(selector = 'img[data-src]') {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      });
    });

    document.querySelectorAll(selector).forEach(img => {
      imageObserver.observe(img);
    });
  } else {
    // Fallback for browsers without IntersectionObserver
    document.querySelectorAll(selector).forEach(img => {
      img.src = img.dataset.src;
      img.classList.remove('lazy');
    });
  }
}

/**
 * Preload critical resources
 * @param {Array} resources - Array of resource objects {href, as, type}
 */
export function preloadResources(resources) {
  resources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = resource.href;
    link.as = resource.as;
    if (resource.type) link.type = resource.type;
    document.head.appendChild(link);
  });
}

/**
 * Measure and log performance metrics
 */
export function measurePerformance() {
  if (!window.performance) return;

  // Core Web Vitals
  const observer = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
      switch (entry.entryType) {
        case 'largest-contentful-paint':
          console.log('LCP:', entry.startTime);
          break;
        case 'first-input':
          console.log('FID:', entry.processingStart - entry.startTime);
          break;
        case 'layout-shift':
          if (!entry.hadRecentInput) {
            console.log('CLS:', entry.value);
          }
          break;
      }
    });
  });

  // Observe different entry types
  ['largest-contentful-paint', 'first-input', 'layout-shift'].forEach(type => {
    try {
      observer.observe({ entryTypes: [type] });
    } catch (e) {
      // Some browsers may not support all entry types
    }
  });
}

/**
 * Optimize animations using requestAnimationFrame
 * @param {Function} callback - Animation callback
 */
export function optimizedAnimation(callback) {
  let rafId;
  let isRunning = false;

  const animate = () => {
    if (!isRunning) return;
    callback();
    rafId = requestAnimationFrame(animate);
  };

  return {
    start() {
      if (!isRunning) {
        isRunning = true;
        rafId = requestAnimationFrame(animate);
      }
    },
    stop() {
      isRunning = false;
      if (rafId) {
        cancelAnimationFrame(rafId);
      }
    }
  };
}

/**
 * Memory usage monitoring
 */
export function monitorMemoryUsage() {
  if ('memory' in performance) {
    const memory = performance.memory;
    console.log('Memory Usage:', {
      used: `${Math.round(memory.usedJSHeapSize / 1048576)} MB`,
      total: `${Math.round(memory.totalJSHeapSize / 1048576)} MB`,
      limit: `${Math.round(memory.jsHeapSizeLimit / 1048576)} MB`
    });
  }
}

/**
 * Bundle size analyzer - logs loaded script sizes
 */
export function analyzeBundleSize() {
  if (!window.performance) return;

  const resources = performance.getEntriesByType('resource');
  const scripts = resources.filter(resource => resource.name.endsWith('.js'));
  
  console.log('Script Bundle Sizes:');
  scripts.forEach(script => {
    const sizeKB = Math.round(script.transferSize / 1024);
    console.log(`${script.name}: ${sizeKB} KB`);
  });
}