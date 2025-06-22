import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Clock, Users, Heart, BookOpen } from 'lucide-react';

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

interface RecipeCardProps {
  recipe: Recipe;
  onBookmark?: (recipeId: string) => void;
  className?: string;
}

const RecipeCard: React.FC<RecipeCardProps> = ({ 
  recipe, 
  onBookmark, 
  className = '' 
}) => {
  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const handleBookmark = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (onBookmark) {
      onBookmark(recipe.id);
    }
  };

  const cardVariants = {
    rest: {
      scale: 1,
      y: 0,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    },
    hover: {
      scale: prefersReducedMotion ? 1 : 1.02,
      y: prefersReducedMotion ? 0 : -4,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    },
    tap: {
      scale: prefersReducedMotion ? 1 : 0.98,
      transition: {
        duration: 0.1,
        ease: "easeOut"
      }
    }
  };

  const imageVariants = {
    rest: {
      scale: 1,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    },
    hover: {
      scale: prefersReducedMotion ? 1 : 1.05,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  const bookmarkVariants = {
    rest: {
      scale: 1,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    },
    hover: {
      scale: prefersReducedMotion ? 1 : 1.1,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    },
    tap: {
      scale: prefersReducedMotion ? 1 : 0.9,
      transition: {
        duration: 0.1,
        ease: "easeOut"
      }
    }
  };

  return (
    <motion.div
      className={`bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden ${className}`}
      variants={cardVariants}
      initial="rest"
      whileHover="hover"
      whileTap="tap"
    >
      <Link to={`/recipe/${recipe.id}`} className="block">
        {/* Image Container */}
        <div className="relative h-48 overflow-hidden bg-gray-200">
          <motion.div
            variants={imageVariants}
            className="w-full h-full"
          >
            {recipe.image ? (
              <img
                src={recipe.image}
                alt={recipe.title}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
                <BookOpen className="w-12 h-12 text-primary-400" />
              </div>
            )}
          </motion.div>
          
          {/* Bookmark Button */}
          <motion.button
            onClick={handleBookmark}
            className={`absolute top-3 right-3 p-2 rounded-full backdrop-blur-sm transition-colors duration-200 ${
              recipe.isBookmarked 
                ? 'bg-red-500 text-white' 
                : 'bg-white/80 text-gray-600 hover:bg-white hover:text-red-500'
            }`}
            variants={bookmarkVariants}
            whileHover="hover"
            whileTap="tap"
            aria-label={recipe.isBookmarked ? 'Remove from bookmarks' : 'Add to bookmarks'}
          >
            <Heart 
              className="w-4 h-4" 
              fill={recipe.isBookmarked ? 'currentColor' : 'none'}
            />
          </motion.button>

          {/* Category Badge */}
          {recipe.category && (
            <motion.div
              className="absolute top-3 left-3 px-2 py-1 bg-primary-500 text-white text-xs rounded-full font-medium"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              {recipe.category}
            </motion.div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          {/* Title */}
          <motion.h3 
            className="font-display font-semibold text-lg text-gray-900 mb-2 line-clamp-2"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            {recipe.title}
          </motion.h3>

          {/* Description */}
          {recipe.description && (
            <motion.p 
              className="text-gray-600 text-sm mb-3 line-clamp-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.3 }}
            >
              {recipe.description}
            </motion.p>
          )}

          {/* Meta Information */}
          <motion.div 
            className="flex items-center justify-between text-sm text-gray-500"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.4 }}
          >
            <div className="flex items-center space-x-4">
              {recipe.cookTime && (
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  <span>{recipe.cookTime}m</span>
                </div>
              )}
              {recipe.servings && (
                <div className="flex items-center">
                  <Users className="w-4 h-4 mr-1" />
                  <span>{recipe.servings}</span>
                </div>
              )}
            </div>
            
            {recipe.difficulty && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                recipe.difficulty === 'Easy' 
                  ? 'bg-green-100 text-green-800'
                  : recipe.difficulty === 'Medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {recipe.difficulty}
              </span>
            )}
          </motion.div>

          {/* Author */}
          {recipe.author && (
            <motion.div 
              className="flex items-center mt-3 pt-3 border-t border-gray-100"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.5 }}
            >
              {recipe.author.avatar ? (
                <img
                  src={recipe.author.avatar}
                  alt={recipe.author.name}
                  className="w-6 h-6 rounded-full mr-2"
                />
              ) : (
                <div className="w-6 h-6 bg-primary-200 rounded-full mr-2 flex items-center justify-center">
                  <span className="text-xs font-medium text-primary-700">
                    {recipe.author.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              <span className="text-sm text-gray-600">{recipe.author.name}</span>
            </motion.div>
          )}
        </div>
      </Link>
    </motion.div>
  );
};

export default RecipeCard;