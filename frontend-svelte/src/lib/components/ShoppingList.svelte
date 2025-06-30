<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { shoppingListService } from '$lib/services/shoppingListService.js';
  import Loading from './Loading.svelte';
  import Button from './Button.svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let recipeIds = [];
  export let showGenerateButton = true;
  export let initialShoppingList = null;
  
  // State
  let shoppingList = initialShoppingList;
  let isLoading = false;
  let isGenerating = false;
  let error = null;
  let duplicateError = null;
  
  // Generation options (simplified)
  let listName = '';
  let consolidateDuplicates = true;
  
  onMount(() => {
    if (initialShoppingList) {
      shoppingList = initialShoppingList;
    }
  });
  
  async function generateShoppingList() {
    if (!recipeIds || recipeIds.length === 0) {
      error = 'Please select at least one recipe to generate a shopping list';
      return;
    }
    
    isGenerating = true;
    error = null;
    duplicateError = null;
    
    try {
      const request = {
        recipe_ids: recipeIds,
        list_name: listName || `Shopping List - ${new Date().toLocaleDateString()}`,
        consolidate_duplicates: consolidateDuplicates
      };
      
      console.log('🛒 Generating shopping list with request:', request);
      
      const shoppingListData = await shoppingListService.generateShoppingList(request);
      
      shoppingList = shoppingListData;
      dispatch('listGenerated', { list: shoppingList });
      console.log('✅ Shopping list generated successfully:', shoppingList);
      
    } catch (err) {
      console.error('❌ Error generating shopping list:', err);
      
      // Check if this is a duplicate shopping list error
      if (err.message && err.message.includes('Shopping lists already exist for:')) {
        duplicateError = {
          message: err.message,
          recipes: extractRecipeNamesFromError(err.message)
        };
        // Dispatch event to parent to handle duplicate error
        dispatch('duplicateError', { 
          message: err.message, 
          recipes: duplicateError.recipes 
        });
      } else {
        error = err.message || 'Failed to generate shopping list';
      }
    } finally {
      isGenerating = false;
    }
  }

  function extractRecipeNamesFromError(errorMessage) {
    // Extract recipe names from error message like "Shopping lists already exist for: Recipe Name. Please use..."
    const match = errorMessage.match(/Shopping lists already exist for: ([^.]+)\./);
    if (match) {
      return match[1].split(', ').map(name => name.trim());
    }
    return [];
  }

  function dismissDuplicateError() {
    duplicateError = null;
  }

  function viewExistingLists() {
    dispatch('viewExistingLists');
    duplicateError = null;
  }
  
  function formatQuantity(quantity, unit) {
    if (!quantity) return '';
    if (!unit || unit === 'item') return quantity.toString();
    
    const unitDisplay = {
      cup: 'cup', cups: 'cups',
      tablespoon: 'tbsp', tablespoons: 'tbsp',
      teaspoon: 'tsp', teaspoons: 'tsp',
      pound: 'lb', pounds: 'lbs',
      ounce: 'oz', ounces: 'oz',
      piece: 'pc', pieces: 'pcs',
      gram: 'g', grams: 'g',
      kilogram: 'kg', kilograms: 'kg',
      liter: 'L', liters: 'L',
      milliliter: 'mL', milliliters: 'mL'
    };
    
    const displayUnit = unitDisplay[unit] || unit;
    return `${quantity} ${displayUnit}`.trim();
  }
  
  function getCategoryDisplayName(category) {
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
  
  function getCategoryIcon(category) {
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
  
  // Group items by category
  $: groupedItems = shoppingList?.items ? 
    shoppingList.items.reduce((groups, item) => {
      const category = item.category || 'other';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(item);
      return groups;
    }, {}) : {};
</script>

{#if showGenerateButton && !shoppingList}
  <div class="generator-section">
    <div class="generator-header">
      <h3>Generate Shopping List</h3>
      <p>Create a smart shopping list from your selected recipes</p>
    </div>
    
    {#if error}
      <div class="error-message">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{error}</span>
        <button class="error-close" on:click={() => error = null}>×</button>
      </div>
    {/if}

    {#if duplicateError}
      <div class="duplicate-error-message">
        <div class="duplicate-error-header">
          <span class="duplicate-error-icon">📋</span>
          <h4>Shopping Lists Already Exist</h4>
          <button class="error-close" on:click={dismissDuplicateError}>×</button>
        </div>
        <p class="duplicate-error-text">
          Some of your selected recipes already have shopping lists:
        </p>
        <ul class="duplicate-recipe-list">
          {#each duplicateError.recipes as recipeName}
            <li>• {recipeName}</li>
          {/each}
        </ul>
        <div class="duplicate-error-actions">
          <div class="duplicate-error-buttons">
            <Button
              variant="primary"
              size="sm"
              icon="👀"
              on:click={viewExistingLists}
            >
              View My Shopping Lists
            </Button>
          </div>
          <p class="duplicate-error-suggestion">
            <strong>Other options:</strong>
          </p>
          <ul class="duplicate-action-list">
            <li>Delete existing lists if you want to create a new one</li>
            <li>Select different recipes that don't have shopping lists yet</li>
          </ul>
        </div>
      </div>
    {/if}
    
    <div class="generator-form">
      <div class="form-group">
        <label for="listName">Shopping List Name</label>
        <input
          id="listName"
          type="text"
          bind:value={listName}
          placeholder="e.g., Weekend Meal Prep"
          class="form-input"
        />
      </div>
      
      <div class="form-group">
        <label class="checkbox-label">
          <input
            type="checkbox"
            bind:checked={consolidateDuplicates}
            class="checkbox"
          />
          <span class="checkbox-text">
            Consolidate duplicate ingredients
            <small>Combine similar ingredients (e.g., "2 cups flour" + "1 cup flour" = "3 cups flour")</small>
          </span>
        </label>
      </div>
      
      <Button
        variant="primary"
        size="md"
        fullWidth={true}
        icon="🛒"
        loading={isGenerating}
        on:click={generateShoppingList}
      >
        {isGenerating ? 'Generating...' : 'Generate Shopping List'}
      </Button>
    </div>
  </div>
{:else if shoppingList}
  <div class="shopping-list">
    <div class="list-header">
      <div class="list-title">
        <h3>{shoppingList.name}</h3>
        <div class="list-meta">
          <span class="item-count">{shoppingList.total_items} items</span>
          <span class="recipe-count">from {shoppingList.recipe_ids.length} recipes</span>
        </div>
      </div>
    </div>
    
    {#if Object.keys(groupedItems).length > 0}
      <div class="categories-grid">
        {#each Object.entries(groupedItems) as [category, items]}
          <div class="category-section">
            <div class="category-header">
              <span class="category-icon">{getCategoryIcon(category)}</span>
              <h4 class="category-name">{getCategoryDisplayName(category)}</h4>
              <span class="category-count">({items.length})</span>
            </div>
            
            <div class="items-list">
              {#each items as item}
                <div class="shopping-item">
                  <div class="item-checkbox">
                    <input type="checkbox" class="checkbox" />
                  </div>
                  <div class="item-info">
                    <div class="item-name">{item.name}</div>
                    <div class="item-quantity">
                      {formatQuantity(item.quantity, item.unit)}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="empty-list">
        <div class="empty-icon">📝</div>
        <p>No items in this shopping list</p>
      </div>
    {/if}
  </div>
{/if}

<style>
  /* Generator Section */
  .generator-section {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
  }
  
  .generator-header {
    text-align: center;
    margin-bottom: 24px;
  }
  
  .generator-header h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
  }
  
  .generator-header p {
    color: #6b7280;
    margin: 0;
  }
  
  .error-message {
    background: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .error-icon {
    font-size: 18px;
  }
  
  .error-text {
    flex: 1;
    color: #dc2626;
    font-weight: 500;
  }
  
  .error-close {
    background: none;
    border: none;
    color: #dc2626;
    font-size: 20px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Duplicate Error Styling */
  .duplicate-error-message {
    background: #fffbeb;
    border: 1px solid #f59e0b;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
  }

  .duplicate-error-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }

  .duplicate-error-icon {
    font-size: 24px;
  }

  .duplicate-error-header h4 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #92400e;
    margin: 0;
    flex: 1;
  }

  .duplicate-error-header .error-close {
    color: #92400e;
  }

  .duplicate-error-text {
    color: #92400e;
    margin: 0 0 12px 0;
    font-weight: 500;
  }

  .duplicate-recipe-list {
    background: rgba(245, 158, 11, 0.1);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
    list-style: none;
  }

  .duplicate-recipe-list li {
    color: #92400e;
    font-weight: 500;
    margin: 4px 0;
  }

  .duplicate-error-actions {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(245, 158, 11, 0.2);
  }

  .duplicate-error-buttons {
    margin-bottom: 16px;
    display: flex;
    justify-content: center;
  }

  .duplicate-error-suggestion {
    color: #92400e;
    margin: 0 0 8px 0;
    font-size: 14px;
  }

  .duplicate-action-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .duplicate-action-list li {
    color: #78350f;
    font-size: 14px;
    margin: 6px 0;
    padding-left: 16px;
    position: relative;
  }

  .duplicate-action-list li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: #f59e0b;
    font-weight: bold;
  }
  
  .generator-form {
    max-width: 400px;
    margin: 0 auto;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    font-weight: 500;
    color: #374151;
    margin-bottom: 6px;
  }
  
  .form-input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.2s;
  }
  
  .form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  .checkbox-label {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    cursor: pointer;
  }
  
  .checkbox {
    margin-top: 2px;
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
  
  .checkbox-text {
    flex: 1;
    font-size: 14px;
    color: #374151;
  }
  
  .checkbox-text small {
    display: block;
    color: #6b7280;
    margin-top: 4px;
    font-size: 12px;
  }
  
  
  /* Shopping List */
  .shopping-list {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
  }
  
  .list-header {
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
  }
  
  .list-title h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
  }
  
  .list-meta {
    display: flex;
    gap: 16px;
    font-size: 14px;
    color: #6b7280;
  }
  
  .categories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1px;
    background: #e5e7eb;
  }
  
  .category-section {
    background: white;
    padding: 20px;
  }
  
  .category-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f3f4f6;
  }
  
  .category-icon {
    font-size: 1.2rem;
  }
  
  .category-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
    flex: 1;
  }
  
  .category-count {
    font-size: 0.9rem;
    color: #6b7280;
  }
  
  .items-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .shopping-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 8px 0;
  }
  
  .item-checkbox {
    margin-top: 2px;
  }
  
  .item-info {
    flex: 1;
  }
  
  .item-name {
    font-weight: 500;
    color: #374151;
    margin-bottom: 2px;
  }
  
  .item-quantity {
    font-size: 0.9rem;
    color: #6b7280;
  }
  
  .empty-list {
    text-align: center;
    padding: 60px 20px;
  }
  
  .empty-icon {
    font-size: 3rem;
    margin-bottom: 16px;
  }
  
  .empty-list p {
    color: #6b7280;
    margin: 0;
  }
  
  /* Responsive Design */
  @media (max-width: 768px) {
    .generator-section {
      padding: 16px;
    }
    
    .categories-grid {
      grid-template-columns: 1fr;
    }
    
    .category-section {
      padding: 16px;
    }
    
    .list-header {
      padding: 16px;
    }
    
    .list-meta {
      flex-direction: column;
      gap: 4px;
    }
  }
</style>