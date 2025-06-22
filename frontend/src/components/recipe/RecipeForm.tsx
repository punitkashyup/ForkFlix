import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { Plus, X, Upload, Clock, Users } from 'lucide-react';
import CookingAnimation from '../common/CookingAnimation';
import SuccessAnimation from '../common/SuccessAnimation';
import ErrorAnimation from '../common/ErrorAnimation';

interface FormData {
  title: string;
  description: string;
  ingredients: string[];
  instructions: string[];
  cookTime: number;
  servings: number;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  category: string;
  image?: File;
}

interface RecipeFormProps {
  onSubmit: (data: FormData) => Promise<void>;
  initialData?: Partial<FormData>;
  isLoading?: boolean;
  className?: string;
}

const RecipeForm: React.FC<RecipeFormProps> = ({
  onSubmit,
  initialData,
  isLoading = false,
  className = ''
}) => {
  const [ingredients, setIngredients] = useState<string[]>(initialData?.ingredients || ['']);
  const [instructions, setInstructions] = useState<string[]>(initialData?.instructions || ['']);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue
  } = useForm<FormData>({
    defaultValues: {
      title: initialData?.title || '',
      description: initialData?.description || '',
      cookTime: initialData?.cookTime || 30,
      servings: initialData?.servings || 4,
      difficulty: initialData?.difficulty || 'Medium',
      category: initialData?.category || ''
    }
  });

  const handleFormSubmit = async (data: FormData) => {
    setSubmitStatus('loading');
    try {
      await onSubmit({
        ...data,
        ingredients: ingredients.filter(i => i.trim()),
        instructions: instructions.filter(i => i.trim())
      });
      setSubmitStatus('success');
      setTimeout(() => setSubmitStatus('idle'), 2000);
    } catch (error) {
      setSubmitStatus('error');
      setTimeout(() => setSubmitStatus('idle'), 3000);
    }
  };

  const addIngredient = () => {
    setIngredients([...ingredients, '']);
  };

  const removeIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const updateIngredient = (index: number, value: string) => {
    const newIngredients = [...ingredients];
    newIngredients[index] = value;
    setIngredients(newIngredients);
  };

  const addInstruction = () => {
    setInstructions([...instructions, '']);
  };

  const removeInstruction = (index: number) => {
    setInstructions(instructions.filter((_, i) => i !== index));
  };

  const updateInstruction = (index: number, value: string) => {
    const newInstructions = [...instructions];
    newInstructions[index] = value;
    setInstructions(newInstructions);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setValue('image', file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const containerVariants = {
    hidden: {
      opacity: 0,
      y: prefersReducedMotion ? 0 : 20
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        staggerChildren: prefersReducedMotion ? 0 : 0.1
      }
    }
  };

  const itemVariants = {
    hidden: {
      opacity: 0,
      y: prefersReducedMotion ? 0 : 10
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3
      }
    }
  };

  const inputFocusVariants = {
    focus: {
      scale: prefersReducedMotion ? 1 : 1.02,
      transition: {
        duration: 0.2
      }
    },
    blur: {
      scale: 1,
      transition: {
        duration: 0.2
      }
    }
  };

  if (submitStatus === 'loading') {
    return (
      <div className="min-h-96 flex flex-col items-center justify-center">
        <CookingAnimation size={100} />
        <motion.p 
          className="text-lg text-gray-600 mt-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          Saving your delicious recipe...
        </motion.p>
      </div>
    );
  }

  if (submitStatus === 'success') {
    return (
      <motion.div 
        className="min-h-96 flex flex-col items-center justify-center text-center"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
      >
        <SuccessAnimation size={100} />
        <h3 className="text-2xl font-bold text-gray-900 mt-4 mb-2">Recipe Saved!</h3>
        <p className="text-gray-600">Your recipe has been successfully saved and is ready to share.</p>
      </motion.div>
    );
  }

  if (submitStatus === 'error') {
    return (
      <motion.div 
        className="min-h-96 flex flex-col items-center justify-center text-center"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
      >
        <ErrorAnimation size={100} />
        <h3 className="text-2xl font-bold text-gray-900 mt-4 mb-2">Something went wrong</h3>
        <p className="text-gray-600 mb-4">There was an error saving your recipe. Please try again.</p>
        <button
          onClick={() => setSubmitStatus('idle')}
          className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          Try Again
        </button>
      </motion.div>
    );
  }

  return (
    <motion.form
      onSubmit={handleSubmit(handleFormSubmit)}
      className={`max-w-4xl mx-auto space-y-8 ${className}`}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Basic Information */}
      <motion.div className="bg-white rounded-xl p-6 shadow-md" variants={itemVariants}>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Basic Information</h2>
        
        <div className="space-y-4">
          {/* Title */}
          <motion.div variants={inputFocusVariants} whileFocus="focus">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recipe Title *
            </label>
            <input
              {...register('title', { required: 'Title is required' })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter recipe title..."
            />
            <AnimatePresence>
              {errors.title && (
                <motion.p
                  className="text-red-500 text-sm mt-1"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  {errors.title.message}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Description */}
          <motion.div variants={inputFocusVariants} whileFocus="focus">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              placeholder="Brief description of your recipe..."
            />
          </motion.div>

          {/* Meta Information */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <motion.div variants={inputFocusVariants} whileFocus="focus">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="w-4 h-4 inline mr-1" />
                Cook Time (minutes)
              </label>
              <input
                {...register('cookTime', { required: true, min: 1 })}
                type="number"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              />
            </motion.div>

            <motion.div variants={inputFocusVariants} whileFocus="focus">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="w-4 h-4 inline mr-1" />
                Servings
              </label>
              <input
                {...register('servings', { required: true, min: 1 })}
                type="number"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              />
            </motion.div>

            <motion.div variants={inputFocusVariants} whileFocus="focus">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty
              </label>
              <select
                {...register('difficulty')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              >
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Image Upload */}
      <motion.div className="bg-white rounded-xl p-6 shadow-md" variants={itemVariants}>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Photo</h2>
        
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            {imagePreview ? (
              <motion.img
                src={imagePreview}
                alt="Recipe preview"
                className="max-h-64 mx-auto rounded-lg"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              />
            ) : (
              <div>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Click to upload a photo of your recipe</p>
              </div>
            )}
          </label>
        </div>
      </motion.div>

      {/* Ingredients */}
      <motion.div className="bg-white rounded-xl p-6 shadow-md" variants={itemVariants}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Ingredients</h2>
          <motion.button
            type="button"
            onClick={addIngredient}
            className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            whileHover={{ scale: prefersReducedMotion ? 1 : 1.05 }}
            whileTap={{ scale: prefersReducedMotion ? 1 : 0.95 }}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Ingredient
          </motion.button>
        </div>

        <div className="space-y-3">
          <AnimatePresence>
            {ingredients.map((ingredient, index) => (
              <motion.div
                key={index}
                className="flex items-center space-x-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <span className="text-gray-500 font-medium">{index + 1}.</span>
                <motion.input
                  type="text"
                  value={ingredient}
                  onChange={(e) => updateIngredient(index, e.target.value)}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                  placeholder="Enter ingredient..."
                  variants={inputFocusVariants}
                  whileFocus="focus"
                />
                {ingredients.length > 1 && (
                  <motion.button
                    type="button"
                    onClick={() => removeIngredient(index)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    whileHover={{ scale: prefersReducedMotion ? 1 : 1.1 }}
                    whileTap={{ scale: prefersReducedMotion ? 1 : 0.9 }}
                  >
                    <X className="w-4 h-4" />
                  </motion.button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Instructions */}
      <motion.div className="bg-white rounded-xl p-6 shadow-md" variants={itemVariants}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Instructions</h2>
          <motion.button
            type="button"
            onClick={addInstruction}
            className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            whileHover={{ scale: prefersReducedMotion ? 1 : 1.05 }}
            whileTap={{ scale: prefersReducedMotion ? 1 : 0.95 }}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Step
          </motion.button>
        </div>

        <div className="space-y-4">
          <AnimatePresence>
            {instructions.map((instruction, index) => (
              <motion.div
                key={index}
                className="flex items-start space-x-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <span className="text-gray-500 font-medium mt-3">{index + 1}.</span>
                <motion.textarea
                  value={instruction}
                  onChange={(e) => updateInstruction(index, e.target.value)}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                  placeholder="Describe this step..."
                  rows={2}
                  variants={inputFocusVariants}
                  whileFocus="focus"
                />
                {instructions.length > 1 && (
                  <motion.button
                    type="button"
                    onClick={() => removeInstruction(index)}
                    className="p-2 mt-1 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    whileHover={{ scale: prefersReducedMotion ? 1 : 1.1 }}
                    whileTap={{ scale: prefersReducedMotion ? 1 : 0.9 }}
                  >
                    <X className="w-4 h-4" />
                  </motion.button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Submit Button */}
      <motion.div
        className="flex justify-center"
        variants={itemVariants}
      >
        <motion.button
          type="submit"
          disabled={isLoading}
          className="px-8 py-4 bg-primary-500 text-white text-lg font-semibold rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          whileHover={{ scale: prefersReducedMotion ? 1 : 1.05 }}
          whileTap={{ scale: prefersReducedMotion ? 1 : 0.95 }}
        >
          {isLoading ? 'Saving Recipe...' : 'Save Recipe'}
        </motion.button>
      </motion.div>
    </motion.form>
  );
};

export default RecipeForm;