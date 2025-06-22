import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import Button from '../components/common/Button';
import ErrorBanner from '../components/common/ErrorBanner';
import Loading from '../components/common/Loading';
import { VALIDATION } from '../config/constants';

/**
 * Signup form data interface
 */
interface SignupFormData {
  displayName: string;
  email: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}

/**
 * Signup page component with form validation and Firebase auth integration
 */
const Signup: React.FC = () => {
  const { signup, user, loading, error, clearError } = useApp();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setError,
  } = useForm<SignupFormData>({
    defaultValues: {
      displayName: '',
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false,
    },
  });

  // Watch password for confirmation validation
  const watchPassword = watch('password');

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate('/', { replace: true });
    }
  }, [user, navigate]);

  // Set page title
  useEffect(() => {
    document.title = 'Sign Up - Recipe Reel Manager';
  }, []);

  // Handle form submission
  const onSubmit = async (data: SignupFormData) => {
    try {
      clearError();
      await signup(data.email, data.password, data.displayName);
    } catch (error: any) {
      // Handle specific Firebase auth errors
      let errorMessage = 'Failed to create account. Please try again.';
      
      if (error?.code) {
        switch (error.code) {
          case 'auth/email-already-in-use':
            errorMessage = 'An account with this email already exists.';
            setError('email', { type: 'manual', message: errorMessage });
            break;
          case 'auth/invalid-email':
            errorMessage = 'Invalid email address format.';
            setError('email', { type: 'manual', message: errorMessage });
            break;
          case 'auth/weak-password':
            errorMessage = 'Password is too weak. Please choose a stronger password.';
            setError('password', { type: 'manual', message: errorMessage });
            break;
          case 'auth/operation-not-allowed':
            errorMessage = 'Email/password accounts are not enabled. Please contact support.';
            break;
          default:
            break;
        }
      }
    }
  };

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Toggle confirm password visibility
  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  // Show loading spinner during auth state check
  if (loading.isLoading && !isSubmitting) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Loading size="large" message="Setting up your account..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-gradient-to-r from-primary-500 to-secondary-500">
            <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Join Recipe Reel Manager and start organizing your favorite recipes
          </p>
        </div>

        {/* Error Banner */}
        {error.hasError && (
          <ErrorBanner
            variant="error"
            message={error.message || 'An error occurred during registration'}
            dismissible
            onDismiss={clearError}
            className="mb-6"
          />
        )}

        {/* Signup Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            {/* Display Name Field */}
            <div>
              <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Full Name
              </label>
              <div className="relative">
                <input
                  {...register('displayName', {
                    required: 'Full name is required',
                    minLength: {
                      value: 2,
                      message: 'Name must be at least 2 characters',
                    },
                    maxLength: {
                      value: 50,
                      message: 'Name cannot exceed 50 characters',
                    },
                    pattern: {
                      value: /^[a-zA-Z\s]+$/,
                      message: 'Name can only contain letters and spaces',
                    },
                  })}
                  type="text"
                  autoComplete="name"
                  className={`
                    appearance-none relative block w-full px-3 py-2 border rounded-lg
                    placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-800
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                    dark:border-gray-600 dark:placeholder-gray-400
                    ${errors.displayName 
                      ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500' 
                      : 'border-gray-300'
                    }
                  `}
                  placeholder="Enter your full name"
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
              {errors.displayName && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.displayName.message}</p>
              )}
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email address
              </label>
              <div className="relative">
                <input
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address format',
                    },
                  })}
                  type="email"
                  autoComplete="email"
                  className={`
                    appearance-none relative block w-full px-3 py-2 border rounded-lg
                    placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-800
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                    dark:border-gray-600 dark:placeholder-gray-400
                    ${errors.email 
                      ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500' 
                      : 'border-gray-300'
                    }
                  `}
                  placeholder="Enter your email"
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                </div>
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password
              </label>
              <div className="relative">
                <input
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: VALIDATION.MIN_PASSWORD_LENGTH,
                      message: `Password must be at least ${VALIDATION.MIN_PASSWORD_LENGTH} characters`,
                    },
                    pattern: {
                      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).*$/,
                      message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number',
                    },
                  })}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  className={`
                    appearance-none relative block w-full px-3 py-2 pr-10 border rounded-lg
                    placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-800
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                    dark:border-gray-600 dark:placeholder-gray-400
                    ${errors.password 
                      ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500' 
                      : 'border-gray-300'
                    }
                  `}
                  placeholder="Create a secure password"
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L12 12m-2.122-2.122L7.76 7.76m0 0L5.636 5.636m0 0L12 12m0 0l7.071-7.071M12 12l-7.071 7.071" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.password.message}</p>
              )}
              <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Password must contain at least 6 characters with uppercase, lowercase, and number
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  {...register('confirmPassword', {
                    required: 'Please confirm your password',
                    validate: (value) => 
                      value === watchPassword || 'Passwords do not match',
                  })}
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  className={`
                    appearance-none relative block w-full px-3 py-2 pr-10 border rounded-lg
                    placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-800
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                    dark:border-gray-600 dark:placeholder-gray-400
                    ${errors.confirmPassword 
                      ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500' 
                      : 'border-gray-300'
                    }
                  `}
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  onClick={toggleConfirmPasswordVisibility}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showConfirmPassword ? (
                    <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L12 12m-2.122-2.122L7.76 7.76m0 0L5.636 5.636m0 0L12 12m0 0l7.071-7.071M12 12l-7.071 7.071" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.confirmPassword.message}</p>
              )}
            </div>
          </div>

          {/* Terms of Service */}
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                {...register('acceptTerms', {
                  required: 'You must accept the terms of service to continue',
                })}
                type="checkbox"
                className={`
                  h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded
                  dark:border-gray-600 dark:bg-gray-800
                  ${errors.acceptTerms ? 'border-red-300 dark:border-red-600' : ''}
                `}
              />
            </div>
            <div className="ml-3 text-sm">
              <label htmlFor="acceptTerms" className="text-gray-700 dark:text-gray-300">
                I agree to the{' '}
                <Link
                  to="/terms"
                  className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Terms of Service
                </Link>
                {' '}and{' '}
                <Link
                  to="/privacy"
                  className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </Link>
              </label>
            </div>
          </div>
          {errors.acceptTerms && (
            <p className="text-sm text-red-600 dark:text-red-400">{errors.acceptTerms.message}</p>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            loading={isSubmitting}
            loadingText="Creating account..."
            disabled={isSubmitting}
          >
            Create Account
          </Button>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Signup;