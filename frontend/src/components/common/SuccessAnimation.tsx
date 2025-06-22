import React from 'react';
import Lottie from 'lottie-react';
import successAnimation from '../../assets/lottie/success.json';

interface SuccessAnimationProps {
  size?: number;
  className?: string;
  onComplete?: () => void;
  autoplay?: boolean;
}

const SuccessAnimation: React.FC<SuccessAnimationProps> = ({
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
    animationData: successAnimation,
    loop: false,
    autoplay: prefersReducedMotion ? false : autoplay,
    onComplete: handleComplete,
    style: {
      width: size,
      height: size,
    },
    className: `success-animation ${className}`,
    'aria-label': 'Success animation - action completed successfully',
    role: 'img'
  };

  return (
    <div className="flex items-center justify-center">
      {prefersReducedMotion ? (
        <div 
          className={`flex items-center justify-center text-success ${className}`}
          style={{ width: size, height: size }}
          aria-label="Action completed successfully"
        >
          <svg 
            className="w-8 h-8" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path 
              fillRule="evenodd" 
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
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

export default SuccessAnimation;