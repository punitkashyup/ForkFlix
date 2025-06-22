import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import ErrorBanner from '../components/common/ErrorBanner';
import { RECIPE_CATEGORIES, PAGINATION } from '../config/constants';
import type { Recipe, RecipeCategory } from '../types';

/**
 * Recipe card component for displaying individual recipes
 */
interface RecipeCardProps {
  recipe: Recipe;
  onView: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, onView, onEdit, onDelete }) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this recipe?')) {
      setIsDeleting(true);
      try {
        await onDelete(recipe.id);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const getCategoryInfo = (category: string) => {
    return RECIPE_CATEGORIES.find(cat => cat.name === category) || RECIPE_CATEGORIES[0];
  };

  const categoryInfo = getCategoryInfo(recipe.category);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
      {/* Thumbnail */}
      <div className="relative h-48 bg-gray-200 dark:bg-gray-700">
        {recipe.thumbnailUrl ? (
          <img
            src={recipe.thumbnailUrl}
            alt={recipe.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        
        {/* Category Badge */}
        <div className="absolute top-3 left-3">
          <span
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white shadow-sm"
            style={{ backgroundColor: categoryInfo.color }}
          >
            <span className="mr-1">{categoryInfo.icon}</span>
            {recipe.category}
          </span>
        </div>

        {/* AI Badge */}
        {recipe.aiExtracted && (
          <div className="absolute top-3 right-3">
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              AI
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
              {recipe.title}
            </h3>
            <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {recipe.cookingTime}min
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
                {recipe.likes}
              </div>
            </div>
          </div>
        </div>

        {/* Tags */}
        {recipe.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {recipe.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
              >
                {tag}
              </span>
            ))}
            {recipe.tags.length > 3 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                +{recipe.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex justify-between items-center">
          <Button
            variant="primary"
            size="sm"
            onClick={() => onView(recipe.id)}
          >
            View Recipe
          </Button>
          
          <div className="flex space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(recipe.id)}
              icon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              }
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              loading={isDeleting}
              icon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              }
              className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Empty state component when no recipes are found
 */
const EmptyState: React.FC<{ onAddRecipe: () => void }> = ({ onAddRecipe }) => (
  <div className="text-center py-12">
    <svg className="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
    <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">No recipes found</h3>
    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
      Get started by adding your first recipe from Instagram.
    </p>
    <div className="mt-6">
      <Button
        variant="primary"
        onClick={onAddRecipe}
        icon={
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        }
      >
        Add Your First Recipe
      </Button>
    </div>
  </div>
);

/**
 * Home page component with recipe grid, search, and filtering
 */
const Home: React.FC = () => {
  const { user, recipes, loading, error, fetchRecipes, deleteRecipe, clearError } = useApp();
  const navigate = useNavigate();
  
  // State for search and filtering
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<RecipeCategory | 'all'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([]);

  // Set page title
  useEffect(() => {
    document.title = 'Home - Recipe Reel Manager';
  }, []);

  // Fetch recipes on component mount
  useEffect(() => {
    if (user) {
      fetchRecipes(1, PAGINATION.DEFAULT_LIMIT);
    }
  }, [user, fetchRecipes]);

  // Filter recipes based on search and category
  useEffect(() => {
    let filtered = recipes;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(recipe =>
        recipe.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        recipe.ingredients.some(ingredient => 
          ingredient.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        recipe.tags.some(tag => 
          tag.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(recipe => recipe.category === selectedCategory);
    }

    setFilteredRecipes(filtered);
  }, [recipes, searchTerm, selectedCategory]);

  // Navigation handlers
  const handleAddRecipe = () => {
    navigate('/add-recipe');
  };

  const handleViewRecipe = (id: string) => {
    navigate(`/recipe/${id}`);
  };

  const handleEditRecipe = (id: string) => {
    navigate(`/recipe/${id}/edit`);
  };

  const handleDeleteRecipe = async (id: string) => {
    await deleteRecipe(id);
  };

  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
    setSelectedCategory('all');
  };

  // If not logged in, show login prompt
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Welcome to Recipe Reel Manager
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Please sign in to access your recipes
          </p>
          <div className="space-x-4">
            <Button variant="primary" onClick={() => navigate('/login')}>
              Sign In
            </Button>
            <Button variant="ghost" onClick={() => navigate('/signup')}>
              Sign Up
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Welcome back, {user.displayName}!
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                You have {recipes.length} recipe{recipes.length !== 1 ? 's' : ''} in your collection
              </p>
            </div>
            <div className="mt-4 sm:mt-0">
              <Button
                variant="primary"
                onClick={handleAddRecipe}
                icon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                }
              >
                Add Recipe
              </Button>
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

        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Search recipes, ingredients, or tags..."
              />
            </div>

            {/* Clear Button */}
            {(searchTerm || selectedCategory !== 'all') && (
              <Button
                variant="ghost"
                onClick={clearSearch}
                icon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                }
              >
                Clear
              </Button>
            )}
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`
                px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200
                ${selectedCategory === 'all'
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }
              `}
            >
              All Categories
            </button>
            {RECIPE_CATEGORIES.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.name as RecipeCategory)}
                className={`
                  px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200 flex items-center space-x-2
                  ${selectedCategory === category.name
                    ? 'text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                  }
                `}
                style={{
                  backgroundColor: selectedCategory === category.name ? category.color : undefined,
                }}
              >
                <span>{category.icon}</span>
                <span>{category.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading.isLoading && (
          <div className="text-center py-12">
            <Loading size="large" message={loading.message || 'Loading recipes...'} />
          </div>
        )}

        {/* Recipe Grid */}
        {!loading.isLoading && (
          <>
            {filteredRecipes.length === 0 ? (
              <EmptyState onAddRecipe={handleAddRecipe} />
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {filteredRecipes.map((recipe) => (
                    <RecipeCard
                      key={recipe.id}
                      recipe={recipe}
                      onView={handleViewRecipe}
                      onEdit={handleEditRecipe}
                      onDelete={handleDeleteRecipe}
                    />
                  ))}
                </div>

                {/* Pagination Placeholder */}
                {filteredRecipes.length >= PAGINATION.DEFAULT_LIMIT && (
                  <div className="mt-8 flex justify-center">
                    <div className="flex space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(currentPage - 1)}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setCurrentPage(currentPage + 1)}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Home;