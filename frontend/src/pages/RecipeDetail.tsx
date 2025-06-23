import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import ErrorBanner from '../components/common/ErrorBanner';
import Modal from '../components/common/Modal';
import apiService from '../services/api';
import { RECIPE_CATEGORIES } from '../config/constants';
import type { Recipe } from '../types';

/**
 * Ingredients list component with checkboxes
 */
interface IngredientsListProps {
  ingredients: string[];
  checkedIngredients: Set<number>;
  onToggleIngredient: (index: number) => void;
}

const IngredientsList: React.FC<IngredientsListProps> = ({
  ingredients,
  checkedIngredients,
  onToggleIngredient,
}) => {
  return (
    <div className="space-y-3">
      {ingredients.map((ingredient, index) => (
        <div key={index} className="flex items-center space-x-3">
          <input
            type="checkbox"
            id={`ingredient-${index}`}
            checked={checkedIngredients.has(index)}
            onChange={() => onToggleIngredient(index)}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded dark:border-gray-600 dark:bg-gray-800"
          />
          <label
            htmlFor={`ingredient-${index}`}
            className={`text-sm flex-1 cursor-pointer ${
              checkedIngredients.has(index)
                ? 'line-through text-gray-500 dark:text-gray-400'
                : 'text-gray-900 dark:text-white'
            }`}
          >
            {ingredient}
          </label>
        </div>
      ))}
    </div>
  );
};

/**
 * Instagram embed component
 */
interface InstagramEmbedProps {
  embedCode: string;
  title: string;
}

const InstagramEmbed: React.FC<InstagramEmbedProps> = ({ embedCode, title }) => {
  useEffect(() => {
    // Load Instagram embed script if not already loaded
    if (typeof window !== 'undefined' && !window.instgrm) {
      const script = document.createElement('script');
      script.async = true;
      script.src = '//www.instagram.com/embed.js';
      document.body.appendChild(script);
    } else if (window.instgrm) {
      window.instgrm.Embeds.process();
    }
  }, [embedCode]);

  return (
    <div className="instagram-embed-container">
      <div
        dangerouslySetInnerHTML={{ __html: embedCode }}
        className="flex justify-center"
      />
    </div>
  );
};

/**
 * RecipeDetail page component
 */
const RecipeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, deleteRecipe, error, clearError } = useApp();
  
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkedIngredients, setCheckedIngredients] = useState<Set<number>>(new Set());
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [shareUrl, setShareUrl] = useState('');

  // Set page title
  useEffect(() => {
    if (recipe) {
      document.title = `${recipe.title} - Recipe Reel Manager`;
    } else {
      document.title = 'Recipe Details - Recipe Reel Manager';
    }
  }, [recipe]);

  // Fetch recipe details
  useEffect(() => {
    const fetchRecipe = async () => {
      if (!id) {
        navigate('/');
        return;
      }

      try {
        setLoading(true);
        const response = await apiService.getRecipe(id);
        
        if (response.data) {
          setRecipe(response.data);
          setShareUrl(window.location.href);
        } else {
          navigate('/');
        }
      } catch (error: any) {
        console.error('Error fetching recipe:', error);
        navigate('/');
      } finally {
        setLoading(false);
      }
    };

    fetchRecipe();
  }, [id, navigate]);

  // Toggle ingredient checkbox
  const toggleIngredient = (index: number) => {
    const newChecked = new Set(checkedIngredients);
    if (newChecked.has(index)) {
      newChecked.delete(index);
    } else {
      newChecked.add(index);
    }
    setCheckedIngredients(newChecked);
  };

  // Clear all ingredient checkboxes
  const clearAllIngredients = () => {
    setCheckedIngredients(new Set());
  };

  // Check all ingredient checkboxes
  const checkAllIngredients = () => {
    if (!recipe) return;
    const allIndices = new Set(recipe.ingredients.map((_, index) => index));
    setCheckedIngredients(allIndices);
  };

  // Handle recipe deletion
  const handleDelete = async () => {
    if (!recipe) return;

    try {
      setIsDeleting(true);
      await deleteRecipe(recipe.id);
      navigate('/');
    } catch (error) {
      console.error('Error deleting recipe:', error);
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  // Share recipe
  const shareRecipe = async () => {
    if (!recipe) return;

    if (navigator.share) {
      try {
        await navigator.share({
          title: recipe.title,
          text: `Check out this recipe: ${recipe.title}`,
          url: shareUrl,
        });
      } catch (error) {
        console.error('Error sharing:', error);
        copyToClipboard();
      }
    } else {
      copyToClipboard();
    }
  };

  // Copy share URL to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl).then(() => {
      // You could show a toast notification here
      alert('Recipe link copied to clipboard!');
    }).catch(() => {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Recipe link copied to clipboard!');
    });
  };

  // Get category info
  const getCategoryInfo = (category: string) => {
    return RECIPE_CATEGORIES.find(cat => cat.name === category) || RECIPE_CATEGORIES[0];
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Loading size="large" message="Loading recipe..." />
      </div>
    );
  }

  // Recipe not found
  if (!recipe) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Recipe Not Found
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            The recipe you're looking for doesn't exist or has been removed.
          </p>
          <Link to="/">
            <Button variant="primary">
              Back to Recipes
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const categoryInfo = getCategoryInfo(recipe.category);
  const isOwner = user?.uid === recipe.userId;
  const completedIngredients = checkedIngredients.size;
  const totalIngredients = recipe.ingredients.length;
  const progressPercentage = totalIngredients > 0 ? (completedIngredients / totalIngredients) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <Link
              to="/"
              className="inline-flex items-center text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Recipes
            </Link>
            
            <div className="flex items-center space-x-3">
              <Button
                variant="ghost"
                onClick={shareRecipe}
                icon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                }
              >
                Share
              </Button>
              
              {isOwner && (
                <>
                  <Link to={`/recipe/${recipe.id}/edit`}>
                    <Button
                      variant="ghost"
                      icon={
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      }
                    >
                      Edit
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    onClick={() => setShowDeleteModal(true)}
                    icon={
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    }
                    className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                  >
                    Delete
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {error.hasError && (
          <ErrorBanner
            variant="error"
            message={error.message || 'An error occurred'}
            dismissible
            onDismiss={clearError}
            className="mb-6"
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Recipe Info */}
          <div className="lg:col-span-2 space-y-8">
            {/* Recipe Header */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    {recipe.title}
                  </h1>
                  <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                    <span
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                      style={{ backgroundColor: categoryInfo.color }}
                    >
                      <span className="mr-1">{categoryInfo.icon}</span>
                      {recipe.category}
                    </span>
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {recipe.cookingTime} minutes
                    </div>
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      {recipe.difficulty}
                    </div>
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                      {recipe.likes} likes
                    </div>
                  </div>
                </div>
                
                {recipe.aiExtracted && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    AI Extracted
                  </span>
                )}
              </div>

              {/* Tags */}
              {recipe.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {recipe.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Dietary Info */}
              {recipe.dietaryInfo.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {recipe.dietaryInfo.map((info, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                    >
                      {info}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Ingredients */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Ingredients ({totalIngredients})
                </h2>
                <div className="flex items-center space-x-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearAllIngredients}
                    disabled={checkedIngredients.size === 0}
                  >
                    Clear All
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={checkAllIngredients}
                    disabled={checkedIngredients.size === totalIngredients}
                  >
                    Check All
                  </Button>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                  <span>Progress</span>
                  <span>{completedIngredients} of {totalIngredients}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
              </div>

              {/* Ingredients List */}
              <IngredientsList
                ingredients={recipe.ingredients}
                checkedIngredients={checkedIngredients}
                onToggleIngredient={toggleIngredient}
              />
            </div>

            {/* Instructions */}
            {recipe.instructions && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Cooking Instructions
                </h2>
                <div className="prose prose-gray dark:prose-invert max-w-none">
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">
                    {recipe.instructions}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Instagram Embed */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 sticky top-8">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Original Post
              </h3>
              
              {recipe.embedCode ? (
                <InstagramEmbed embedCode={recipe.embedCode} title={recipe.title} />
              ) : (
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Instagram embed not available
                  </p>
                  <Link
                    to={recipe.instagramUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 inline-flex items-center text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
                  >
                    View on Instagram
                    <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Delete Confirmation Modal */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => setShowDeleteModal(false)}
          title="Delete Recipe"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-700 dark:text-gray-300">
              Are you sure you want to delete "<strong>{recipe.title}</strong>"? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <Button
                variant="ghost"
                onClick={() => setShowDeleteModal(false)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDelete}
                loading={isDeleting}
                loadingText="Deleting..."
                disabled={isDeleting}
              >
                Delete Recipe
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  );
};

export default RecipeDetail;