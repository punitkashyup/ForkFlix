import React, { forwardRef } from 'react';
import { LoadingSpinner } from './Loading';

/**
 * Button variant types
 */
export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';

/**
 * Button size types
 */
export type ButtonSize = 'sm' | 'md' | 'lg';

/**
 * Icon position types
 */
export type IconPosition = 'left' | 'right';

/**
 * Props for the Button component
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant style */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Loading state */
  loading?: boolean;
  /** Loading text to show when loading */
  loadingText?: string;
  /** Icon to display */
  icon?: React.ReactNode;
  /** Left icon (alias for icon with left position) */
  leftIcon?: React.ReactNode;
  /** Right icon */
  rightIcon?: React.ReactNode;
  /** Icon position */
  iconPosition?: IconPosition;
  /** Full width button */
  fullWidth?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Children content */
  children?: React.ReactNode;
}

/**
 * Button component with multiple variants, sizes, loading states, and icon support
 */
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      loadingText,
      icon,
      leftIcon,
      rightIcon,
      iconPosition = 'left',
      fullWidth = false,
      disabled = false,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    // Base styles
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none';

    // Variant styles
    const variantStyles = {
      primary: 'bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white shadow-lg hover:shadow-xl focus:ring-primary-500 dark:focus:ring-offset-gray-900',
      secondary: 'bg-gradient-to-r from-secondary-500 to-secondary-600 hover:from-secondary-600 hover:to-secondary-700 text-white shadow-lg hover:shadow-xl focus:ring-secondary-500 dark:focus:ring-offset-gray-900',
      danger: 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg hover:shadow-xl focus:ring-red-500 dark:focus:ring-offset-gray-900',
      ghost: 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800 dark:focus:ring-offset-gray-900',
      outline: 'border-2 border-primary-500 text-primary-500 hover:bg-primary-500 hover:text-white focus:ring-primary-500 dark:focus:ring-offset-gray-900',
    };

    // Size styles
    const sizeStyles = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2 text-base gap-2',
      lg: 'px-6 py-3 text-lg gap-2.5',
    };

    // Full width styles
    const widthStyles = fullWidth ? 'w-full' : '';

    // Loading spinner size based on button size
    const spinnerSizes = {
      sm: 'small' as const,
      md: 'small' as const,
      lg: 'medium' as const,
    };

    // Combine all styles
    const buttonClasses = `
      ${baseStyles}
      ${variantStyles[variant]}
      ${sizeStyles[size]}
      ${widthStyles}
      ${className}
    `.trim();

    // Determine if button should be disabled
    const isDisabled = disabled || loading;

    // Render loading spinner with appropriate color
    const renderLoadingSpinner = () => {
      const spinnerColor = variant === 'ghost' || variant === 'outline' 
        ? 'text-current' 
        : 'text-white';
      
      return (
        <LoadingSpinner 
          size={spinnerSizes[size]} 
          color={spinnerColor}
        />
      );
    };

    // Determine which icon to show and position
    const getIconAndPosition = () => {
      if (leftIcon) return { icon: leftIcon, position: 'left' };
      if (rightIcon) return { icon: rightIcon, position: 'right' };
      if (icon) return { icon, position: iconPosition };
      return { icon: null, position: 'left' };
    };

    const { icon: displayIcon, position } = getIconAndPosition();

    // Render icon with proper spacing
    const renderIcon = () => {
      if (!displayIcon || loading) return null;
      
      return (
        <span className="flex-shrink-0" aria-hidden="true">
          {displayIcon}
        </span>
      );
    };

    // Render button content
    const renderContent = () => {
      if (loading) {
        return (
          <>
            {renderLoadingSpinner()}
            {loadingText || children}
          </>
        );
      }

      if (position === 'left') {
        return (
          <>
            {renderIcon()}
            {children}
          </>
        );
      }

      return (
        <>
          {children}
          {renderIcon()}
        </>
      );
    };

    return (
      <button
        ref={ref}
        className={buttonClasses}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        {...props}
      >
        {renderContent()}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;