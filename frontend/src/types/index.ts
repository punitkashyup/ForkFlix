// Recipe Types
export interface Recipe {
  id: string;
  userId: string;
  title: string;
  instagramUrl: string;
  embedCode: string;
  category: RecipeCategory;
  cookingTime: number;
  difficulty: RecipeDifficulty;
  ingredients: string[];
  instructions: string;
  aiExtracted: boolean;
  tags: string[];
  dietaryInfo: DietaryInfo[];
  createdAt: Date;
  updatedAt: Date;
  isPublic: boolean;
  likes: number;
  thumbnailUrl?: string;
}

export type RecipeCategory = 
  | 'Starters' 
  | 'Main Course' 
  | 'Desserts' 
  | 'Beverages' 
  | 'Snacks';

export type RecipeDifficulty = 'Easy' | 'Medium' | 'Hard';

export type DietaryInfo = 
  | 'vegetarian' 
  | 'vegan' 
  | 'gluten-free' 
  | 'dairy-free' 
  | 'nut-free' 
  | 'keto' 
  | 'paleo';

// User Types
export interface User {
  uid: string;
  email: string;
  displayName: string;
  photoURL?: string;
  recipeCount: number;
  createdAt: Date;
  preferences: UserPreferences;
}

export interface UserPreferences {
  defaultCategory: RecipeCategory;
  aiAutoExtract: boolean;
  publicRecipes: boolean;
}

// Category Types
export interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  description: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Form Types
export interface RecipeFormData {
  instagramUrl: string;
  title?: string;
  category?: RecipeCategory;
  isPublic?: boolean;
}

export interface UserProfileFormData {
  displayName: string;
  preferences: UserPreferences;
}

// Instagram Types
export interface InstagramMetadata {
  url: string;
  title: string;
  description: string;
  thumbnailUrl: string;
  embedCode: string;
  authorName: string;
  authorUrl: string;
}

// AI Types
export interface AIAnalysisResult {
  ingredients: string[];
  category: RecipeCategory;
  cookingTime: number;
  difficulty: RecipeDifficulty;
  dietaryInfo: DietaryInfo[];
  tags: string[];
  instructions?: string;
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

// Error Types
export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}

// Context Types
export interface AppContextType {
  user: User | null;
  recipes: Recipe[];
  categories: Category[];
  loading: LoadingState;
  error: ErrorState;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, displayName: string) => Promise<void>;
  logout: () => Promise<void>;
  createRecipe: (data: RecipeFormData) => Promise<Recipe>;
  updateRecipe: (id: string, data: Partial<Recipe>) => Promise<Recipe>;
  deleteRecipe: (id: string) => Promise<void>;
  fetchRecipes: (page?: number, limit?: number) => Promise<void>;
  clearError: () => void;
}