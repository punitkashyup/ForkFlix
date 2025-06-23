import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/constants';
import type { 
  Recipe, 
  RecipeFormData, 
  PaginatedResponse, 
  ApiResponse,
  InstagramMetadata,
  AIAnalysisResult 
} from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    try {
      console.log('🔧 Initializing ApiService...');
      console.log('- API_BASE_URL:', API_BASE_URL);
      console.log('- API_ENDPOINTS:', API_ENDPOINTS);
      console.log('- No static auth import (using dynamic import)');
      
      if (!API_BASE_URL) {
        throw new Error('API_BASE_URL is not defined');
      }
      
      this.client = axios.create({
        baseURL: API_BASE_URL,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      this.setupInterceptors();
      console.log('✅ ApiService initialized successfully');
      console.log('✅ Available methods on this instance:', Object.getOwnPropertyNames(Object.getPrototypeOf(this)));
    } catch (error) {
      console.error('❌ Failed to initialize ApiService:', error);
      console.error('❌ Error details:', error);
      throw error;
    }
  }

  private setupInterceptors() {
    try {
      console.log('🔧 Setting up interceptors...');
      // Request interceptor to add auth token
      this.client.interceptors.request.use(
        async (config) => {
          try {
            // Dynamically import auth to avoid circular dependencies
            const { auth } = await import('../config/firebase');
            const user = auth?.currentUser;
            if (user) {
              const token = await user.getIdToken();
              config.headers.Authorization = `Bearer ${token}`;
            }
          } catch (error) {
            console.warn('Failed to get auth token:', error);
            // Continue without auth token for development
          }
          return config;
        },
        (error) => {
          return Promise.reject(error);
        }
      );
      console.log('✅ Request interceptor set up');
    } catch (error) {
      console.warn('⚠️ Failed to setup request interceptor, continuing without auth:', error);
      // Don't throw - continue without auth interceptor
    }

    // Response interceptor for error handling
    try {
      this.client.interceptors.response.use(
        (response: AxiosResponse) => response,
        async (error: AxiosError) => {
          if (error.response?.status === 401) {
            try {
              // Handle unauthorized - redirect to login
              const { auth } = await import('../config/firebase');
              auth.signOut();
            } catch (importError) {
              console.warn('Failed to import auth for signOut:', importError);
            }
          }
          return Promise.reject(error);
        }
      );
      console.log('✅ Response interceptor set up');
    } catch (error) {
      console.warn('⚠️ Failed to setup response interceptor:', error);
      // Don't throw - continue without response interceptor
    }
  }

  // Recipe API methods
  createRecipe = async (data: RecipeFormData): Promise<ApiResponse<Recipe>> => {
    const response = await this.client.post(API_ENDPOINTS.RECIPES, data);
    return response.data;
  }

  getRecipes = async (params?: {
    page?: number;
    limit?: number;
    category?: string;
    search?: string;
  }): Promise<PaginatedResponse<Recipe>> => {
    const response = await this.client.get(API_ENDPOINTS.RECIPES, { params });
    return response.data;
  }

  getRecipe = async (id: string): Promise<ApiResponse<Recipe>> => {
    const response = await this.client.get(API_ENDPOINTS.RECIPE_BY_ID(id));
    return response.data;
  }

  updateRecipe = async (id: string, data: Partial<Recipe>): Promise<ApiResponse<Recipe>> => {
    const response = await this.client.put(API_ENDPOINTS.RECIPE_BY_ID(id), data);
    return response.data;
  }

  deleteRecipe = async (id: string): Promise<ApiResponse<void>> => {
    const response = await this.client.delete(API_ENDPOINTS.RECIPE_BY_ID(id));
    return response.data;
  }

  reprocessRecipeAI = async (id: string): Promise<ApiResponse<AIAnalysisResult>> => {
    const response = await this.client.post(API_ENDPOINTS.RECIPE_AI_EXTRACT(id));
    return response.data;
  }

  // Instagram API methods
  validateInstagramUrl = async (url: string): Promise<ApiResponse<{
    isValid: boolean;
    message: string;
  }>> => {
    const response = await this.client.post(API_ENDPOINTS.INSTAGRAM_VALIDATE, { url });
    return response.data;
  }

  getInstagramEmbed = async (url: string, maxWidth?: number): Promise<ApiResponse<{
    embedCode: string;
    width: number;
    height: number;
  }>> => {
    const response = await this.client.post(API_ENDPOINTS.INSTAGRAM_EMBED, { 
      url, 
      maxWidth 
    });
    return response.data;
  }

  getInstagramMetadata = async (url: string): Promise<ApiResponse<InstagramMetadata>> => {
    const response = await this.client.get(API_ENDPOINTS.INSTAGRAM_METADATA(url));
    return response.data;
  }

  // AI API methods
  extractRecipeFromInstagram = async (url: string): Promise<ApiResponse<AIAnalysisResult>> => {
    const response = await this.client.post(API_ENDPOINTS.AI_EXTRACT_INGREDIENTS, {
      instagramUrl: url,
      extractIngredients: true,
      categorize: true,
      extractInstructions: true,
    });
    return response.data;
  }

  categorizeRecipe = async (text: string, ingredients: string[]): Promise<ApiResponse<{
    category: string;
    confidence: number;
  }>> => {
    const response = await this.client.post(API_ENDPOINTS.AI_CATEGORIZE, {
      text,
      ingredients,
    });
    return response.data;
  }

  // User API methods
  getUserProfile = async (): Promise<ApiResponse<any>> => {
    const response = await this.client.get(API_ENDPOINTS.USER_PROFILE);
    return response.data;
  }

  updateUserProfile = async (data: any): Promise<ApiResponse<any>> => {
    const response = await this.client.put(API_ENDPOINTS.USER_PROFILE, data);
    return response.data;
  }

  getUserRecipes = async (params?: {
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Recipe>> => {
    const response = await this.client.get(API_ENDPOINTS.USER_RECIPES, { params });
    return response.data;
  }
}

// Factory function to create API service instance
const createApiService = (): ApiService => {
  console.log('🚀 Creating API service instance...');
  const service = new ApiService();
  console.log('✅ API service instance created:', service);
  console.log('🔍 Available methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(service)));
  console.log('🔍 Direct method check - getRecipes:', service.getRecipes);
  console.log('🔍 Direct method check - getUserProfile:', service.getUserProfile);
  return service;
};

// Create service instance
const serviceInstance = createApiService();

// Create a bound API object to ensure methods are properly attached
const apiService = {
  // Recipe methods
  createRecipe: serviceInstance.createRecipe.bind(serviceInstance),
  getRecipes: serviceInstance.getRecipes.bind(serviceInstance),
  getRecipe: serviceInstance.getRecipe.bind(serviceInstance),
  updateRecipe: serviceInstance.updateRecipe.bind(serviceInstance),
  deleteRecipe: serviceInstance.deleteRecipe.bind(serviceInstance),
  reprocessRecipeAI: serviceInstance.reprocessRecipeAI.bind(serviceInstance),

  // Instagram methods
  validateInstagramUrl: serviceInstance.validateInstagramUrl.bind(serviceInstance),
  getInstagramEmbed: serviceInstance.getInstagramEmbed.bind(serviceInstance),
  getInstagramMetadata: serviceInstance.getInstagramMetadata.bind(serviceInstance),

  // AI methods
  extractRecipeFromInstagram: serviceInstance.extractRecipeFromInstagram.bind(serviceInstance),
  categorizeRecipe: serviceInstance.categorizeRecipe.bind(serviceInstance),

  // User methods
  getUserProfile: serviceInstance.getUserProfile.bind(serviceInstance),
  updateUserProfile: serviceInstance.updateUserProfile.bind(serviceInstance),
  getUserRecipes: serviceInstance.getUserRecipes.bind(serviceInstance),
};

console.log('🔧 Created bound API service object:', apiService);
console.log('🔧 Bound getRecipes method:', apiService.getRecipes);
console.log('🔧 Bound getUserProfile method:', apiService.getUserProfile);

// Also export the class for manual instantiation if needed
export { ApiService, createApiService };
export default apiService;