import React, { createContext, useContext, useReducer, useEffect, useCallback, ReactNode } from 'react';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  User as FirebaseUser
} from 'firebase/auth';
import { auth } from '../config/firebase';
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
import apiService from '../services/api';

// Debug the imported API service
console.log('🔍 AppContext: Imported apiService:', apiService);
console.log('🔍 AppContext: apiService type:', typeof apiService);
console.log('🔍 AppContext: apiService constructor:', apiService?.constructor?.name);
console.log('🔍 AppContext: apiService methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(apiService || {})));
console.log('🔍 AppContext: Direct access to getRecipes:', apiService?.getRecipes);
console.log('🔍 AppContext: Direct access to getUserProfile:', apiService?.getUserProfile);

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
          // 🔥 TEMPORARY: Console log Firebase ID token for testing
          const idToken = await firebaseUser.getIdToken();
          console.log('🔥 Firebase ID Token (REMOVE IN PRODUCTION):', idToken);
          console.log('🔥 User UID:', firebaseUser.uid);
          console.log('🔥 User Email:', firebaseUser.email);
          console.log('🔥 Use in Swagger: Bearer', idToken);
          
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
        console.log('🔥 User logged out - no token available');
        dispatch({ type: 'SET_USER', payload: null });
        dispatch({ type: 'SET_RECIPES', payload: [] });
      }
    });

    return () => unsubscribe();
  }, []);

  // Context methods
  const login = useCallback(async (email: string, password: string): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Signing in...' } });
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // 🔥 TEMPORARY: Console log Firebase ID token immediately after login
      const idToken = await userCredential.user.getIdToken();
      console.log('🔥 LOGIN SUCCESS - Firebase ID Token:', idToken);
      console.log('🔥 Copy this for Swagger: Bearer', idToken);
      
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
  }, []);

  const signup = async (email: string, password: string, displayName: string): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Creating account...' } });
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update profile with display name using Firebase auth function
      await updateProfile(result.user, { displayName });
      
      // 🔥 TEMPORARY: Console log Firebase ID token after signup
      const idToken = await result.user.getIdToken();
      console.log('🔥 SIGNUP SUCCESS - Firebase ID Token:', idToken);
      console.log('🔥 Copy this for Swagger: Bearer', idToken);
      
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

  const fetchRecipes = useCallback(async (page = 1, limit = 12): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Loading recipes...' } });
      
      console.log('🔍 Debug fetchRecipes:');
      console.log('- apiService:', apiService);
      console.log('- apiService type:', typeof apiService);
      console.log('- apiService is null?', apiService === null);
      console.log('- apiService is undefined?', apiService === undefined);
      
      if (apiService) {
        console.log('- getRecipes method:', apiService.getRecipes);
        console.log('- getRecipes type:', typeof apiService.getRecipes);
        console.log('- apiService constructor:', apiService.constructor?.name);
        console.log('- apiService keys:', Object.keys(apiService));
        console.log('- apiService prototype methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(apiService)));
      }
      
      if (!apiService) {
        console.error('❌ API service is undefined or null');
        throw new Error('API service is undefined or null');
      }
      
      if (typeof apiService.getRecipes !== 'function') {
        console.error('❌ getRecipes is not a function:', typeof apiService.getRecipes);
        throw new Error(`getRecipes method not found. Type: ${typeof apiService.getRecipes}`);
      }
      
      console.log('✅ About to call apiService.getRecipes');
      const response = await apiService.getRecipes({ page, limit });
      console.log('✅ API response received:', response);
      
      dispatch({ type: 'SET_RECIPES', payload: response.items });
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
    } catch (error: any) {
      console.error('❌ fetchRecipes error:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          hasError: true, 
          message: error.message || 'Failed to load recipes'
        } 
      });
    }
  }, []);

  const clearError = useCallback((): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  // 🔥 TEMPORARY: Helper function to get current token (for testing)
  const getCurrentToken = useCallback(async (): Promise<string | null> => {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      console.log('🔥 Current Firebase ID Token:', token);
      console.log('🔥 Use in Swagger: Bearer', token);
      return token;
    }
    console.log('🔥 No user logged in');
    return null;
  }, []);

  // 🔥 TEMPORARY: Expose to window for easy console access
  useEffect(() => {
    (window as any).getFirebaseToken = getCurrentToken;
    console.log('🔥 Helper available: Run getFirebaseToken() in console to get current token');
  }, []); // Remove getCurrentToken dependency to prevent re-renders

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