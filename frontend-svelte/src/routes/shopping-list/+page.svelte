<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { auth } from '$lib/config/firebase.js';
  import { user, authInitialized } from '$lib/stores/auth.js';
  import { apiService } from '$lib/services/api.js';
  import { shoppingListService } from '$lib/services/shoppingListService.js';
  import ShoppingList from '$lib/components/ShoppingList.svelte';
  import Loading from '$lib/components/Loading.svelte';
  import Button from '$lib/components/Button.svelte';
  
  let recipes = [];
  let selectedRecipeIds = [];
  let isLoading = true;
  let loadingRecipes = false;
  let error = null;
  let activeTab = 'create'; // 'create', 'my-lists'
  let myShoppingLists = [];
  let loadingLists = false;
  
  // Redirect to login if not authenticated
  $: if (!$user && $authInitialized) {
    goto('/login');
  }
  
  onMount(async () => {
    // Check for pre-selected recipes from URL params
    const urlParams = new URLSearchParams($page.url.search);
    const preSelectedRecipes = urlParams.getAll('recipe');
    if (preSelectedRecipes.length > 0) {
      selectedRecipeIds = preSelectedRecipes;
    }
    
    if ($user) {
      await loadUserRecipes();
    }
    isLoading = false;
  });
  
  async function loadUserRecipes() {
    if (!$user) return;
    
    loadingRecipes = true;
    error = null;
    
    try {
      console.log('🔍 Loading recipes for user:', $user.uid);
      
      const response = await apiService.getRecipes({ limit: 50 });
      console.log('✅ Recipes API response:', response);
      if (response.items) {
        recipes = response.items || [];
        console.log('✅ Loaded recipes:', recipes.length);
      } else {
        throw new Error('Failed to load recipes');
      }
    } catch (err) {
      console.error('❌ Error loading recipes:', err);
      error = 'Failed to load your recipes. Please try again.';
    } finally {
      loadingRecipes = false;
    }
  }
  
  async function loadMyShoppingLists() {
    if (!$user) return;
    
    loadingLists = true;
    
    try {
      console.log('🔍 Loading shopping lists for user:', $user.uid);
      
      const response = await shoppingListService.getShoppingLists({ limit: 20 });
      console.log('✅ Shopping lists response:', response);
      myShoppingLists = response.items || [];
    } catch (err) {
      console.error('❌ Error loading shopping lists:', err);
      error = `Failed to load shopping lists: ${err.message}`;
    } finally {
      loadingLists = false;
    }
  }
  
  function toggleRecipeSelection(recipeId) {
    if (selectedRecipeIds.includes(recipeId)) {
      selectedRecipeIds = selectedRecipeIds.filter(id => id !== recipeId);
    } else {
      selectedRecipeIds = [...selectedRecipeIds, recipeId];
    }
  }
  
  function selectAllRecipes() {
    selectedRecipeIds = recipes.map(recipe => recipe.id);
  }
  
  function clearSelection() {
    selectedRecipeIds = [];
  }
  
  function handleListGenerated(event) {
    console.log('Shopping list generated:', event.detail.list);
    // Show success message or redirect
    activeTab = 'my-lists';
    loadMyShoppingLists();
  }
  
  function handleTabChange(tab) {
    activeTab = tab;
    if (tab === 'my-lists' && myShoppingLists.length === 0) {
      loadMyShoppingLists();
    }
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
  }
  
  function goBack() {
    goto('/');
  }
</script>

<svelte:head>
  <title>Smart Shopping Lists - ForkFlix</title>
  <meta name="description" content="Generate intelligent shopping lists from your saved recipes." />
</svelte:head>

{#if isLoading}
  <div class="loading-container">
    <Loading size="lg" message="Loading shopping lists..." />
  </div>
{:else}
  <div class="shopping-list-page">
    <!-- Header with Back Button -->
    <div class="page-header">
      <div class="header-top">
        <Button
          variant="ghost"
          icon="←"
          on:click={goBack}
        >
          Back to Recipes
        </Button>
      </div>
      
      <div class="header-content">
        <h1>🛒 Smart Shopping Lists</h1>
        <p class="page-description">
          Generate optimized shopping lists from your saved recipes with smart ingredient consolidation.
        </p>
      </div>
    </div>
    
    <!-- Tab Navigation -->
    <div class="tab-navigation">
      <button 
        class="tab-button" 
        class:active={activeTab === 'create'}
        on:click={() => handleTabChange('create')}
      >
        Create New List
      </button>
      <button 
        class="tab-button" 
        class:active={activeTab === 'my-lists'}
        on:click={() => handleTabChange('my-lists')}
      >
        My Shopping Lists
      </button>
    </div>
    
    {#if activeTab === 'create'}
      <!-- Create New Shopping List Tab -->
      <div class="create-list-section">
        {#if error}
          <div class="error-message">
            <span class="error-icon">⚠️</span>
            <span class="error-text">{error}</span>
            <button class="error-close" on:click={() => error = null}>×</button>
          </div>
        {/if}
        
        {#if loadingRecipes}
          <div class="loading-section">
            <Loading size="md" message="Loading your recipes..." />
          </div>
        {:else if recipes.length === 0}
          <div class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>No Recipes Found</h3>
            <p>You need to save some recipes first before creating shopping lists. Start by adding recipes from Instagram, YouTube, or manually enter your favorites!</p>
            <div class="empty-actions">
              <button 
                class="btn-primary"
                on:click={() => goto('/add-recipe')}
              >
                🍳 Add Your First Recipe
              </button>
              <button 
                class="btn-outline"
                on:click={() => goto('/')}
              >
                🏠 Browse All Recipes
              </button>
            </div>
          </div>
        {:else}
          <!-- Recipe Selection -->
          <div class="recipe-selection">
            <div class="selection-header">
              <h2>Select Recipes for Shopping List</h2>
              <div class="selection-actions">
                <span class="selection-count">{selectedRecipeIds.length} of {recipes.length} selected</span>
                <Button variant="ghost" size="sm" on:click={selectAllRecipes}>Select All</Button>
                <Button variant="ghost" size="sm" on:click={clearSelection}>Clear</Button>
              </div>
            </div>
            
            <div class="recipes-grid">
              {#each recipes as recipe}
                <div 
                  class="recipe-card"
                  class:selected={selectedRecipeIds.includes(recipe.id)}
                  on:click={() => toggleRecipeSelection(recipe.id)}
                  role="button"
                  tabindex="0"
                  on:keydown={(e) => e.key === 'Enter' && toggleRecipeSelection(recipe.id)}
                >
                  <div class="recipe-checkbox">
                    <input 
                      type="checkbox" 
                      checked={selectedRecipeIds.includes(recipe.id)}
                      on:change={() => toggleRecipeSelection(recipe.id)}
                    />
                  </div>
                  
                  {#if recipe.thumbnailUrl}
                    <img 
                      src={recipe.thumbnailUrl} 
                      alt={recipe.title}
                      class="recipe-thumbnail"
                    />
                  {:else}
                    <div class="recipe-placeholder">🍳</div>
                  {/if}
                  
                  <div class="recipe-info">
                    <h3 class="recipe-title">{recipe.title}</h3>
                    <div class="recipe-meta">
                      <span class="recipe-category">{recipe.category}</span>
                      <span class="recipe-time">{recipe.cookingTime}min</span>
                      <span class="recipe-ingredients">{recipe.ingredients?.length || 0} ingredients</span>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Shopping List Generator -->
          {#if selectedRecipeIds.length > 0}
            <div class="list-generator">
              <ShoppingList 
                recipeIds={selectedRecipeIds}
                showGenerateButton={true}
                on:listGenerated={handleListGenerated}
              />
            </div>
          {:else}
            <div class="selection-prompt">
              <h3>👆 Select recipes above to generate your shopping list</h3>
              <p>Choose one or more recipes to create an optimized shopping list with smart ingredient consolidation.</p>
              <div class="selection-benefits">
                <div class="benefit-item">
                  <span class="benefit-icon">🔄</span>
                  <span>Consolidates duplicate ingredients</span>
                </div>
                <div class="benefit-item">
                  <span class="benefit-icon">📝</span>
                  <span>Organized by categories</span>
                </div>
                <div class="benefit-item">
                  <span class="benefit-icon">✅</span>
                  <span>Easy to check off items</span>
                </div>
              </div>
            </div>
          {/if}
        {/if}
      </div>
    
    {:else if activeTab === 'my-lists'}
      <!-- My Shopping Lists Tab -->
      <div class="my-lists-section">
        {#if loadingLists}
          <div class="loading-section">
            <Loading size="md" message="Loading your shopping lists..." />
          </div>
        {:else if myShoppingLists.length === 0}
          <div class="empty-state">
            <div class="empty-icon">🛒</div>
            <h3>No Shopping Lists Yet</h3>
            <p>Create your first shopping list from your saved recipes. Smart lists help you save time by consolidating ingredients!</p>
            <div class="empty-actions">
              <button 
                class="btn-primary"
                on:click={() => handleTabChange('create')}
              >
                🛒 Create Shopping List
              </button>
              <button 
                class="btn-outline"
                on:click={() => goto('/')}
              >
                📋 Browse Recipes
              </button>
            </div>
          </div>
        {:else}
          <div class="lists-grid">
            {#each myShoppingLists as list}
              <div class="list-card">
                <div class="list-header">
                  <h3 class="list-name">{list.name}</h3>
                  <span class="list-status" class:completed={list.status === 'completed'}>
                    {list.status}
                  </span>
                </div>
                
                <div class="list-stats">
                  <div class="stat">
                    <span class="stat-value">{list.total_items}</span>
                    <span class="stat-label">items</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{list.checked_items}</span>
                    <span class="stat-label">completed</span>
                  </div>
                </div>
                
                <div class="list-meta">
                  <span class="list-date">Created {formatDate(list.created_at)}</span>
                  <span class="list-recipes">{list.recipe_ids.length} recipes</span>
                </div>
                
                <div class="list-actions">
                  <Button variant="secondary" size="sm">View List</Button>
                  <Button variant="outline" size="sm">Edit</Button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>
{/if}

<style>
  .shopping-list-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 16px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    min-height: 100vh;
  }
  
  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }
  
  /* Header */
  .page-header {
    margin-bottom: 24px;
  }
  
  .header-top {
    margin-bottom: 16px;
  }
  
  .back-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: transparent;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    color: #6b7280;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
  }
  
  .back-button:hover {
    background: #f9fafb;
    border-color: #3b82f6;
    color: #3b82f6;
  }
  
  .header-content {
    text-align: center;
  }
  
  .page-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 12px 0;
  }
  
  .page-description {
    font-size: 1.1rem;
    color: #6b7280;
    max-width: 600px;
    margin: 0 auto;
  }
  
  /* Tab Navigation */
  .tab-navigation {
    display: flex;
    border-bottom: 2px solid #e5e7eb;
    margin-bottom: 24px;
    gap: 8px;
  }
  
  .tab-button {
    padding: 12px 24px;
    background: none;
    border: none;
    font-size: 16px;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
  }
  
  .tab-button:hover {
    color: #3b82f6;
  }
  
  .tab-button.active {
    color: #3b82f6;
    border-bottom-color: #3b82f6;
  }
  
  /* Error Message */
  .error-message {
    background: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
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
  
  /* Loading Section */
  .loading-section {
    display: flex;
    justify-content: center;
    padding: 60px 0;
  }
  
  /* Empty State */
  .empty-state {
    text-align: center;
    padding: 60px 20px;
  }
  
  .empty-icon {
    font-size: 4rem;
    margin-bottom: 16px;
  }
  
  .empty-state h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
  }
  
  .empty-state p {
    color: #6b7280;
    margin: 0 0 24px 0;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
  }
  
  .empty-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  /* Recipe Selection */
  .recipe-selection {
    margin-bottom: 32px;
  }
  
  .selection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .selection-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
  }
  
  .selection-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .selection-count {
    font-size: 0.9rem;
    color: #6b7280;
  }
  
  .btn-link {
    background: none;
    border: none;
    color: #3b82f6;
    font-size: 0.9rem;
    cursor: pointer;
    text-decoration: underline;
  }
  
  .btn-link:hover {
    color: #2563eb;
  }
  
  /* Recipes Grid */
  .recipes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
  }
  
  .recipe-card {
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    background: white;
    position: relative;
  }
  
  .recipe-card:hover {
    border-color: #3b82f6;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .recipe-card.selected {
    border-color: #3b82f6;
    background: #f0f9ff;
  }
  
  .recipe-checkbox {
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 1;
  }
  
  .recipe-checkbox input {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
  
  .recipe-thumbnail {
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 12px;
  }
  
  .recipe-placeholder {
    width: 100%;
    height: 120px;
    background: #f3f4f6;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin-bottom: 12px;
  }
  
  .recipe-info {
    padding-right: 32px;
  }
  
  .recipe-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
    line-height: 1.3;
  }
  
  .recipe-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 0.8rem;
    color: #6b7280;
  }
  
  .recipe-category,
  .recipe-time,
  .recipe-ingredients {
    background: #f3f4f6;
    padding: 2px 8px;
    border-radius: 12px;
  }
  
  /* Selection Prompt */
  .selection-prompt {
    text-align: center;
    padding: 40px 20px;
    background: #f9fafb;
    border-radius: 12px;
    margin-top: 24px;
  }
  
  .selection-prompt h3 {
    font-size: 1.3rem;
    color: #374151;
    margin: 0 0 8px 0;
  }
  
  .selection-prompt p {
    color: #6b7280;
    margin: 0 0 20px 0;
  }
  
  .selection-benefits {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
  }
  
  .benefit-item {
    display: flex;
    align-items: center;
    gap: 8px;
    background: white;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    font-size: 0.9rem;
    color: #374151;
  }
  
  .benefit-icon {
    font-size: 1.2rem;
  }
  
  /* List Generator */
  .list-generator {
    margin-top: 32px;
    padding-top: 32px;
    border-top: 2px solid #e5e7eb;
  }
  
  /* My Lists Section */
  .lists-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  .list-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s ease;
  }
  
  .list-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .list-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
  }
  
  .list-status {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    background: #f3f4f6;
    color: #6b7280;
    text-transform: capitalize;
  }
  
  .list-status.completed {
    background: #dcfce7;
    color: #166534;
  }
  
  .list-stats {
    display: flex;
    gap: 20px;
    margin-bottom: 16px;
  }
  
  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .stat-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
  }
  
  .stat-label {
    font-size: 0.8rem;
    color: #6b7280;
  }
  
  .list-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 16px;
  }
  
  .list-actions {
    display: flex;
    gap: 8px;
  }
  
  /* Buttons */
  .btn-primary, .btn-secondary, .btn-outline {
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    font-size: 14px;
  }
  
  .btn-primary {
    background: #3b82f6;
    color: white;
  }
  
  .btn-primary:hover {
    background: #2563eb;
  }
  
  .btn-secondary {
    background: #10b981;
    color: white;
  }
  
  .btn-secondary:hover {
    background: #059669;
  }
  
  .btn-outline {
    background: transparent;
    color: #6b7280;
    border: 1px solid #e5e7eb;
  }
  
  .btn-outline:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }
  
  /* Responsive Design */
  @media (max-width: 768px) {
    .shopping-list-page {
      padding: 12px;
    }
    
    .page-header h1 {
      font-size: 2rem;
    }
    
    .selection-header {
      flex-direction: column;
      align-items: stretch;
    }
    
    .selection-actions {
      justify-content: space-between;
    }
    
    .recipes-grid {
      grid-template-columns: 1fr;
    }
    
    .lists-grid {
      grid-template-columns: 1fr;
    }
    
    .list-stats {
      gap: 12px;
    }
    
    .list-actions {
      flex-direction: column;
    }
  }
</style>