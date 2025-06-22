import React from 'react';
import Lottie from 'lottie-react';
import cookingAnimation from '../../assets/lottie/cooking.json';

interface CookingAnimationProps {
  size?: number;
  className?: string;
  loop?: boolean;
  autoplay?: boolean;
}

const CookingAnimation: React.FC<CookingAnimationProps> = ({
  size = 100,
  className = '',
  loop = true,
  autoplay = true
}) => {
  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const lottieProps = {
    animationData: cookingAnimation,
    loop: prefersReducedMotion ? false : loop,
    autoplay: prefersReducedMotion ? false : autoplay,
    style: {
      width: size,
      height: size,
    },
    className: `cooking-animation ${className}`,
    'aria-label': 'Cooking animation - loading content',
    role: 'img'
  };

  return (
    <div className="flex items-center justify-center">
      {prefersReducedMotion ? (
        <div 
          className={`flex items-center justify-center ${className}`}
          style={{ width: size, height: size }}
          aria-label="Loading content"
        >
          <div className="w-8 h-8 border-2 border-primary-500 rounded-full animate-pulse" />
        </div>
      ) : (
        <Lottie {...lottieProps} />
      )}
    </div>
  );
};

export default CookingAnimation;