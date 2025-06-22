import React from 'react';
import { motion } from 'framer-motion';
import RecipeCard from './RecipeCard';
import CookingAnimation from '../common/CookingAnimation';

interface Recipe {
  id: string;
  title: string;
  description?: string;
  image?: string;
  cookTime?: number;
  servings?: number;
  difficulty?: 'Easy' | 'Medium' | 'Hard';
  category?: string;
  isBookmarked?: boolean;
  author?: {
    name: string;
    avatar?: string;
  };
}

interface RecipeGridProps {
  recipes: Recipe[];
  loading?: boolean;
  onBookmark?: (recipeId: string) => void;
  className?: string;
  emptyMessage?: string;
}

const RecipeGrid: React.FC<RecipeGridProps> = ({
  recipes,
  loading = false,
  onBookmark,
  className = '',
  emptyMessage = 'No recipes found'
}) => {
  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const containerVariants = {
    hidden: {
      opacity: 0
    },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.3,
        staggerChildren: prefersReducedMotion ? 0 : 0.1,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: {
      opacity: 0,
      y: prefersReducedMotion ? 0 : 20,
      scale: prefersReducedMotion ? 1 : 0.9
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  if (loading) {
    return (
      <div className={`min-h-64 flex flex-col items-center justify-center ${className}`}>
        <CookingAnimation size={80} />
        <motion.p 
          className="text-gray-600 mt-4 text-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          Loading delicious recipes...
        </motion.p>
      </div>
    );
  }

  if (recipes.length === 0) {
    return (
      <motion.div 
        className={`min-h-64 flex flex-col items-center justify-center text-center ${className}`}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
      >
        <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center mb-4">
          <motion.div
            animate={{ 
              rotate: prefersReducedMotion ? 0 : 360,
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              rotate: { duration: 2, repeat: Infinity, ease: "linear" },
              scale: { duration: 1, repeat: Infinity, ease: "easeInOut" }
            }}
          >
            🍽️
          </motion.div>
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No recipes yet</h3>
        <p className="text-gray-600 max-w-md">{emptyMessage}</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 ${className}`}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {recipes.map((recipe, index) => (
        <motion.div
          key={recipe.id}
          variants={itemVariants}
          custom={index}
          layout
        >
          <RecipeCard
            recipe={recipe}
            onBookmark={onBookmark}
            className="h-full"
          />
        </motion.div>
      ))}
    </motion.div>
  );
};

export default RecipeGrid;