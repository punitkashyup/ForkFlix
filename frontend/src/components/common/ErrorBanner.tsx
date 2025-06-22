import React, { useState, useEffect } from 'react';

/**
 * Banner variant types
 */
export type BannerVariant = 'error' | 'warning' | 'info' | 'success';

/**
 * Props for the ErrorBanner component
 */
export interface ErrorBannerProps {
  /** Banner variant style */
  variant?: BannerVariant;
  /** Banner message */
  message: string;
  /** Banner title */
  title?: string;
  /** Whether the banner is dismissible */
  dismissible?: boolean;
  /** Auto-dismiss timer in milliseconds */
  autoDissmiss?: number;
  /** Callback when banner is dismissed */
  onDismiss?: () => void;
  /** Callback when banner is closed (alias for onDismiss) */
  onClose?: () => void;
  /** Show icon indicator */
  showIcon?: boolean;
  /** Custom icon */
  customIcon?: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Whether the banner is visible */
  visible?: boolean;
}

/**
 * ErrorBanner component with multiple variants, dismissible functionality, and animations
 */
const ErrorBanner: React.FC<ErrorBannerProps> = ({
  variant = 'error',
  message,
  title,
  dismissible = true,
  autoDissmiss,
  onDismiss,
  onClose,
  showIcon = true,
  customIcon,
  className = '',
  visible = true,
}) => {
  const [isVisible, setIsVisible] = useState(visible);
  const [isAnimating, setIsAnimating] = useState(false);

  // Auto-dismiss functionality
  useEffect(() => {
    if (autoDissmiss && autoDissmiss > 0) {
      const timer = setTimeout(() => {
        handleDismiss();
      }, autoDissmiss);

      return () => clearTimeout(timer);
    }
  }, [autoDissmiss]);

  // Update visibility when prop changes
  useEffect(() => {
    setIsVisible(visible);
  }, [visible]);

  // Handle dismiss with animation
  const handleDismiss = () => {
    setIsAnimating(true);
    setTimeout(() => {
      setIsVisible(false);
      setIsAnimating(false);
      onDismiss?.();
      onClose?.();
    }, 300);
  };

  // Variant styles
  const variantStyles = {
    error: {
      container: 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800',
      text: 'text-red-800 dark:text-red-200',
      title: 'text-red-900 dark:text-red-100',
      icon: 'text-red-400 dark:text-red-300',
      button: 'text-red-400 hover:text-red-600 dark:text-red-300 dark:hover:text-red-100',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800',
      text: 'text-yellow-800 dark:text-yellow-200',
      title: 'text-yellow-900 dark:text-yellow-100',
      icon: 'text-yellow-400 dark:text-yellow-300',
      button: 'text-yellow-400 hover:text-yellow-600 dark:text-yellow-300 dark:hover:text-yellow-100',
    },
    info: {
      container: 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800',
      text: 'text-blue-800 dark:text-blue-200',
      title: 'text-blue-900 dark:text-blue-100',
      icon: 'text-blue-400 dark:text-blue-300',
      button: 'text-blue-400 hover:text-blue-600 dark:text-blue-300 dark:hover:text-blue-100',
    },
    success: {
      container: 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800',
      text: 'text-green-800 dark:text-green-200',
      title: 'text-green-900 dark:text-green-100',
      icon: 'text-green-400 dark:text-green-300',
      button: 'text-green-400 hover:text-green-600 dark:text-green-300 dark:hover:text-green-100',
    },
  };

  // Default icons for each variant
  const defaultIcons = {
    error: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
          clipRule="evenodd"
        />
      </svg>
    ),
    warning: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
    ),
    info: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
          clipRule="evenodd"
        />
      </svg>
    ),
    success: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
          clipRule="evenodd"
        />
      </svg>
    ),
  };

  // Don't render if not visible
  if (!isVisible) return null;

  const styles = variantStyles[variant];
  const icon = customIcon || defaultIcons[variant];

  return (
    <div
      className={`
        border rounded-lg p-4 transition-all duration-300 ease-in-out
        ${styles.container}
        ${isAnimating ? 'opacity-0 -translate-y-2 transform' : 'opacity-100 translate-y-0 transform animate-slide-up'}
        ${className}
      `}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start">
        {/* Icon */}
        {showIcon && (
          <div className={`flex-shrink-0 ${styles.icon} mr-3`} aria-hidden="true">
            {icon}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {title && (
            <h3 className={`text-sm font-medium ${styles.title} mb-1`}>
              {title}
            </h3>
          )}
          <p className={`text-sm ${styles.text} leading-5`}>
            {message}
          </p>
        </div>

        {/* Dismiss button */}
        {dismissible && (
          <div className="flex-shrink-0 ml-4">
            <button
              onClick={handleDismiss}
              className={`
                inline-flex rounded-md p-1.5 transition-colors duration-200
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent
                ${styles.button}
              `}
              aria-label="Dismiss notification"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorBanner;