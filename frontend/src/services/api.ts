import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { auth } from '../config/firebase';
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
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const user = auth.currentUser;
        if (user) {
          const token = await user.getIdToken();
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          auth.signOut();
        }
        return Promise.reject(error);
      }
    );
  }

  // Recipe API methods
  async createRecipe(data: RecipeFormData): Promise<ApiResponse<Recipe>> {
    const response = await this.client.post(API_ENDPOINTS.RECIPES, data);
    return response.data;
  }

  async getRecipes(params?: {
    page?: number;
    limit?: number;
    category?: string;
    search?: string;
  }): Promise<PaginatedResponse<Recipe>> {
    const response = await this.client.get(API_ENDPOINTS.RECIPES, { params });
    return response.data;
  }

  async getRecipe(id: string): Promise<ApiResponse<Recipe>> {
    const response = await this.client.get(API_ENDPOINTS.RECIPE_BY_ID(id));
    return response.data;
  }

  async updateRecipe(id: string, data: Partial<Recipe>): Promise<ApiResponse<Recipe>> {
    const response = await this.client.put(API_ENDPOINTS.RECIPE_BY_ID(id), data);
    return response.data;
  }

  async deleteRecipe(id: string): Promise<ApiResponse<void>> {
    const response = await this.client.delete(API_ENDPOINTS.RECIPE_BY_ID(id));
    return response.data;
  }

  async reprocessRecipeAI(id: string): Promise<ApiResponse<AIAnalysisResult>> {
    const response = await this.client.post(API_ENDPOINTS.RECIPE_AI_EXTRACT(id));
    return response.data;
  }

  // Instagram API methods
  async validateInstagramUrl(url: string): Promise<ApiResponse<{
    isValid: boolean;
    message: string;
  }>> {
    const response = await this.client.post(API_ENDPOINTS.INSTAGRAM_VALIDATE, { url });
    return response.data;
  }

  async getInstagramEmbed(url: string, maxWidth?: number): Promise<ApiResponse<{
    embedCode: string;
    width: number;
    height: number;
  }>> {
    const response = await this.client.post(API_ENDPOINTS.INSTAGRAM_EMBED, { 
      url, 
      maxWidth 
    });
    return response.data;
  }

  async getInstagramMetadata(url: string): Promise<ApiResponse<InstagramMetadata>> {
    const response = await this.client.get(API_ENDPOINTS.INSTAGRAM_METADATA(url));
    return response.data;
  }

  // AI API methods
  async extractRecipeFromInstagram(url: string): Promise<ApiResponse<AIAnalysisResult>> {
    const response = await this.client.post(API_ENDPOINTS.AI_EXTRACT_INGREDIENTS, {
      instagramUrl: url,
      extractIngredients: true,
      categorize: true,
      extractInstructions: true,
    });
    return response.data;
  }

  async categorizeRecipe(text: string, ingredients: string[]): Promise<ApiResponse<{
    category: string;
    confidence: number;
  }>> {
    const response = await this.client.post(API_ENDPOINTS.AI_CATEGORIZE, {
      text,
      ingredients,
    });
    return response.data;
  }

  // User API methods
  async getUserProfile(): Promise<ApiResponse<any>> {
    const response = await this.client.get(API_ENDPOINTS.USER_PROFILE);
    return response.data;
  }

  async updateUserProfile(data: any): Promise<ApiResponse<any>> {
    const response = await this.client.put(API_ENDPOINTS.USER_PROFILE, data);
    return response.data;
  }

  async getUserRecipes(params?: {
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Recipe>> {
    const response = await this.client.get(API_ENDPOINTS.USER_RECIPES, { params });
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;