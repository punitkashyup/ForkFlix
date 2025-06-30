<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { user, authInitialized } from '$lib/stores/auth.js';
  import { shoppingListService } from '$lib/services/shoppingListService.js';
  import Loading from '$lib/components/Loading.svelte';
  import Button from '$lib/components/Button.svelte';

  let shoppingList = null;
  let isLoading = true;
  let isSaving = false;
  let error = null;

  // Form fields
  let listName = '';
  let items = [];

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
      console.log('🔍 Loading shopping list for edit:', listId);
      shoppingList = await shoppingListService.getShoppingList(listId);
      
      // Populate form fields
      listName = shoppingList.name || '';
      items = (shoppingList.items || []).map(item => ({
        ...item,
        id: Math.random().toString(36).substr(2, 9) // Add temporary ID for tracking
      }));
      
      console.log('✅ Shopping list loaded for editing:', shoppingList);
    } catch (err) {
      console.error('❌ Error loading shopping list:', err);
      error = err.message || 'Failed to load shopping list';
    }
  }

  async function saveChanges() {
    if (!shoppingList || isSaving) return;
    
    if (!listName.trim()) {
      error = 'List name is required';
      return;
    }

    try {
      isSaving = true;
      error = null;

      // Prepare update data
      const updateData = {
        name: listName.trim(),
        items: items.map(item => ({
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          category: item.category,
          is_checked: item.is_checked || false,
          alternatives: item.alternatives || [],
          estimated_price: item.estimated_price || null
        })),
        total_items: items.length,
        checked_items: items.filter(item => item.is_checked).length
      };

      await shoppingListService.updateShoppingList(listId, updateData);
      console.log('✅ Shopping list updated successfully');
      
      // Redirect back to the shopping list view
      goto(`/shopping-list/${listId}`);
      
    } catch (err) {
      console.error('❌ Error saving shopping list:', err);
      error = err.message || 'Failed to save changes';
    } finally {
      isSaving = false;
    }
  }

  function addNewItem() {
    items = [...items, {
      id: Math.random().toString(36).substr(2, 9),
      name: '',
      quantity: 1,
      unit: 'item',
      category: 'other',
      is_checked: false,
      alternatives: [],
      estimated_price: null
    }];
  }

  function removeItem(itemId) {
    items = items.filter(item => item.id !== itemId);
  }

  function goBack() {
    goto(`/shopping-list/${listId}`);
  }

  const categoryOptions = [
    { value: 'produce', label: 'Produce' },
    { value: 'meat_seafood', label: 'Meat & Seafood' },
    { value: 'dairy_eggs', label: 'Dairy & Eggs' },
    { value: 'pantry', label: 'Pantry' },
    { value: 'frozen', label: 'Frozen' },
    { value: 'bakery', label: 'Bakery' },
    { value: 'beverages', label: 'Beverages' },
    { value: 'snacks', label: 'Snacks' },
    { value: 'household', label: 'Household' },
    { value: 'other', label: 'Other' }
  ];

  const unitOptions = [
    { value: 'item', label: 'item' },
    { value: 'cup', label: 'cup' },
    { value: 'cups', label: 'cups' },
    { value: 'tablespoon', label: 'tbsp' },
    { value: 'teaspoon', label: 'tsp' },
    { value: 'pound', label: 'lb' },
    { value: 'ounce', label: 'oz' },
    { value: 'gram', label: 'g' },
    { value: 'kilogram', label: 'kg' },
    { value: 'liter', label: 'L' },
    { value: 'milliliter', label: 'mL' }
  ];
</script>

<svelte:head>
  <title>Edit Shopping List - ForkFlix</title>
  <meta name="description" content="Edit your shopping list" />
</svelte:head>

{#if isLoading}
  <div class="loading-container">
    <Loading size="lg" message="Loading shopping list..." />
  </div>
{:else if error && !shoppingList}
  <div class="error-container">
    <div class="error-card">
      <div class="error-icon">⚠️</div>
      <h2>Error Loading Shopping List</h2>
      <p>{error}</p>
      <Button variant="primary" on:click={() => goto('/shopping-list')}>
        ← Back to Shopping Lists
      </Button>
    </div>
  </div>
{:else if shoppingList}
  <div class="edit-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-top">
        <Button variant="ghost" icon="←" on:click={goBack}>
          Back to Shopping List
        </Button>
      </div>
      
      <div class="header-content">
        <h1>✏️ Edit Shopping List</h1>
        <p>Make changes to your shopping list items and details.</p>
      </div>
    </div>

    <!-- Error Message -->
    {#if error}
      <div class="error-message">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{error}</span>
        <button class="error-close" on:click={() => error = null}>×</button>
      </div>
    {/if}

    <!-- Edit Form -->
    <div class="edit-form">
      <!-- List Name -->
      <div class="form-section">
        <label for="listName" class="form-label">Shopping List Name</label>
        <input
          id="listName"
          type="text"
          bind:value={listName}
          placeholder="Enter list name"
          class="form-input"
          required
        />
      </div>

      <!-- Items Section -->
      <div class="form-section">
        <div class="section-header">
          <h3>Shopping Items ({items.length})</h3>
          <Button variant="outline" size="sm" icon="+" on:click={addNewItem}>
            Add Item
          </Button>
        </div>

        {#if items.length === 0}
          <div class="empty-items">
            <div class="empty-icon">📝</div>
            <p>No items in this shopping list</p>
            <Button variant="primary" on:click={addNewItem}>Add First Item</Button>
          </div>
        {:else}
          <div class="items-list">
            {#each items as item, index (item.id)}
              <div class="item-editor">
                <div class="item-fields">
                  <div class="field-group">
                    <label class="field-label">Item Name</label>
                    <input
                      type="text"
                      bind:value={item.name}
                      placeholder="Enter item name"
                      class="form-input"
                    />
                  </div>
                  
                  <div class="field-group quantity-group">
                    <label class="field-label">Quantity</label>
                    <input
                      type="number"
                      bind:value={item.quantity}
                      min="0"
                      step="0.1"
                      class="form-input quantity-input"
                    />
                  </div>
                  
                  <div class="field-group">
                    <label class="field-label">Unit</label>
                    <select bind:value={item.unit} class="form-select">
                      {#each unitOptions as option}
                        <option value={option.value}>{option.label}</option>
                      {/each}
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label class="field-label">Category</label>
                    <select bind:value={item.category} class="form-select">
                      {#each categoryOptions as option}
                        <option value={option.value}>{option.label}</option>
                      {/each}
                    </select>
                  </div>
                </div>
                
                <div class="item-actions">
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      bind:checked={item.is_checked}
                      class="checkbox"
                    />
                    <span class="checkbox-text">Completed</span>
                  </label>
                  
                  <Button
                    variant="danger"
                    size="sm"
                    icon="🗑️"
                    on:click={() => removeItem(item.id)}
                    title="Remove item"
                  />
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <Button variant="outline" on:click={goBack}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          loading={isSaving}
          on:click={saveChanges}
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>
    </div>
  </div>
{:else}
  <div class="error-container">
    <div class="error-card">
      <div class="error-icon">❓</div>
      <h2>Shopping List Not Found</h2>
      <p>The shopping list you're trying to edit doesn't exist or you don't have access to it.</p>
      <Button variant="primary" on:click={() => goto('/shopping-list')}>
        ← Back to Shopping Lists
      </Button>
    </div>
  </div>
{/if}

<style>
  .edit-page {
    max-width: 800px;
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
    margin: 0 0 8px 0;
  }

  .header-content p {
    color: #6b7280;
    margin: 0;
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

  .error-message .error-icon {
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

  /* Form */
  .edit-form {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px;
  }

  .form-section {
    margin-bottom: 32px;
  }

  .form-section:last-child {
    margin-bottom: 0;
  }

  .form-label {
    display: block;
    font-weight: 600;
    color: #374151;
    margin-bottom: 8px;
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

  .form-select {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 16px;
    background: white;
    cursor: pointer;
    transition: border-color 0.2s;
  }

  .form-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  /* Section Header */
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .section-header h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
  }

  /* Items */
  .empty-items {
    text-align: center;
    padding: 40px 20px;
    background: #f9fafb;
    border-radius: 8px;
    border: 1px dashed #d1d5db;
  }

  .empty-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
  }

  .empty-items p {
    color: #6b7280;
    margin: 0 0 16px 0;
  }

  .items-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .item-editor {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
  }

  .item-fields {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1.5fr;
    gap: 12px;
    margin-bottom: 12px;
  }

  .field-group {
    display: flex;
    flex-direction: column;
  }

  .field-label {
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    margin-bottom: 4px;
  }

  .quantity-input {
    max-width: 100px;
  }

  .item-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }

  .checkbox {
    width: 16px;
    height: 16px;
    cursor: pointer;
  }

  .checkbox-text {
    font-size: 14px;
    color: #374151;
  }

  /* Form Actions */
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #e5e7eb;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .edit-page {
      padding: 12px;
    }

    .header-content h1 {
      font-size: 1.5rem;
    }

    .item-fields {
      grid-template-columns: 1fr;
      gap: 8px;
    }

    .form-actions {
      flex-direction: column;
    }
  }
</style>