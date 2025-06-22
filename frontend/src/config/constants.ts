export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Recipe endpoints
  RECIPES: '/api/v1/recipes',
  RECIPE_BY_ID: (id: string) => `/api/v1/recipes/${id}`,
  RECIPE_AI_EXTRACT: (id: string) => `/api/v1/recipes/${id}/ai`,
  
  // Instagram endpoints
  INSTAGRAM_VALIDATE: '/api/v1/instagram/validate',
  INSTAGRAM_EMBED: '/api/v1/instagram/embed',
  INSTAGRAM_METADATA: (url: string) => `/api/v1/instagram/metadata/${encodeURIComponent(url)}`,
  
  // AI endpoints
  AI_EXTRACT_INGREDIENTS: '/api/v1/ai/extract-ingredients',
  AI_CATEGORIZE: '/api/v1/ai/categorize',
  AI_ANALYZE_VIDEO: '/api/v1/ai/analyze-video',
  AI_MODELS: '/api/v1/ai/models',
  
  // Auth endpoints
  AUTH_LOGIN: '/api/v1/auth/login',
  AUTH_LOGOUT: '/api/v1/auth/logout',
  
  // User endpoints
  USER_PROFILE: '/api/v1/users/profile',
  USER_RECIPES: '/api/v1/users/recipes',
} as const;

export const RECIPE_CATEGORIES = [
  { id: 'starters', name: 'Starters', icon: '🥗', color: '#4ade80' },
  { id: 'main-course', name: 'Main Course', icon: '🍽️', color: '#3b82f6' },
  { id: 'desserts', name: 'Desserts', icon: '🍰', color: '#f59e0b' },
  { id: 'beverages', name: 'Beverages', icon: '🥤', color: '#06b6d4' },
  { id: 'snacks', name: 'Snacks', icon: '🍿', color: '#8b5cf6' },
] as const;

export const DIETARY_OPTIONS = [
  'vegetarian',
  'vegan',
  'gluten-free',
  'dairy-free',
  'nut-free',
  'keto',
  'paleo',
] as const;

export const DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard'] as const;

export const PAGINATION = {
  DEFAULT_LIMIT: 12,
  MAX_LIMIT: 50,
} as const;

export const VALIDATION = {
  MIN_RECIPE_TITLE_LENGTH: 3,
  MAX_RECIPE_TITLE_LENGTH: 100,
  MIN_PASSWORD_LENGTH: 6,
  MAX_INGREDIENTS: 50,
} as const;

export const STORAGE_KEYS = {
  USER_PREFERENCES: 'user_preferences',
  CACHED_RECIPES: 'cached_recipes',
  LAST_SYNC: 'last_sync',
} as const;