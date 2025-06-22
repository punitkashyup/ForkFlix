import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User as FirebaseUser
} from 'firebase/auth';
import { auth } from '../config/firebase';
import { apiService } from '../services/api';
import type { 
  AppContextType, 
  Recipe, 
  User, 
  Category, 
  RecipeFormData,
  LoadingState,
  ErrorState 
} from '../types';
import { RECIPE_CATEGORIES } from '../config/constants';

// Action types
type AppAction = 
  | { type: 'SET_LOADING'; payload: LoadingState }
  | { type: 'SET_ERROR'; payload: ErrorState }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_RECIPES'; payload: Recipe[] }
  | { type: 'ADD_RECIPE'; payload: Recipe }
  | { type: 'UPDATE_RECIPE'; payload: Recipe }
  | { type: 'DELETE_RECIPE'; payload: string }
  | { type: 'SET_CATEGORIES'; payload: Category[] };

// Initial state
interface AppState {
  user: User | null;
  recipes: Recipe[];
  categories: Category[];
  loading: LoadingState;
  error: ErrorState;
}

const initialState: AppState = {
  user: null,
  recipes: [],
  categories: RECIPE_CATEGORIES.map(cat => ({
    id: cat.id,
    name: cat.name,
    icon: cat.icon,
    color: cat.color,
    description: `${cat.name} recipes`
  })),
  loading: { isLoading: false },
  error: { hasError: false }
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: { isLoading: false } };
    case 'CLEAR_ERROR':
      return { ...state, error: { hasError: false } };
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_RECIPES':
      return { ...state, recipes: action.payload };
    case 'ADD_RECIPE':
      return { ...state, recipes: [action.payload, ...state.recipes] };
    case 'UPDATE_RECIPE':
      return {
        ...state,
        recipes: state.recipes.map(recipe => 
          recipe.id === action.payload.id ? action.payload : recipe
        )
      };
    case 'DELETE_RECIPE':
      return {
        ...state,
        recipes: state.recipes.filter(recipe => recipe.id !== action.payload)
      };
    case 'SET_CATEGORIES':
      return { ...state, categories: action.payload };
    default:
      return state;
  }
}

// Context
const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider component
interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Auth state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      if (firebaseUser) {
        try {
          // Get or create user profile
          const profileResponse = await apiService.getUserProfile();
          if (profileResponse.data) {
            dispatch({ type: 'SET_USER', payload: profileResponse.data });
          }
        } catch (error) {
          console.error('Error fetching user profile:', error);
          // Set basic user info from Firebase
          const basicUser: User = {
            uid: firebaseUser.uid,
            email: firebaseUser.email || '',
            displayName: firebaseUser.displayName || '',
            photoURL: firebaseUser.photoURL || undefined,
            recipeCount: 0,
            createdAt: new Date(),
            preferences: {
              defaultCategory: 'Main Course',
              aiAutoExtract: true,
              publicRecipes: false
            }
          };
          dispatch({ type: 'SET_USER', payload: basicUser });
        }
      } else {
        dispatch({ type: 'SET_USER', payload: null });
        dispatch({ type: 'SET_RECIPES', payload: [] });
      }
    });

    return () => unsubscribe();
  }, []);

  // Context methods
  const login = async (email: string, password: string): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Signing in...' } });
      await signInWithEmailAndPassword(auth, email, password);
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to sign in'
        } 
      });
      throw error;
    }
  };

  const signup = async (email: string, password: string, displayName: string): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Creating account...' } });
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update profile with display name (using Firebase User methods)
      await result.user.updateProfile({ displayName });
      
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to create account'
        } 
      });
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await signOut(auth);
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to sign out'
        } 
      });
    }
  };

  const createRecipe = async (data: RecipeFormData): Promise<Recipe> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Creating recipe...' } });
      
      const response = await apiService.createRecipe(data);
      const newRecipe = response.data!;
      
      dispatch({ type: 'ADD_RECIPE', payload: newRecipe });
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
      
      return newRecipe;
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to create recipe'
        } 
      });
      throw error;
    }
  };

  const updateRecipe = async (id: string, data: Partial<Recipe>): Promise<Recipe> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Updating recipe...' } });
      
      const response = await apiService.updateRecipe(id, data);
      const updatedRecipe = response.data!;
      
      dispatch({ type: 'UPDATE_RECIPE', payload: updatedRecipe });
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
      
      return updatedRecipe;
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to update recipe'
        } 
      });
      throw error;
    }
  };

  const deleteRecipe = async (id: string): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Deleting recipe...' } });
      
      await apiService.deleteRecipe(id);
      
      dispatch({ type: 'DELETE_RECIPE', payload: id });
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to delete recipe'
        } 
      });
      throw error;
    }
  };

  const fetchRecipes = async (page = 1, limit = 12): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Loading recipes...' } });
      
      const response = await apiService.getRecipes({ page, limit });
      
      dispatch({ type: 'SET_RECIPES', payload: response.items });
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to load recipes'
        } 
      });
    }
  };

  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const contextValue: AppContextType = {
    user: state.user,
    recipes: state.recipes,
    categories: state.categories,
    loading: state.loading,
    error: state.error,
    login,
    signup,
    logout,
    createRecipe,
    updateRecipe,
    deleteRecipe,
    fetchRecipes,
    clearError
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

// Hook to use context
export function useApp(): AppContextType {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export default AppContext;