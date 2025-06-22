import React from 'react';
import Lottie from 'lottie-react';
import errorAnimation from '../../assets/lottie/error.json';

interface ErrorAnimationProps {
  size?: number;
  className?: string;
  onComplete?: () => void;
  autoplay?: boolean;
}

const ErrorAnimation: React.FC<ErrorAnimationProps> = ({
  size = 80,
  className = '',
  onComplete,
  autoplay = true
}) => {
  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const handleComplete = () => {
    if (onComplete) {
      onComplete();
    }
  };

  const lottieProps = {
    animationData: errorAnimation,
    loop: false,
    autoplay: prefersReducedMotion ? false : autoplay,
    onComplete: handleComplete,
    style: {
      width: size,
      height: size,
    },
    className: `error-animation ${className}`,
    'aria-label': 'Error animation - an error occurred',
    role: 'img'
  };

  return (
    <div className="flex items-center justify-center">
      {prefersReducedMotion ? (
        <div 
          className={`flex items-center justify-center text-error ${className}`}
          style={{ width: size, height: size }}
          aria-label="An error occurred"
        >
          <svg 
            className="w-8 h-8" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path 
              fillRule="evenodd" 
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
              clipRule="evenodd" 
            />
          </svg>
        </div>
      ) : (
        <Lottie {...lottieProps} />
      )}
    </div>
  );
};

export default ErrorAnimation;