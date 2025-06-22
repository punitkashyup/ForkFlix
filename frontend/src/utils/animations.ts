import { Variants } from 'framer-motion';

// Check for reduced motion preference
const prefersReducedMotion = () => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

// Animation configuration
export const animationConfig = {
  duration: {
    fast: 0.2,
    normal: 0.3,
    slow: 0.5
  },
  easing: {
    easeOut: [0.16, 1, 0.3, 1],
    easeIn: [0.7, 0, 0.84, 0],
    easeInOut: [0.76, 0, 0.24, 1]
  },
  spring: {
    gentle: { type: "spring", damping: 20, stiffness: 300 },
    bouncy: { type: "spring", damping: 15, stiffness: 400 },
    stiff: { type: "spring", damping: 25, stiffness: 500 }
  }
};

// Page transition variants
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    x: prefersReducedMotion() ? 0 : -20,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  },
  in: {
    opacity: 1,
    x: 0,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  },
  out: {
    opacity: 0,
    x: prefersReducedMotion() ? 0 : 20,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  }
};

// Fade animation variants
export const fadeVariants: Variants = {
  hidden: {
    opacity: 0,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  visible: {
    opacity: 1,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  exit: {
    opacity: 0,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  }
};

// Slide up animation variants
export const slideUpVariants: Variants = {
  hidden: {
    opacity: 0,
    y: prefersReducedMotion() ? 0 : 20,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  },
  exit: {
    opacity: 0,
    y: prefersReducedMotion() ? 0 : -20,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  }
};

// Scale animation variants
export const scaleVariants: Variants = {
  hidden: {
    opacity: 0,
    scale: prefersReducedMotion() ? 1 : 0.8,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  },
  exit: {
    opacity: 0,
    scale: prefersReducedMotion() ? 1 : 0.8,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  }
};

// Stagger container variants
export const staggerContainer: Variants = {
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1,
    transition: {
      duration: animationConfig.duration.fast,
      staggerChildren: prefersReducedMotion() ? 0 : 0.1,
      delayChildren: 0.1
    }
  }
};

// Stagger item variants
export const staggerItem: Variants = {
  hidden: {
    opacity: 0,
    y: prefersReducedMotion() ? 0 : 10,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  }
};

// Hover interaction variants
export const hoverVariants: Variants = {
  rest: {
    scale: 1,
    y: 0,
    transition: { 
      duration: animationConfig.duration.fast,
      ease: animationConfig.easing.easeOut 
    }
  },
  hover: {
    scale: prefersReducedMotion() ? 1 : 1.02,
    y: prefersReducedMotion() ? 0 : -2,
    transition: { 
      duration: animationConfig.duration.fast,
      ease: animationConfig.easing.easeOut 
    }
  },
  tap: {
    scale: prefersReducedMotion() ? 1 : 0.98,
    transition: { 
      duration: 0.1,
      ease: animationConfig.easing.easeOut 
    }
  }
};

// Button interaction variants
export const buttonVariants: Variants = {
  rest: {
    scale: 1,
    transition: animationConfig.spring.gentle
  },
  hover: {
    scale: prefersReducedMotion() ? 1 : 1.05,
    transition: animationConfig.spring.gentle
  },
  tap: {
    scale: prefersReducedMotion() ? 1 : 0.95,
    transition: animationConfig.spring.gentle
  }
};

// Card hover variants
export const cardHoverVariants: Variants = {
  rest: {
    scale: 1,
    y: 0,
    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    transition: { 
      duration: animationConfig.duration.fast,
      ease: animationConfig.easing.easeOut 
    }
  },
  hover: {
    scale: prefersReducedMotion() ? 1 : 1.02,
    y: prefersReducedMotion() ? 0 : -4,
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    transition: { 
      duration: animationConfig.duration.fast,
      ease: animationConfig.easing.easeOut 
    }
  },
  tap: {
    scale: prefersReducedMotion() ? 1 : 0.98,
    transition: { 
      duration: 0.1,
      ease: animationConfig.easing.easeOut 
    }
  }
};

// Loading spinner variants
export const spinnerVariants: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: "linear"
    }
  }
};

// Toast notification variants
export const toastVariants: Variants = {
  hidden: {
    opacity: 0,
    scale: prefersReducedMotion() ? 1 : 0.8,
    x: prefersReducedMotion() ? 0 : 100,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  },
  visible: {
    opacity: 1,
    scale: 1,
    x: 0,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  },
  exit: {
    opacity: 0,
    scale: prefersReducedMotion() ? 1 : 0.8,
    x: prefersReducedMotion() ? 0 : 100,
    transition: { 
      duration: animationConfig.duration.fast,
      ease: animationConfig.easing.easeIn 
    }
  }
};

// Modal variants
export const modalVariants: Variants = {
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  exit: {
    opacity: 0,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  }
};

export const modalContentVariants: Variants = {
  hidden: {
    opacity: 0,
    scale: prefersReducedMotion() ? 1 : 0.8,
    y: prefersReducedMotion() ? 0 : 20,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  },
  exit: {
    opacity: 0,
    scale: prefersReducedMotion() ? 1 : 0.8,
    y: prefersReducedMotion() ? 0 : 20,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  }
};

// Input focus variants
export const inputFocusVariants: Variants = {
  rest: {
    scale: 1,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  },
  focus: {
    scale: prefersReducedMotion() ? 1 : 1.02,
    transition: { 
      duration: animationConfig.duration.fast 
    }
  }
};

// List item reveal variants (for search results, etc.)
export const listItemVariants: Variants = {
  hidden: {
    opacity: 0,
    x: prefersReducedMotion() ? 0 : -10,
    transition: { 
      duration: animationConfig.duration.normal 
    }
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: { 
      duration: animationConfig.duration.normal,
      ease: animationConfig.easing.easeOut 
    }
  }
};

// Error shake animation
export const shakeVariants: Variants = {
  shake: {
    x: prefersReducedMotion() ? 0 : [-5, 5, -5, 5, 0],
    transition: { 
      duration: 0.5 
    }
  }
};

// Pulse animation for loading states
export const pulseVariants: Variants = {
  pulse: {
    scale: prefersReducedMotion() ? 1 : [1, 1.05, 1],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut"
    }
  }
};

// Helper function to create custom variants
export const createCustomVariants = (
  hiddenProps: Record<string, any> = {},
  visibleProps: Record<string, any> = {},
  exitProps: Record<string, any> = {}
): Variants => {
  return {
    hidden: {
      ...hiddenProps,
      transition: { 
        duration: animationConfig.duration.normal,
        ...hiddenProps.transition 
      }
    },
    visible: {
      ...visibleProps,
      transition: { 
        duration: animationConfig.duration.normal,
        ease: animationConfig.easing.easeOut,
        ...visibleProps.transition 
      }
    },
    exit: {
      ...exitProps,
      transition: { 
        duration: animationConfig.duration.fast,
        ...exitProps.transition 
      }
    }
  };
};

export default {
  pageVariants,
  fadeVariants,
  slideUpVariants,
  scaleVariants,
  staggerContainer,
  staggerItem,
  hoverVariants,
  buttonVariants,
  cardHoverVariants,
  spinnerVariants,
  toastVariants,
  modalVariants,
  modalContentVariants,
  inputFocusVariants,
  listItemVariants,
  shakeVariants,
  pulseVariants,
  createCustomVariants,
  animationConfig
};