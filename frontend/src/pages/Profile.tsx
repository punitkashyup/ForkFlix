import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { User, Settings, Camera, Save } from 'lucide-react';
import { useApp } from '../context/AppContext';
import Button from '../components/common/Button';
import { LoadingSpinner } from '../components/common/Loading';
import ErrorBanner from '../components/common/ErrorBanner';
import type { UserProfileFormData } from '../types';

export function Profile() {
  const { user, loading, error } = useApp();
  const [isEditing, setIsEditing] = useState(false);
  const [localError, setLocalError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch
  } = useForm<UserProfileFormData>({
    defaultValues: {
      displayName: user?.displayName || '',
      preferences: user?.preferences || {
        defaultCategory: 'Main Course',
        aiAutoExtract: true,
        publicRecipes: false
      }
    }
  });

  // Reset form when user data changes
  useEffect(() => {
    if (user) {
      reset({
        displayName: user.displayName,
        preferences: user.preferences
      });
    }
  }, [user, reset]);

  const onSubmit = async (data: UserProfileFormData) => {
    try {
      setLocalError('');
      // Update user profile would go here
      // await updateUserProfile(data);
      setSuccessMessage('Profile updated successfully!');
      setIsEditing(false);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setLocalError(err.message || 'Failed to update profile');
    }
  };

  const handleCancel = () => {
    reset();
    setIsEditing(false);
    setLocalError('');
  };

  if (loading.isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" message="Loading profile..." />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-20">
        <User className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No user data</h3>
        <p className="text-gray-500">Please try refreshing the page.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile</h1>
        <p className="text-gray-600">Manage your account settings and preferences</p>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="mb-6">
          <ErrorBanner
            variant="success"
            message={successMessage}
            onClose={() => setSuccessMessage('')}
          />
        </div>
      )}

      {/* Error Message */}
      {(error.hasError || localError) && (
        <div className="mb-6">
          <ErrorBanner
            variant="error"
            message={error.message || localError}
            onClose={() => setLocalError('')}
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Overview */}
        <div className="lg:col-span-1">
          <div className="card p-6">
            <div className="text-center">
              {/* Avatar */}
              <div className="relative inline-block mb-4">
                {user.photoURL ? (
                  <img
                    src={user.photoURL}
                    alt={user.displayName}
                    className="w-24 h-24 rounded-full border-4 border-white shadow-lg"
                  />
                ) : (
                  <div className="w-24 h-24 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold border-4 border-white shadow-lg">
                    {user.displayName.charAt(0).toUpperCase()}
                  </div>
                )}
                <button
                  type="button"
                  className="absolute bottom-0 right-0 bg-white rounded-full p-2 shadow-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  disabled
                >
                  <Camera className="h-4 w-4 text-gray-600" />
                </button>
              </div>

              <h2 className="text-xl font-semibold text-gray-900 mb-1">
                {user.displayName}
              </h2>
              <p className="text-gray-500 mb-4">{user.email}</p>

              {/* Stats */}
              <div className="grid grid-cols-1 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-gray-900">
                    {user.recipeCount}
                  </div>
                  <div className="text-sm text-gray-500">Recipes Created</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Settings */}
        <div className="lg:col-span-2">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Account Settings
              </h3>
              {!isEditing && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                >
                  Edit Profile
                </Button>
              )}
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Display Name */}
              <div>
                <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 mb-2">
                  Display Name
                </label>
                <input
                  {...register('displayName', {
                    required: 'Display name is required',
                    minLength: {
                      value: 2,
                      message: 'Display name must be at least 2 characters'
                    }
                  })}
                  type="text"
                  id="displayName"
                  disabled={!isEditing}
                  className={`input-field ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                  placeholder="Enter your display name"
                />
                {errors.displayName && (
                  <p className="mt-1 text-sm text-red-600">{errors.displayName.message}</p>
                )}
              </div>

              {/* Email (read-only) */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  value={user.email}
                  disabled
                  className="input-field bg-gray-50 cursor-not-allowed"
                />
                <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
              </div>

              {/* Preferences */}
              <div className="border-t pt-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Preferences</h4>
                
                <div className="space-y-4">
                  {/* Default Category */}
                  <div>
                    <label htmlFor="defaultCategory" className="block text-sm font-medium text-gray-700 mb-2">
                      Default Recipe Category
                    </label>
                    <select
                      {...register('preferences.defaultCategory')}
                      id="defaultCategory"
                      disabled={!isEditing}
                      className={`input-field ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                    >
                      <option value="Starters">Starters</option>
                      <option value="Main Course">Main Course</option>
                      <option value="Desserts">Desserts</option>
                      <option value="Beverages">Beverages</option>
                      <option value="Snacks">Snacks</option>
                    </select>
                  </div>

                  {/* AI Auto Extract */}
                  <div className="flex items-center">
                    <input
                      {...register('preferences.aiAutoExtract')}
                      type="checkbox"
                      id="aiAutoExtract"
                      disabled={!isEditing}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label htmlFor="aiAutoExtract" className="ml-2 block text-sm text-gray-700">
                      Automatically extract recipe information using AI
                    </label>
                  </div>

                  {/* Public Recipes */}
                  <div className="flex items-center">
                    <input
                      {...register('preferences.publicRecipes')}
                      type="checkbox"
                      id="publicRecipes"
                      disabled={!isEditing}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label htmlFor="publicRecipes" className="ml-2 block text-sm text-gray-700">
                      Make my recipes public by default
                    </label>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {isEditing && (
                <div className="flex justify-end space-x-3 pt-6 border-t">
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleCancel}
                    disabled={isSubmitting}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={isSubmitting}
                    leftIcon={<Save className="h-4 w-4" />}
                  >
                    Save Changes
                  </Button>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}