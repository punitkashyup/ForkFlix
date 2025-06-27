import { apiService } from './api.js';

class ShoppingListService {
    constructor() {
        this.baseEndpoint = '/api/v1/shopping-lists';
    }

    // Use the main API service for all requests to ensure proper auth headers
    async _request(endpoint, options = {}) {
        return apiService.request(endpoint, options);
    }

    /**
     * Generate a smart shopping list from multiple recipes
     * @param {Object} request - Generation request parameters
     * @returns {Promise<Object>} Generated shopping list
     */
    async generateShoppingList(request) {
        try {
            console.log('🛒 Generating shopping list with request:', request);
            
            const response = await this._request(`${this.baseEndpoint}/generate`, {
                method: 'POST',
                body: JSON.stringify(request)
            });
            
            if (response.success) {
                console.log('✅ Shopping list generated successfully:', response.data);
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to generate shopping list');
            }
        } catch (error) {
            console.error('❌ Error generating shopping list:', error);
            throw error;
        }
    }

    /**
     * Get all shopping lists for the current user
     * @param {Object} params - Query parameters (page, limit, status_filter)
     * @returns {Promise<Object>} Paginated shopping lists
     */
    async getShoppingLists(params = {}) {
        try {
            const searchParams = new URLSearchParams(params);
            const endpoint = `${this.baseEndpoint}?${searchParams}`;
            console.log('🔍 Shopping List Service: Making request to:', endpoint);
            
            const response = await this._request(endpoint);
            console.log('🔍 Shopping List Service: Raw response:', response);
            
            if (response.success) {
                console.log('✅ Shopping List Service: Success response data:', response.data);
                return response.data;
            } else {
                console.error('❌ Shopping List Service: API returned error:', response);
                throw new Error(response.message || 'Failed to fetch shopping lists');
            }
        } catch (error) {
            console.error('❌ Shopping List Service: Error fetching shopping lists:', error);
            throw error;
        }
    }

    /**
     * Get a specific shopping list by ID
     * @param {string} listId - Shopping list ID
     * @returns {Promise<Object>} Shopping list data
     */
    async getShoppingList(listId) {
        try {
            const response = await this._request(`${this.baseEndpoint}/${listId}`);
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to fetch shopping list');
            }
        } catch (error) {
            console.error('❌ Error fetching shopping list:', error);
            throw error;
        }
    }

    /**
     * Update a shopping list
     * @param {string} listId - Shopping list ID
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object>} Updated shopping list
     */
    async updateShoppingList(listId, updateData) {
        try {
            const response = await this._request(`${this.baseEndpoint}/${listId}`, {
                method: 'PUT',
                body: JSON.stringify(updateData)
            });
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to update shopping list');
            }
        } catch (error) {
            console.error('❌ Error updating shopping list:', error);
            throw error;
        }
    }

    /**
     * Delete a shopping list
     * @param {string} listId - Shopping list ID
     * @returns {Promise<Object>} Deletion result
     */
    async deleteShoppingList(listId) {
        try {
            const response = await this._request(`${this.baseEndpoint}/${listId}`, {
                method: 'DELETE'
            });
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to delete shopping list');
            }
        } catch (error) {
            console.error('❌ Error deleting shopping list:', error);
            throw error;
        }
    }

    /**
     * Optimize a shopping list for cost and time efficiency
     * @param {string} listId - Shopping list ID
     * @param {Object} optimizationOptions - Optimization preferences
     * @returns {Promise<Object>} Optimization results
     */
    async optimizeShoppingList(listId, optimizationOptions = {}) {
        try {
            const request = {
                shopping_list_id: listId,
                budget_priority: false,
                time_priority: true,
                include_bulk_recommendations: true,
                ...optimizationOptions
            };
            
            console.log('🔧 Optimizing shopping list:', request);
            
            const response = await this._request(`${this.baseEndpoint}/${listId}/optimize`, {
                method: 'POST',
                body: JSON.stringify(request)
            });
            
            if (response.success) {
                console.log('✅ Shopping list optimized successfully:', response.data);
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to optimize shopping list');
            }
        } catch (error) {
            console.error('❌ Error optimizing shopping list:', error);
            throw error;
        }
    }

    /**
     * Add an item to a shopping list
     * @param {string} listId - Shopping list ID
     * @param {Object} item - Item to add
     * @returns {Promise<Object>} Result
     */
    async addItemToList(listId, item) {
        try {
            const response = await this._request(`${this.baseEndpoint}/${listId}/items`, {
                method: 'POST',
                body: JSON.stringify(item)
            });
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to add item to shopping list');
            }
        } catch (error) {
            console.error('❌ Error adding item to shopping list:', error);
            throw error;
        }
    }

    /**
     * Update an item in a shopping list
     * @param {string} listId - Shopping list ID
     * @param {number} itemIndex - Item index
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object>} Result
     */
    async updateListItem(listId, itemIndex, updateData) {
        try {
            const response = await this._request(`${this.baseEndpoint}/${listId}/items/${itemIndex}`, {
                method: 'PUT',
                body: JSON.stringify(updateData)
            });
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to update item');
            }
        } catch (error) {
            console.error('❌ Error updating item:', error);
            throw error;
        }
    }

    /**
     * Remove an item from a shopping list
     * @param {string} listId - Shopping list ID
     * @param {number} itemIndex - Item index
     * @returns {Promise<Object>} Result
     */
    async removeItemFromList(listId, itemIndex) {
        try {
            const response = await this._request(`${this.baseEndpoint}/${listId}/items/${itemIndex}`, {
                method: 'DELETE'
            });
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to remove item');
            }
        } catch (error) {
            console.error('❌ Error removing item:', error);
            throw error;
        }
    }

    /**
     * Process ingredients with NLP for smart extraction
     * @param {Array<string>} ingredients - Raw ingredient strings
     * @param {string} recipeId - Optional recipe ID for context
     * @param {Array<string>} dietaryRestrictions - Dietary restrictions
     * @returns {Promise<Object>} Processed ingredients
     */
    async processIngredients(ingredients, recipeId = null, dietaryRestrictions = []) {
        try {
            const request = {
                ingredients,
                recipe_id: recipeId,
                dietary_restrictions: dietaryRestrictions
            };
            
            console.log('🔍 Processing ingredients:', request);
            
            const response = await this._request(`${this.baseEndpoint}/ingredients/process`, {
                method: 'POST',
                body: JSON.stringify(request)
            });
            
            if (response.success) {
                console.log('✅ Ingredients processed successfully:', response.data);
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to process ingredients');
            }
        } catch (error) {
            console.error('❌ Error processing ingredients:', error);
            throw error;
        }
    }


    /**
     * Get shopping list statistics
     * @returns {Promise<Object>} Statistics
     */
    async getShoppingListStats() {
        try {
            const response = await this._request(`${this.baseEndpoint}/stats`);
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.message || 'Failed to fetch statistics');
            }
        } catch (error) {
            console.error('❌ Error fetching statistics:', error);
            throw error;
        }
    }

    /**
     * Generate shopping list from selected recipes (convenience method)
     * @param {Array<string>} recipeIds - Recipe IDs to include
     * @param {Object} options - Generation options
     * @returns {Promise<Object>} Generated shopping list
     */
    async generateFromRecipes(recipeIds, options = {}) {
        const request = {
            recipe_ids: recipeIds,
            list_name: options.listName || `Shopping List - ${new Date().toLocaleDateString()}`,
            consolidate_duplicates: options.consolidateDuplicates ?? true
        };

        return this.generateShoppingList(request);
    }

    /**
     * Toggle item checked status (convenience method)
     * @param {string} listId - Shopping list ID
     * @param {number} itemIndex - Item index
     * @param {boolean} isChecked - New checked state
     * @returns {Promise<Object>} Result
     */
    async toggleItemChecked(listId, itemIndex, isChecked) {
        return this.updateListItem(listId, itemIndex, { is_checked: isChecked });
    }

    /**
     * Complete a shopping list (mark as completed)
     * @param {string} listId - Shopping list ID
     * @returns {Promise<Object>} Updated shopping list
     */
    async completeShoppingList(listId) {
        return this.updateShoppingList(listId, { 
            status: 'completed',
            completed_at: new Date().toISOString()
        });
    }

    /**
     * Archive a shopping list
     * @param {string} listId - Shopping list ID
     * @returns {Promise<Object>} Updated shopping list
     */
    async archiveShoppingList(listId) {
        return this.updateShoppingList(listId, { 
            status: 'archived'
        });
    }

    /**
     * Utility method to format quantity with unit
     * @param {number} quantity - Quantity value
     * @param {string} unit - Unit type
     * @returns {string} Formatted quantity string
     */
    formatQuantity(quantity, unit) {
        if (!quantity) return '';
        if (!unit) return quantity.toString();
        
        const unitDisplay = {
            cup: 'cup', cups: 'cups',
            tablespoon: 'tbsp', tablespoons: 'tbsp',
            teaspoon: 'tsp', teaspoons: 'tsp',
            pound: 'lb', pounds: 'lbs',
            ounce: 'oz', ounces: 'oz',
            piece: 'pc', pieces: 'pcs',
            item: '', items: '',
            gram: 'g', grams: 'g',
            kilogram: 'kg', kilograms: 'kg',
            liter: 'L', liters: 'L',
            milliliter: 'mL', milliliters: 'mL'
        };
        
        const displayUnit = unitDisplay[unit] || unit;
        return `${quantity} ${displayUnit}`.trim();
    }

    /**
     * Get category display name
     * @param {string} category - Category key
     * @returns {string} Display name
     */
    getCategoryDisplayName(category) {
        const names = {
            produce: 'Produce',
            meat_seafood: 'Meat & Seafood',
            dairy_eggs: 'Dairy & Eggs',
            pantry: 'Pantry',
            frozen: 'Frozen',
            bakery: 'Bakery',
            beverages: 'Beverages',
            snacks: 'Snacks',
            household: 'Household',
            other: 'Other'
        };
        return names[category] || 'Other';
    }

    /**
     * Get category icon
     * @param {string} category - Category key
     * @returns {string} Icon emoji
     */
    getCategoryIcon(category) {
        const icons = {
            produce: '🥬',
            meat_seafood: '🥩',
            dairy_eggs: '🥛',
            pantry: '🥫',
            frozen: '🧊',
            bakery: '🍞',
            beverages: '🥤',
            snacks: '🍿',
            household: '🧽',
            other: '📦'
        };
        return icons[category] || '📦';
    }
}

// Export singleton instance
export const shoppingListService = new ShoppingListService();