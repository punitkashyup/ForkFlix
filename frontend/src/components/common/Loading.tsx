import React from 'react';

/**
 * Size options for loading components
 */
export type LoadingSize = 'small' | 'medium' | 'large';

/**
 * Props for the LoadingSpinner component
 */
export interface LoadingSpinnerProps {
  /** Size of the spinner */
  size?: LoadingSize;
  /** Custom color class for the spinner */
  color?: string;
  /** Additional CSS classes */
  className?: string;
  /** Loading message to display */
  message?: string;
}

/**
 * Props for the LoadingDots component
 */
export interface LoadingDotsProps {
  /** Size of the dots */
  size?: LoadingSize;
  /** Custom color class for the dots */
  color?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Props for the main Loading component
 */
export interface LoadingProps {
  /** Type of loading animation */
  type?: 'spinner' | 'dots';
  /** Size of the loading component */
  size?: LoadingSize;
  /** Optional message to display */
  message?: string;
  /** Center the loading component */
  centered?: boolean;
  /** Custom color class */
  color?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * LoadingSpinner component with customizable size and color
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  color = 'text-primary-500',
  className = '',
  message,
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  if (message) {
    return (
      <div className={`flex flex-col items-center space-y-3 ${className}`}>
        <div
          className={`inline-block animate-spin rounded-full border-2 border-current border-t-transparent ${sizeClasses[size]} ${color}`}
          role="status"
          aria-label="Loading"
        >
          <span className="sr-only">Loading...</span>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
      </div>
    );
  }

  return (
    <div
      className={`inline-block animate-spin rounded-full border-2 border-current border-t-transparent ${sizeClasses[size]} ${color} ${className}`}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

/**
 * LoadingDots component with bouncing animation
 */
export const LoadingDots: React.FC<LoadingDotsProps> = ({
  size = 'medium',
  color = 'bg-primary-500',
  className = '',
}) => {
  const sizeClasses = {
    small: 'w-1 h-1',
    medium: 'w-2 h-2',
    large: 'w-3 h-3',
  };

  const gapClasses = {
    small: 'space-x-1',
    medium: 'space-x-1.5',
    large: 'space-x-2',
  };

  return (
    <div
      className={`flex items-center ${gapClasses[size]} ${className}`}
      role="status"
      aria-label="Loading"
    >
      <div
        className={`${sizeClasses[size]} ${color} rounded-full animate-bounce`}
        style={{ animationDelay: '0ms' }}
      />
      <div
        className={`${sizeClasses[size]} ${color} rounded-full animate-bounce`}
        style={{ animationDelay: '150ms' }}
      />
      <div
        className={`${sizeClasses[size]} ${color} rounded-full animate-bounce`}
        style={{ animationDelay: '300ms' }}
      />
      <span className="sr-only">Loading...</span>
    </div>
  );
};

/**
 * Main Loading component that supports both spinner and dots animations
 * with optional message display
 */
const Loading: React.FC<LoadingProps> = ({
  type = 'spinner',
  size = 'medium',
  message,
  centered = false,
  color,
  className = '',
}) => {
  const LoadingComponent = type === 'spinner' ? LoadingSpinner : LoadingDots;
  const componentProps = {
    size,
    color: color || (type === 'spinner' ? 'text-primary-500' : 'bg-primary-500'),
  };

  const containerClasses = `
    ${centered ? 'flex flex-col items-center justify-center' : ''}
    ${className}
  `.trim();

  const messageClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
  };

  return (
    <div className={containerClasses}>
      <LoadingComponent {...componentProps} />
      {message && (
        <p
          className={`mt-3 text-gray-600 dark:text-gray-400 ${messageClasses[size]} text-center`}
          aria-live="polite"
        >
          {message}
        </p>
      )}
    </div>
  );
};

export default Loading;