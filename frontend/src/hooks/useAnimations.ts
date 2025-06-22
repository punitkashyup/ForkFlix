import { useEffect, useState } from 'react';

export interface AnimationConfig {
  duration: number;
  easing: string;
  reducedMotion: boolean;
  enabled: boolean;
}

/**
 * Hook to manage animation preferences and settings
 * Respects user's reduced motion preferences and app settings
 */
export const useAnimations = (): AnimationConfig => {
  const [reducedMotion, setReducedMotion] = useState<boolean>(false);

  useEffect(() => {
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);

    // Listen for changes to the media query
    const handleChange = (event: MediaQueryListEvent) => {
      setReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Get animation settings from environment variables
  const enabled = process.env.REACT_APP_ENABLE_ANIMATIONS !== 'false';
  const duration = parseInt(process.env.REACT_APP_ANIMATION_DURATION || '300', 10);
  const respectReducedMotion = process.env.REACT_APP_REDUCED_MOTION_RESPECT !== 'false';

  return {
    duration: reducedMotion && respectReducedMotion ? 0 : duration,
    easing: 'easeOut',
    reducedMotion: reducedMotion && respectReducedMotion,
    enabled: enabled && (!reducedMotion || !respectReducedMotion)
  };
};

/**
 * Hook to get animation variants based on user preferences
 */
export const useAnimationVariants = () => {
  const { reducedMotion, duration } = useAnimations();

  const fadeIn = {
    hidden: {
      opacity: 0,
      transition: { duration: duration / 1000 }
    },
    visible: {
      opacity: 1,
      transition: { duration: duration / 1000 }
    }
  };

  const slideUp = {
    hidden: {
      opacity: 0,
      y: reducedMotion ? 0 : 20,
      transition: { duration: duration / 1000 }
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: duration / 1000 }
    }
  };

  const slideLeft = {
    hidden: {
      opacity: 0,
      x: reducedMotion ? 0 : 20,
      transition: { duration: duration / 1000 }
    },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: duration / 1000 }
    }
  };

  const scale = {
    hidden: {
      opacity: 0,
      scale: reducedMotion ? 1 : 0.8,
      transition: { duration: duration / 1000 }
    },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: duration / 1000 }
    }
  };

  const staggerContainer = {
    hidden: {
      opacity: 0
    },
    visible: {
      opacity: 1,
      transition: {
        duration: duration / 1000,
        staggerChildren: reducedMotion ? 0 : 0.1,
        delayChildren: 0.1
      }
    }
  };

  const staggerItem = {
    hidden: {
      opacity: 0,
      y: reducedMotion ? 0 : 10,
      transition: { duration: duration / 1000 }
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: duration / 1000 }
    }
  };

  const hover = {
    rest: {
      scale: 1,
      transition: { duration: 0.2, ease: "easeOut" }
    },
    hover: {
      scale: reducedMotion ? 1 : 1.02,
      transition: { duration: 0.2, ease: "easeOut" }
    },
    tap: {
      scale: reducedMotion ? 1 : 0.98,
      transition: { duration: 0.1, ease: "easeOut" }
    }
  };

  return {
    fadeIn,
    slideUp,
    slideLeft,
    scale,
    staggerContainer,
    staggerItem,
    hover
  };
};

/**
 * Hook to get spring animation configuration
 */
export const useSpringConfig = () => {
  const { reducedMotion } = useAnimations();

  if (reducedMotion) {
    return {
      type: "tween",
      duration: 0
    };
  }

  return {
    type: "spring",
    damping: 20,
    stiffness: 300
  };
};

export default useAnimations;