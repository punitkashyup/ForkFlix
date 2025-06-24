import { auth } from '$lib/config/firebase.js';
import { PUBLIC_API_URL } from '$env/static/public';

const API_BASE_URL = PUBLIC_API_URL;

class ApiService {
	constructor() {
		this.baseURL = API_BASE_URL;
	}

	async request(endpoint, options = {}) {
		const url = `${this.baseURL}${endpoint}`;
		
		// Get auth token if user is logged in
		let token = null;
		if (auth?.currentUser) {
			try {
				token = await auth.currentUser.getIdToken();
			} catch (error) {
				console.warn('Failed to get auth token:', error);
			}
		}

		const config = {
			headers: {
				'Content-Type': 'application/json',
				...(token && { Authorization: `Bearer ${token}` }),
				...options.headers
			},
			...options
		};

		try {
			const response = await fetch(url, config);
			
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			
			return await response.json();
		} catch (error) {
			console.error('API request failed:', error);
			throw error;
		}
	}

	// Recipe endpoints
	async getRecipes(params = {}) {
		const searchParams = new URLSearchParams(params);
		return this.request(`/api/v1/recipes?${searchParams}`);
	}

	async getRecipe(id) {
		const response = await this.request(`/api/v1/recipes/${id}`);
		return response.data; // Extract recipe from SuccessResponse.data
	}

	async createRecipe(data) {
		return this.request('/api/v1/recipes', {
			method: 'POST',
			body: JSON.stringify(data)
		});
	}

	async updateRecipe(id, data) {
		return this.request(`/api/v1/recipes/${id}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		});
	}

	async deleteRecipe(id) {
		return this.request(`/api/v1/recipes/${id}`, {
			method: 'DELETE'
		});
	}

	// AI endpoints
	async extractRecipeFromInstagram(url) {
		return this.request('/api/v1/ai/extract-ingredients', {
			method: 'POST',
			body: JSON.stringify({
				instagramUrl: url,
				extractIngredients: true,
				categorize: true,
				extractInstructions: true
			})
		});
	}

	// Instagram endpoints
	async validateInstagramUrl(url) {
		return this.request('/api/v1/instagram/validate', {
			method: 'POST',
			body: JSON.stringify({ url })
		});
	}

	async getInstagramEmbed(url, maxWidth = 320) {
		return this.request('/api/v1/instagram/embed', {
			method: 'POST',
			body: JSON.stringify({ url, maxWidth })
		});
	}

	async getInstagramMetadata(url) {
		// Use the full URL as path parameter - FastAPI will handle it with {url:path}
		const cleanUrl = url.startsWith('http') ? url.substring(url.indexOf('://') + 3) : url;
		return this.request(`/api/v1/instagram/metadata/${cleanUrl}`);
	}
}

export const apiService = new ApiService();