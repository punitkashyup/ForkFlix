<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { user, authInitialized } from '$lib/stores/auth.js';
  import { shoppingListService } from '$lib/services/shoppingListService.js';
  import Loading from '$lib/components/Loading.svelte';
  import Button from '$lib/components/Button.svelte';
  import Modal from '$lib/components/Modal.svelte';

  let shoppingList = null;
  let isLoading = true;
  let error = null;
  let isUpdating = false;
  let showDeleteModal = false;
  let isDeleting = false;

  // Get shopping list ID from URL
  $: listId = $page.params.id;

  // Redirect to login if not authenticated
  $: if (!$user && $authInitialized) {
    goto('/login');
  }

  onMount(async () => {
    if ($user && listId) {
      await loadShoppingList();
    }
    isLoading = false;
  });

  async function loadShoppingList() {
    try {
      console.log('🔍 Loading shopping list:', listId);
      shoppingList = await shoppingListService.getShoppingList(listId);
      console.log('✅ Shopping list loaded:', shoppingList);
    } catch (err) {
      console.error('❌ Error loading shopping list:', err);
      error = err.message || 'Failed to load shopping list';
    }
  }

  async function toggleItemChecked(itemIndex, currentChecked) {
    if (!shoppingList || isUpdating) return;
    
    try {
      isUpdating = true;
      const newChecked = !currentChecked;
      
      // Update locally for immediate feedback
      shoppingList.items[itemIndex].is_checked = newChecked;
      shoppingList.checked_items = shoppingList.items.filter(item => item.is_checked).length;
      
      // Update on server
      await shoppingListService.updateListItem(listId, itemIndex, { is_checked: newChecked });
      
      console.log(`✅ Item ${itemIndex} marked as ${newChecked ? 'checked' : 'unchecked'}`);
    } catch (err) {
      console.error('❌ Error updating item:', err);
      // Revert local change on error
      shoppingList.items[itemIndex].is_checked = currentChecked;
      shoppingList.checked_items = shoppingList.items.filter(item => item.is_checked).length;
      error = 'Failed to update item';
    } finally {
      isUpdating = false;
    }
  }

  async function completeShoppingList() {
    if (!shoppingList || isUpdating) return;
    
    try {
      isUpdating = true;
      await shoppingListService.completeShoppingList(listId);
      shoppingList.status = 'completed';
      console.log('✅ Shopping list completed');
    } catch (err) {
      console.error('❌ Error completing shopping list:', err);
      error = 'Failed to complete shopping list';
    } finally {
      isUpdating = false;
    }
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

  function goBack() {
    goto('/shopping-list');
  }

  function handleDeleteShoppingList() {
    showDeleteModal = true;
  }

  async function confirmDeleteShoppingList() {
    if (!shoppingList || isDeleting) return;

    try {
      isDeleting = true;
      await shoppingListService.deleteShoppingList(listId);
      console.log('✅ Shopping list deleted successfully');
      goto('/shopping-list');
    } catch (err) {
      console.error('❌ Error deleting shopping list:', err);
      error = `Failed to delete shopping list: ${err.message}`;
      showDeleteModal = false;
    } finally {
      isDeleting = false;
    }
  }

  function cancelDeleteShoppingList() {
    showDeleteModal = false;
  }

  // Group items by category
  $: groupedItems = shoppingList?.items ? 
    shoppingList.items.reduce((groups, item, index) => {
      const category = item.category || 'other';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push({ ...item, index });
      return groups;
    }, {}) : {};

  $: completionPercentage = shoppingList?.total_items > 0 
    ? Math.round((shoppingList.checked_items / shoppingList.total_items) * 100) 
    : 0;
</script>

<svelte:head>
  <title>Shopping List - ForkFlix</title>
  <meta name="description" content="View and manage your shopping list" />
</svelte:head>

{#if isLoading}
  <div class="loading-container">
    <Loading size="lg" message="Loading shopping list..." />
  </div>
{:else if error}
  <div class="error-container">
    <div class="error-card">
      <div class="error-icon">⚠️</div>
      <h2>Error Loading Shopping List</h2>
      <p>{error}</p>
      <div class="error-actions">
        <Button variant="primary" on:click={goBack}>
          ← Back to Shopping Lists
        </Button>
        <Button variant="outline" on:click={() => window.location.reload()}>
          🔄 Retry
        </Button>
      </div>
    </div>
  </div>
{:else if shoppingList}
  <div class="shopping-list-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-top">
        <Button variant="ghost" icon="←" on:click={goBack}>
          Back to Shopping Lists
        </Button>
      </div>
      
      <div class="header-content">
        <h1>{shoppingList.name}</h1>
        <div class="list-meta">
          <span class="meta-item">
            <span class="meta-icon">📝</span>
            {shoppingList.total_items} items
          </span>
          <span class="meta-item">
            <span class="meta-icon">✅</span>
            {shoppingList.checked_items} completed
          </span>
          <span class="meta-item">
            <span class="meta-icon">🍳</span>
            {shoppingList.recipe_ids.length} recipes
          </span>
        </div>
        
        <!-- Progress Bar -->
        <div class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              style="width: {completionPercentage}%"
            ></div>
          </div>
          <span class="progress-text">{completionPercentage}% complete</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="list-actions">
      {#if shoppingList.status !== 'completed'}
        <Button 
          variant="success" 
          icon="✅"
          loading={isUpdating}
          on:click={completeShoppingList}
        >
          Complete Shopping
        </Button>
      {:else}
        <div class="completed-badge">
          <span class="badge-icon">✅</span>
          Completed
        </div>
      {/if}
      
      <Button 
        variant="outline" 
        icon="✏️"
        on:click={() => goto(`/shopping-list/${listId}/edit`)}
      >
        Edit List
      </Button>
      
      <Button 
        variant="danger" 
        icon="🗑️"
        on:click={handleDeleteShoppingList}
      >
        Delete List
      </Button>
    </div>

    <!-- Shopping Items -->
    {#if Object.keys(groupedItems).length > 0}
      <div class="categories-container">
        {#each Object.entries(groupedItems) as [category, items]}
          <div class="category-section">
            <div class="category-header">
              <span class="category-icon">{getCategoryIcon(category)}</span>
              <h3 class="category-name">{getCategoryDisplayName(category)}</h3>
              <span class="category-count">({items.length})</span>
            </div>
            
            <div class="items-list">
              {#each items as item}
                <div 
                  class="shopping-item"
                  class:checked={item.is_checked}
                >
                  <label class="item-checkbox">
                    <input 
                      type="checkbox" 
                      checked={item.is_checked}
                      disabled={isUpdating}
                      on:change={() => toggleItemChecked(item.index, item.is_checked)}
                    />
                    <span class="checkmark"></span>
                  </label>
                  
                  <div class="item-info">
                    <div class="item-name" class:completed={item.is_checked}>
                      {item.name}
                    </div>
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
        <h3>No items in this shopping list</h3>
        <p>This shopping list is empty.</p>
      </div>
    {/if}
  </div>
{:else}
  <div class="error-container">
    <div class="error-card">
      <div class="error-icon">❓</div>
      <h2>Shopping List Not Found</h2>
      <p>The shopping list you're looking for doesn't exist or you don't have access to it.</p>
      <Button variant="primary" on:click={goBack}>
        ← Back to Shopping Lists
      </Button>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
<Modal
  bind:open={showDeleteModal}
  title="Delete Shopping List"
  confirmText="Delete"
  cancelText="Cancel"
  confirmVariant="danger"
  loading={isDeleting}
  on:confirm={confirmDeleteShoppingList}
  on:cancel={cancelDeleteShoppingList}
  on:close={cancelDeleteShoppingList}
>
  <div class="text-center">
    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
      <span class="text-2xl">⚠️</span>
    </div>
    <p class="text-gray-900 mb-2">
      Are you sure you want to delete 
      <strong class="font-semibold">"{shoppingList?.name}"</strong>?
    </p>
    <p class="text-sm text-gray-500">
      This action cannot be undone. The shopping list and all its items will be permanently removed.
    </p>
  </div>
</Modal>

<style>
  .shopping-list-page {
    max-width: 1000px;
    margin: 0 auto;
    padding: 16px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    min-height: 100vh;
  }

  .loading-container,
  .error-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }

  .error-card {
    background: white;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 16px;
  }

  .error-card h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
  }

  .error-card p {
    color: #6b7280;
    margin: 0 0 24px 0;
  }

  .error-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  /* Header */
  .page-header {
    margin-bottom: 24px;
  }

  .header-top {
    margin-bottom: 20px;
  }

  .header-content {
    text-align: center;
  }

  .header-content h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #374151;
    margin: 0 0 16px 0;
  }

  .list-meta {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    color: #6b7280;
  }

  .meta-icon {
    font-size: 16px;
  }

  .progress-container {
    max-width: 400px;
    margin: 0 auto;
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(to right, #10b981, #059669);
    transition: width 0.3s ease;
  }

  .progress-text {
    font-size: 14px;
    color: #6b7280;
    text-align: center;
    display: block;
  }

  /* Actions */
  .list-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-bottom: 32px;
    flex-wrap: wrap;
  }

  .completed-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #dcfce7;
    color: #166534;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 500;
    border: 1px solid #bbf7d0;
  }

  .badge-icon {
    font-size: 16px;
  }

  /* Categories */
  .categories-container {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .category-section {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
  }

  .category-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
  }

  .category-icon {
    font-size: 1.5rem;
  }

  .category-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
    flex: 1;
  }

  .category-count {
    font-size: 0.9rem;
    color: #6b7280;
    background: #e5e7eb;
    padding: 4px 8px;
    border-radius: 12px;
  }

  .items-list {
    padding: 0;
  }

  .shopping-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    border-bottom: 1px solid #f3f4f6;
    transition: all 0.2s ease;
  }

  .shopping-item:last-child {
    border-bottom: none;
  }

  .shopping-item:hover {
    background: #f9fafb;
  }

  .shopping-item.checked {
    background: #f0fdf4;
    opacity: 0.7;
  }

  .item-checkbox {
    display: flex;
    align-items: center;
    cursor: pointer;
    position: relative;
  }

  .item-checkbox input {
    width: 20px;
    height: 20px;
    margin: 0;
    cursor: pointer;
  }

  .item-info {
    flex: 1;
  }

  .item-name {
    font-weight: 500;
    color: #374151;
    margin-bottom: 4px;
    transition: all 0.2s ease;
  }

  .item-name.completed {
    text-decoration: line-through;
    color: #6b7280;
  }

  .item-quantity {
    font-size: 0.9rem;
    color: #6b7280;
  }

  .empty-list {
    text-align: center;
    padding: 60px 20px;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 16px;
  }

  .empty-list h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
  }

  .empty-list p {
    color: #6b7280;
    margin: 0;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .shopping-list-page {
      padding: 12px;
    }

    .header-content h1 {
      font-size: 1.5rem;
    }

    .list-meta {
      flex-direction: column;
      gap: 8px;
    }

    .list-actions {
      flex-direction: column;
      align-items: center;
    }

    .category-header {
      padding: 12px 16px;
    }

    .shopping-item {
      padding: 12px 16px;
    }
  }
</style>