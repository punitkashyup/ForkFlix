import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import ErrorBanner from '../components/common/ErrorBanner';
import { apiService } from '../services/api';
import { RECIPE_CATEGORIES, DIFFICULTY_LEVELS, VALIDATION } from '../config/constants';
import type { RecipeFormData, RecipeCategory, RecipeDifficulty, InstagramMetadata, AIAnalysisResult } from '../types';

/**
 * Add recipe form data interface
 */
interface AddRecipeFormData extends RecipeFormData {
  cookingTime?: number;
  difficulty?: RecipeDifficulty;
  ingredients?: string[];
  instructions?: string;
  tags?: string[];
  isPublic?: boolean;
}

/**
 * AddRecipe page component with Instagram URL input and AI extraction
 */
const AddRecipe: React.FC = () => {
  const { createRecipe, user, loading, error, clearError } = useApp();
  const navigate = useNavigate();
  
  // State for Instagram processing
  const [instagramMetadata, setInstagramMetadata] = useState<InstagramMetadata | null>(null);
  const [aiAnalysis, setAIAnalysis] = useState<AIAnalysisResult | null>(null);
  const [isValidatingUrl, setIsValidatingUrl] = useState(false);
  const [isExtractingAI, setIsExtractingAI] = useState(false);
  const [urlError, setUrlError] = useState<string>('');
  const [showManualForm, setShowManualForm] = useState(false);
  const [currentStep, setCurrentStep] = useState<'url' | 'preview' | 'details' | 'manual'>('url');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
    reset,
  } = useForm<AddRecipeFormData>({
    defaultValues: {
      instagramUrl: '',
      title: '',
      category: 'Main Course',
      cookingTime: 30,
      difficulty: 'Medium',
      ingredients: [],
      instructions: '',
      tags: [],
      isPublic: false,
    },
  });

  const watchedUrl = watch('instagramUrl');
  const watchedIngredients = watch('ingredients') || [];

  // Set page title
  useEffect(() => {
    document.title = 'Add Recipe - Recipe Reel Manager';
  }, []);

  // Redirect if not logged in
  useEffect(() => {
    if (!user) {
      navigate('/login', { replace: true });
    }
  }, [user, navigate]);

  // Validate Instagram URL
  const validateInstagramUrl = async (url: string) => {
    if (!url) return;

    try {
      setIsValidatingUrl(true);
      setUrlError('');
      
      const response = await apiService.validateInstagramUrl(url);
      
      if (response.data?.isValid) {
        // Get Instagram metadata
        const metadataResponse = await apiService.getInstagramMetadata(url);
        if (metadataResponse.data) {
          setInstagramMetadata(metadataResponse.data);
          setCurrentStep('preview');
        }
      } else {
        setUrlError(response.data?.message || 'Invalid Instagram URL');
      }
    } catch (error: any) {
      setUrlError(error.response?.data?.message || 'Failed to validate Instagram URL');
    } finally {
      setIsValidatingUrl(false);
    }
  };

  // Extract recipe data using AI
  const extractWithAI = async () => {
    if (!watchedUrl) return;

    try {
      setIsExtractingAI(true);
      clearError();
      
      const response = await apiService.extractRecipeFromInstagram(watchedUrl);
      
      if (response.data) {
        setAIAnalysis(response.data);
        
        // Pre-fill form with AI data
        setValue('title', instagramMetadata?.title || '');
        setValue('category', response.data.category);
        setValue('cookingTime', response.data.cookingTime);
        setValue('difficulty', response.data.difficulty);
        setValue('ingredients', response.data.ingredients);
        setValue('instructions', response.data.instructions || '');
        setValue('tags', response.data.tags);
        
        setCurrentStep('details');
      }
    } catch (error: any) {
      console.error('AI extraction error:', error);
      // Continue to manual form even if AI fails
      setShowManualForm(true);
      setCurrentStep('manual');
    } finally {
      setIsExtractingAI(false);
    }
  };

  // Skip AI and go to manual form
  const skipAI = () => {
    if (instagramMetadata) {
      setValue('title', instagramMetadata.title || '');
    }
    setShowManualForm(true);
    setCurrentStep('manual');
  };

  // Handle form submission
  const onSubmit = async (data: AddRecipeFormData) => {
    try {
      clearError();
      
      const recipeData: RecipeFormData = {
        instagramUrl: data.instagramUrl,
        title: data.title,
        category: data.category,
        isPublic: data.isPublic,
      };

      const newRecipe = await createRecipe(recipeData);
      navigate(`/recipe/${newRecipe.id}`);
    } catch (error: any) {
      console.error('Recipe creation error:', error);
    }
  };

  // Add ingredient
  const addIngredient = () => {
    const currentIngredients = watchedIngredients;
    setValue('ingredients', [...currentIngredients, '']);
  };

  // Remove ingredient
  const removeIngredient = (index: number) => {
    const currentIngredients = watchedIngredients;
    setValue('ingredients', currentIngredients.filter((_, i) => i !== index));
  };

  // Update ingredient
  const updateIngredient = (index: number, value: string) => {
    const currentIngredients = [...watchedIngredients];
    currentIngredients[index] = value;
    setValue('ingredients', currentIngredients);
  };

  // Reset form and go back to URL step
  const startOver = () => {
    reset();
    setInstagramMetadata(null);
    setAIAnalysis(null);
    setUrlError('');
    setShowManualForm(false);
    setCurrentStep('url');
    clearError();
  };

  if (!user) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Add New Recipe
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Import a recipe from Instagram or create one manually
              </p>
            </div>
            <Link
              to="/"
              className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Link>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <nav aria-label="Progress">
            <ol role="list" className="flex items-center">
              {[
                { id: 'url', name: 'Instagram URL', status: currentStep === 'url' ? 'current' : currentStep === 'preview' || currentStep === 'details' || currentStep === 'manual' ? 'complete' : 'upcoming' },
                { id: 'preview', name: 'Preview', status: currentStep === 'preview' ? 'current' : currentStep === 'details' || currentStep === 'manual' ? 'complete' : 'upcoming' },
                { id: 'details', name: 'Recipe Details', status: currentStep === 'details' || currentStep === 'manual' ? 'current' : 'upcoming' },
              ].map((step, stepIdx) => (
                <li key={step.id} className={stepIdx !== 2 ? 'pr-8 sm:pr-20' : ''}>
                  <div className="flex items-center">
                    <div className="flex items-center text-sm">
                      <span className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
                        step.status === 'complete'
                          ? 'border-primary-600 bg-primary-600'
                          : step.status === 'current'
                          ? 'border-primary-600 bg-white dark:bg-gray-800'
                          : 'border-gray-300 bg-white dark:bg-gray-800 dark:border-gray-600'
                      }`}>
                        {step.status === 'complete' ? (
                          <svg className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <span className={`${
                            step.status === 'current'
                              ? 'text-primary-600'
                              : 'text-gray-500 dark:text-gray-400'
                          }`}>
                            {stepIdx + 1}
                          </span>
                        )}
                      </span>
                      <span className={`ml-4 text-sm font-medium ${
                        step.status === 'current'
                          ? 'text-primary-600 dark:text-primary-400'
                          : step.status === 'complete'
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        {step.name}
                      </span>
                    </div>
                    {stepIdx !== 2 && (
                      <div className={`ml-4 h-0.5 w-full ${
                        step.status === 'complete'
                          ? 'bg-primary-600'
                          : 'bg-gray-200 dark:bg-gray-700'
                      }`} />
                    )}
                  </div>
                </li>
              ))}
            </ol>
          </nav>
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

        {/* Step 1: Instagram URL Input */}
        {currentStep === 'url' && (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Enter Instagram Recipe URL
            </h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="instagramUrl" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Instagram Post URL
                </label>
                <div className="flex space-x-4">
                  <div className="flex-1">
                    <input
                      {...register('instagramUrl', {
                        required: 'Instagram URL is required',
                        pattern: {
                          value: /^https?:\/\/(www\.)?instagram\.com\/(p|reel)\/[a-zA-Z0-9_-]+\/?/,
                          message: 'Please enter a valid Instagram post or reel URL',
                        },
                      })}
                      type="url"
                      className={`
                        block w-full px-3 py-2 border rounded-lg
                        placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-700
                        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                        dark:border-gray-600 dark:placeholder-gray-400
                        ${errors.instagramUrl || urlError
                          ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500'
                          : 'border-gray-300'
                        }
                      `}
                      placeholder="https://www.instagram.com/p/..."
                    />
                    {(errors.instagramUrl || urlError) && (
                      <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                        {errors.instagramUrl?.message || urlError}
                      </p>
                    )}
                  </div>
                  <Button
                    type="button"
                    variant="primary"
                    onClick={() => validateInstagramUrl(watchedUrl)}
                    loading={isValidatingUrl}
                    loadingText="Validating..."
                    disabled={!watchedUrl || !!errors.instagramUrl}
                  >
                    Validate URL
                  </Button>
                </div>
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                <p>Tip: Copy the URL from an Instagram recipe post or reel and paste it above.</p>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Instagram Preview */}
        {currentStep === 'preview' && instagramMetadata && (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Instagram Post Preview
            </h2>
            <div className="space-y-6">
              {/* Instagram Embed Preview */}
              <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-700">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{instagramMetadata.authorName}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Instagram</p>
                  </div>
                </div>
                {instagramMetadata.thumbnailUrl && (
                  <img
                    src={instagramMetadata.thumbnailUrl}
                    alt="Instagram post thumbnail"
                    className="w-full h-64 object-cover rounded-lg mb-3"
                  />
                )}
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">{instagramMetadata.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{instagramMetadata.description}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-between">
                <Button
                  variant="ghost"
                  onClick={startOver}
                >
                  Start Over
                </Button>
                <div className="space-x-3">
                  <Button
                    variant="ghost"
                    onClick={skipAI}
                  >
                    Skip AI Analysis
                  </Button>
                  <Button
                    variant="primary"
                    onClick={extractWithAI}
                    loading={isExtractingAI}
                    loadingText="Extracting recipe..."
                  >
                    Extract Recipe with AI
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI Extraction Loading */}
        {isExtractingAI && (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <Loading 
              size="large" 
              message="Our AI is analyzing the Instagram post to extract recipe details..." 
              centered 
            />
          </div>
        )}

        {/* Step 3: Recipe Details Form */}
        {(currentStep === 'details' || currentStep === 'manual') && (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
                Recipe Details
                {aiAnalysis && (
                  <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    AI Extracted
                  </span>
                )}
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Recipe Title */}
                <div className="md:col-span-2">
                  <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Recipe Title
                  </label>
                  <input
                    {...register('title', {
                      required: 'Recipe title is required',
                      minLength: {
                        value: VALIDATION.MIN_RECIPE_TITLE_LENGTH,
                        message: `Title must be at least ${VALIDATION.MIN_RECIPE_TITLE_LENGTH} characters`,
                      },
                      maxLength: {
                        value: VALIDATION.MAX_RECIPE_TITLE_LENGTH,
                        message: `Title cannot exceed ${VALIDATION.MAX_RECIPE_TITLE_LENGTH} characters`,
                      },
                    })}
                    type="text"
                    className={`
                      block w-full px-3 py-2 border rounded-lg
                      placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-700
                      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                      dark:border-gray-600 dark:placeholder-gray-400
                      ${errors.title
                        ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300'
                      }
                    `}
                    placeholder="Enter recipe title"
                  />
                  {errors.title && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title.message}</p>
                  )}
                </div>

                {/* Category */}
                <div>
                  <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Category
                  </label>
                  <select
                    {...register('category', { required: 'Category is required' })}
                    className={`
                      block w-full px-3 py-2 border rounded-lg
                      text-gray-900 dark:text-white dark:bg-gray-700
                      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                      dark:border-gray-600
                      ${errors.category
                        ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300'
                      }
                    `}
                  >
                    {RECIPE_CATEGORIES.map((category) => (
                      <option key={category.id} value={category.name}>
                        {category.icon} {category.name}
                      </option>
                    ))}
                  </select>
                  {errors.category && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.category.message}</p>
                  )}
                </div>

                {/* Cooking Time */}
                <div>
                  <label htmlFor="cookingTime" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Cooking Time (minutes)
                  </label>
                  <input
                    {...register('cookingTime', {
                      required: 'Cooking time is required',
                      min: { value: 1, message: 'Cooking time must be at least 1 minute' },
                      max: { value: 1440, message: 'Cooking time cannot exceed 24 hours' },
                    })}
                    type="number"
                    min="1"
                    max="1440"
                    className={`
                      block w-full px-3 py-2 border rounded-lg
                      placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-700
                      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                      dark:border-gray-600 dark:placeholder-gray-400
                      ${errors.cookingTime
                        ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300'
                      }
                    `}
                    placeholder="30"
                  />
                  {errors.cookingTime && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.cookingTime.message}</p>
                  )}
                </div>

                {/* Difficulty */}
                <div>
                  <label htmlFor="difficulty" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Difficulty Level
                  </label>
                  <select
                    {...register('difficulty', { required: 'Difficulty is required' })}
                    className={`
                      block w-full px-3 py-2 border rounded-lg
                      text-gray-900 dark:text-white dark:bg-gray-700
                      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                      dark:border-gray-600
                      ${errors.difficulty
                        ? 'border-red-300 dark:border-red-600 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300'
                      }
                    `}
                  >
                    {DIFFICULTY_LEVELS.map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                  {errors.difficulty && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.difficulty.message}</p>
                  )}
                </div>

                {/* Public Recipe */}
                <div>
                  <div className="flex items-center">
                    <input
                      {...register('isPublic')}
                      type="checkbox"
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded dark:border-gray-600 dark:bg-gray-800"
                    />
                    <label htmlFor="isPublic" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Make this recipe public
                    </label>
                  </div>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Public recipes can be discovered by other users
                  </p>
                </div>
              </div>

              {/* Ingredients */}
              <div className="mt-6">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Ingredients
                  </label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={addIngredient}
                    icon={
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                    }
                  >
                    Add Ingredient
                  </Button>
                </div>
                <div className="space-y-2">
                  {watchedIngredients.map((ingredient, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={ingredient}
                        onChange={(e) => updateIngredient(index, e.target.value)}
                        className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:placeholder-gray-400"
                        placeholder="Enter ingredient"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeIngredient(index)}
                        icon={
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        }
                        className="text-red-600 hover:text-red-700"
                      />
                    </div>
                  ))}
                  {watchedIngredients.length === 0 && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                      No ingredients added yet. Click "Add Ingredient" to start building your recipe.
                    </p>
                  )}
                </div>
              </div>

              {/* Instructions */}
              <div className="mt-6">
                <label htmlFor="instructions" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Cooking Instructions
                </label>
                <textarea
                  {...register('instructions')}
                  rows={6}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-500 text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:placeholder-gray-400"
                  placeholder="Enter step-by-step cooking instructions..."
                />
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex justify-between">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={startOver}
                >
                  Start Over
                </Button>
                <div className="space-x-3">
                  <Link to="/">
                    <Button variant="ghost">
                      Cancel
                    </Button>
                  </Link>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={isSubmitting}
                    loadingText="Creating recipe..."
                    disabled={isSubmitting}
                  >
                    Create Recipe
                  </Button>
                </div>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default AddRecipe;