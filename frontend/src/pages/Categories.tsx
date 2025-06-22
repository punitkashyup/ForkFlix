import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Grid, Filter, Search } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { LoadingSpinner } from '../components/common/Loading';
import ErrorBanner from '../components/common/ErrorBanner';
import { RECIPE_CATEGORIES } from '../config/constants';
import type { Recipe, RecipeCategory } from '../types';

export default function Categories() {
  const { user, loading } = useApp();
  const [selectedCategory, setSelectedCategory] = useState<RecipeCategory | 'all'>('all');
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadRecipes();
  }, [selectedCategory]);

  useEffect(() => {
    filterRecipes();
  }, [recipes, searchTerm, selectedCategory]);

  const loadRecipes = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      // TODO: Replace with actual API call
      // const response = await apiService.getRecipes({ category: selectedCategory });
      // setRecipes(response.data.items);
      
      // Mock data for now
      setRecipes([]);
      
    } catch (err: any) {
      setError(err.message || 'Failed to load recipes');
    } finally {
      setIsLoading(false);
    }
  };

  const filterRecipes = () => {
    let filtered = recipes;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(recipe => recipe.category === selectedCategory);
    }

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

    setFilteredRecipes(filtered);
  };

  const getCategoryCount = (category: RecipeCategory | 'all') => {
    if (category === 'all') return recipes.length;
    return recipes.filter(recipe => recipe.category === category).length;
  };

  if (loading.isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" message="Loading categories..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Recipe Categories</h1>
        <p className="text-gray-600">Discover recipes organized by category</p>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Search recipes, ingredients, or tags..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-6">
          <ErrorBanner message={error} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Categories Sidebar */}
        <div className="lg:col-span-1">
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              Categories
            </h2>
            
            <div className="space-y-2">
              {/* All Categories */}
              <button
                onClick={() => setSelectedCategory('all')}
                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                  selectedCategory === 'all'
                    ? 'bg-primary-100 text-primary-700 border border-primary-200'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span>All Recipes</span>
                  <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
                    {getCategoryCount('all')}
                  </span>
                </div>
              </button>

              {/* Individual Categories */}
              {RECIPE_CATEGORIES.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id as RecipeCategory)}
                  className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-primary-100 text-primary-700 border border-primary-200'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span>{category.name}</span>
                    <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
                      {getCategoryCount(category.id as RecipeCategory)}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Recipes Grid */}
        <div className="lg:col-span-3">
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <LoadingSpinner size="large" message="Loading recipes..." />
            </div>
          ) : filteredRecipes.length === 0 ? (
            <div className="text-center py-20">
              <Grid className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm ? 'No recipes found' : 'No recipes in this category'}
              </h3>
              <p className="text-gray-500">
                {searchTerm 
                  ? 'Try adjusting your search terms'
                  : 'Start creating recipes to see them here'
                }
              </p>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
            >
              {filteredRecipes.map((recipe) => (
                <motion.div
                  key={recipe.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card hover:shadow-lg transition-shadow"
                >
                  {/* Recipe Card Content */}
                  <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {recipe.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-4">
                      {recipe.category} • {recipe.cookingTime} min • {recipe.difficulty}
                    </p>
                    
                    {/* Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {recipe.tags.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                      {recipe.tags.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{recipe.tags.length - 3} more
                        </span>
                      )}
                    </div>
                    
                    {/* Actions */}
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        {recipe.ingredients.length} ingredients
                      </span>
                      <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                        View Recipe
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}