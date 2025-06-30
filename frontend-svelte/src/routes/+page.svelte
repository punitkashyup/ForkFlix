<script>
	import { onMount } from 'svelte';
	import { user, recipes, loading, error, authInitialized } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import { PAGINATION } from '$lib/config/constants.js';
	import { signOut } from 'firebase/auth';
	import { auth } from '$lib/config/firebase.js';
	import Loading from '$lib/components/Loading.svelte';
	import SafeImage from '$lib/components/SafeImage.svelte';
	import Modal from '$lib/components/Modal.svelte';
	import Button from '$lib/components/Button.svelte';
	import SkeletonLoader from '$lib/components/SkeletonLoader.svelte';
	import { enhancedGoto } from '$lib/stores/navigation.js';
	import { safeLogout } from '$lib/utils/auth-guard.js';
	import { goto as gotoPage } from '$app/navigation';
	
	// Redirect to landing page for non-authenticated users
	$: if (!$user && $authInitialized) {
		gotoPage('/landing');
	}
	
	let searchTerm = '';
	let selectedCategory = '';
	let filteredRecipes = [];
	let showUserMenu = false;
	let hasAttemptedFetch = false;
	let selectedRecipeIds = [];
	let showBulkActions = false;
	let showDeleteModal = false;
	let recipeToDelete = null;
	let deletingRecipe = false;
	let navigatingToRecipe = null;
	let showMultiDeleteModal = false;
	let deletingMultipleRecipes = false;
	
	// Subscribe to recipes store
	$: filteredRecipes = $recipes.filter(recipe => {
		const matchesSearch = !searchTerm || 
			recipe.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
			recipe.ingredients.some(ing => ing.toLowerCase().includes(searchTerm.toLowerCase()));
		
		const matchesCategory = !selectedCategory || recipe.category === selectedCategory;
		
		return matchesSearch && matchesCategory;
	});

	let currentUserId = null;

	onMount(() => {
		console.log('🔧 Home page mounted');
	});

	// Watch for auth changes and handle accordingly
	$: if ($authInitialized) {
		const userId = $user?.uid;
		if (userId && userId !== currentUserId) {
			// User logged in or changed
			console.log('👤 User logged in:', userId);
			currentUserId = userId;
			hasAttemptedFetch = false; // Reset flag for new user
			fetchRecipes();
		} else if (!userId && currentUserId) {
			// User logged out
			console.log('🚪 User logged out');
			currentUserId = null;
			hasAttemptedFetch = false;
			recipes.set([]);
			error.set(null);
		}
	}

	async function fetchRecipes() {
		console.log('🔍 fetchRecipes called');
		try {
			loading.set(true);
			hasAttemptedFetch = true; // Set flag to prevent repeated calls
			const response = await apiService.getRecipes({ page: 1, limit: PAGINATION.DEFAULT_LIMIT });
			console.log('✅ API Response:', response);
			recipes.set(response.items || []);
			console.log('✅ Recipes set in store:', response.items?.length || 0, 'items');
		} catch (err) {
			error.set('Failed to load recipes');
			console.error('❌ Error fetching recipes:', err);
		} finally {
			loading.set(false);
		}
	}

	function handleLogin() {
		goto('/login');
	}

	function handleAddRecipe() {
		enhancedGoto('/add-recipe');
	}

	async function navigateToRecipe(recipeId) {
		navigatingToRecipe = recipeId;
		try {
			await enhancedGoto(`/recipe/${recipeId}`);
		} finally {
			navigatingToRecipe = null;
		}
	}

	async function handleLogout() {
		await safeLogout(auth, signOut);
	}

	// Close dropdown when clicking outside
	function handleClickOutside(event) {
		if (showUserMenu && !event.target.closest('.user-menu')) {
			showUserMenu = false;
		}
	}

	function toggleRecipeSelection(recipeId, event = null) {
		if (event) {
			event.stopPropagation();
		}
		if (selectedRecipeIds.includes(recipeId)) {
			selectedRecipeIds = selectedRecipeIds.filter(id => id !== recipeId);
		} else {
			selectedRecipeIds = [...selectedRecipeIds, recipeId];
		}
		showBulkActions = selectedRecipeIds.length > 0;
	}

	function handleCardClick(recipeId, event) {
		// Don't toggle selection if clicking on the "View Recipe" button or checkbox
		if (event.target.closest('button') || event.target.closest('input')) {
			return;
		}
		toggleRecipeSelection(recipeId);
	}

	function selectAllRecipes() {
		selectedRecipeIds = filteredRecipes.map(recipe => recipe.id);
		showBulkActions = true;
	}

	function clearSelection() {
		selectedRecipeIds = [];
		showBulkActions = false;
	}

	function createShoppingListFromSelected() {
		if (selectedRecipeIds.length === 0) return;
		
		// Navigate to shopping list page with selected recipes
		const queryParams = new URLSearchParams();
		selectedRecipeIds.forEach(id => queryParams.append('recipe', id));
		enhancedGoto(`/shopping-list?${queryParams.toString()}`);
	}

	function handleDeleteRecipe(recipe) {
		recipeToDelete = recipe;
		showDeleteModal = true;
	}

	function handleDeleteCancel() {
		showDeleteModal = false;
		recipeToDelete = null;
	}

	async function handleDeleteConfirm() {
		if (!recipeToDelete) return;
		
		try {
			deletingRecipe = true;
			await apiService.deleteRecipe(recipeToDelete.id);
			
			// Remove from local store
			recipes.update(currentRecipes => 
				currentRecipes.filter(r => r.id !== recipeToDelete.id)
			);
			
			// Remove from selected recipes if it was selected
			selectedRecipeIds = selectedRecipeIds.filter(id => id !== recipeToDelete.id);
			showBulkActions = selectedRecipeIds.length > 0;
			
			// Close modal
			showDeleteModal = false;
			recipeToDelete = null;
			
		} catch (err) {
			console.error('Failed to delete recipe:', err);
			error.set('Failed to delete recipe. Please try again.');
		} finally {
			deletingRecipe = false;
		}
	}

	function handleDeleteMultipleRecipes() {
		if (selectedRecipeIds.length === 0) return;
		showMultiDeleteModal = true;
	}

	function handleMultiDeleteCancel() {
		showMultiDeleteModal = false;
	}

	async function handleMultiDeleteConfirm() {
		if (selectedRecipeIds.length === 0) return;
		
		try {
			deletingMultipleRecipes = true;
			
			// Delete all selected recipes
			const deletePromises = selectedRecipeIds.map(id => apiService.deleteRecipe(id));
			await Promise.all(deletePromises);
			
			// Remove from local store
			recipes.update(currentRecipes => 
				currentRecipes.filter(r => !selectedRecipeIds.includes(r.id))
			);
			
			// Clear selection and close modal
			selectedRecipeIds = [];
			showBulkActions = false;
			showMultiDeleteModal = false;
			
		} catch (err) {
			console.error('Failed to delete recipes:', err);
			error.set('Failed to delete some recipes. Please try again.');
		} finally {
			deletingMultipleRecipes = false;
		}
	}
</script>

<svelte:head>
	<title>ForkFlix - Recipe Manager</title>
</svelte:head>

<div class="min-h-screen" on:click={handleClickOutside} on:keydown={handleClickOutside} role="main">
	<!-- Header -->
	<header class="bg-white/90 backdrop-blur-md shadow-lg border-b border-white/20 sticky top-0 z-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">🍴 ForkFlix</h1>
				</div>
				
				<div class="flex items-center space-x-4">
					{#if $user}
						<Button
							variant="primary"
							icon="✨"
							on:click={handleAddRecipe}
						>
							Add Recipe
						</Button>
						<Button
							variant="secondary"
							icon="🛒"
							on:click={() => enhancedGoto('/shopping-list')}
						>
							Shopping List
						</Button>
						<div class="relative user-menu">
							<button 
								on:click={() => showUserMenu = !showUserMenu}
								class="flex items-center space-x-2 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 rounded-xl px-3 py-2 transition-all duration-200"
							>
								<SafeImage 
									src={$user.photoURL} 
									alt="Profile" 
									fallbackText={$user.displayName || $user.email}
									size="sm"
								/>
								<span class="text-sm font-medium">{$user.displayName || $user.email}</span>
								<svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
								</svg>
							</button>
							
							{#if showUserMenu}
								<div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border">
									<button
										on:click={() => { showUserMenu = false; enhancedGoto('/profile'); }}
										class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
									>
										👤 Profile
									</button>
									<button
										on:click={() => { showUserMenu = false; enhancedGoto('/shopping-list'); }}
										class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
									>
										🛒 Shopping Lists
									</button>
									<button
										on:click={() => { showUserMenu = false; handleLogout(); }}
										class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
									>
										🚪 Logout
									</button>
								</div>
							{/if}
						</div>
					{:else}
						<Button
							variant="primary"
							on:click={handleLogin}
						>
							Login
						</Button>
					{/if}
				</div>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main>
		{#if $user}
			<!-- Logged-in user content -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
				<div class="text-center mb-12">
					<h2 class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-4">Your Recipe Collection</h2>
					<p class="text-xl text-gray-600 max-w-2xl mx-auto">Discover, organize, and cook your favorite recipes</p>
				</div>
				
				<!-- Bulk Actions Bar -->
				{#if showBulkActions}
					<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 mb-6 flex items-center justify-between shadow-lg">
						<div class="flex items-center space-x-4">
							<span class="font-semibold text-green-800">
								{selectedRecipeIds.length} recipe{selectedRecipeIds.length === 1 ? '' : 's'} selected
							</span>
							<button
								on:click={selectAllRecipes}
								class="text-green-600 hover:text-green-800 font-medium underline text-sm"
							>
								Select All ({filteredRecipes.length})
							</button>
							<button
								on:click={clearSelection}
								class="text-green-600 hover:text-green-800 font-medium underline text-sm"
							>
								Clear Selection
							</button>
						</div>
						<div class="flex items-center space-x-3">
							<Button
								variant="secondary"
								icon="🛒"
								on:click={createShoppingListFromSelected}
							>
								Create Shopping List
							</Button>
							<Button
								variant="danger"
								icon="🗑️"
								on:click={handleDeleteMultipleRecipes}
							>
								Delete Selected
							</Button>
						</div>
					</div>
				{/if}

				<!-- Search and Filter -->
				<div class="flex flex-col sm:flex-row gap-6 mb-8">
					<div class="relative flex-1">
						<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
							</svg>
						</div>
						<input
							type="text"
							placeholder="Search your recipes..."
							bind:value={searchTerm}
							class="w-full pl-12 pr-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 shadow-lg transition-all duration-200"
						>
					</div>
					<select 
						bind:value={selectedCategory} 
						class="sm:w-64 px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 shadow-lg transition-all duration-200"
					>
						<option value="">🍽️ All Categories</option>
						<option value="Starters">🥗 Starters</option>
						<option value="Main Course">🍖 Main Course</option>
						<option value="Desserts">🍰 Desserts</option>
						<option value="Beverages">🥤 Beverages</option>
						<option value="Snacks">🍿 Snacks</option>
					</select>
				</div>

				<!-- Loading State -->
				{#if $loading}
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
						<SkeletonLoader type="card" count={8} />
					</div>
				{:else if $error}
					<div class="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-2xl p-6 shadow-lg">
						<div class="flex items-center space-x-3">
							<div class="text-2xl">⚠️</div>
							<p class="text-red-700 font-medium">{$error}</p>
						</div>
					</div>
				{:else if filteredRecipes.length === 0}
					<!-- Empty State -->
					<div class="text-center py-20">
						<div class="bg-gradient-to-br from-blue-100 to-purple-100 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-8">
							<div class="text-6xl">🍳</div>
						</div>
						<h3 class="text-3xl font-bold text-gray-900 mb-4">
							No recipes yet
						</h3>
						<p class="text-xl text-gray-600 mb-8 max-w-md mx-auto">
							Start building your collection by adding your first recipe from Instagram or YouTube!
						</p>
						<Button
							variant="primary"
							size="lg"
							icon="✨"
							on:click={handleAddRecipe}
						>
							Add Your First Recipe
						</Button>
					</div>
				{:else}
					<!-- Recipe Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
						{#each filteredRecipes as recipe (recipe.id)}
							<div class="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer overflow-hidden h-full flex flex-col border border-white/20 hover:border-blue-200 transform hover:scale-[1.02] relative"
								 class:ring-2={selectedRecipeIds.includes(recipe.id)}
								 class:ring-green-500={selectedRecipeIds.includes(recipe.id)}
								 class:bg-green-50={selectedRecipeIds.includes(recipe.id)}
								 on:click={(e) => handleCardClick(recipe.id, e)}
								 role="button"
								 tabindex="0"
								 on:keydown={(e) => e.key === 'Enter' && handleCardClick(recipe.id, e)}>
								
								<!-- Selection Checkbox -->
								<div class="absolute top-2 right-2 z-10">
									<input
										type="checkbox"
										checked={selectedRecipeIds.includes(recipe.id)}
										on:change={(e) => toggleRecipeSelection(recipe.id, e)}
										class="w-5 h-5 text-green-600 bg-white border-2 border-gray-300 rounded focus:ring-green-500 focus:ring-2 shadow-lg"
									/>
								</div>
								<!-- Recipe thumbnail -->
								{#if recipe.thumbnailUrl}
									<div class="h-40 bg-gradient-to-br from-gray-100 to-gray-200 overflow-hidden relative">
										<img 
											src={recipe.thumbnailUrl} 
											alt={recipe.title}
											class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
											loading="lazy"
										>
										<div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
									</div>
								{:else}
									<div class="h-40 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center relative overflow-hidden">
										<span class="text-4xl opacity-80 group-hover:scale-110 transition-transform duration-300">🍽️</span>
										<div class="absolute inset-0 bg-gradient-to-t from-white/20 to-transparent"></div>
									</div>
								{/if}
								
								<!-- Recipe Content -->
								<div class="p-4 flex-1 flex flex-col">
									<!-- Title -->
									<h3 class="text-lg font-bold text-gray-900 mb-3 line-clamp-2 min-h-[3rem] group-hover:text-blue-600 transition-colors duration-200">
										{recipe.title}
									</h3>
									
									<!-- Tags -->
									<div class="flex items-center flex-wrap gap-1.5 text-sm text-gray-600 mb-3">
										<span class="bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold border border-blue-200">
											{recipe.category}
										</span>
										<span class="bg-gradient-to-r from-green-100 to-emerald-200 text-green-800 px-2 py-1 rounded-full text-xs font-semibold border border-green-200">
											⏱️ {recipe.cookingTime}min
										</span>
										<span class="bg-gradient-to-r from-purple-100 to-purple-200 text-purple-800 px-2 py-1 rounded-full text-xs font-semibold border border-purple-200">
											📈 {recipe.difficulty}
										</span>
									</div>
									
									<!-- Ingredients Preview -->
									<div class="mb-4 flex-1">
										<p class="text-xs text-gray-600 font-medium mb-1">🥘 Ingredients:</p>
										<p class="text-sm text-gray-700 leading-relaxed">
											{recipe.ingredients.slice(0, 2).join(', ')}
											{#if recipe.ingredients.length > 2}
												<span class="text-blue-600 font-semibold">
													 +{recipe.ingredients.length - 2} more
												</span>
											{/if}
										</p>
									</div>
									
									<!-- Action Buttons -->
									<div class="flex gap-2 items-center">
										<Button
											variant="secondary"
											size="sm"
											fullWidth={true}
											iconPosition="right"
											icon="→"
											loading={navigatingToRecipe === recipe.id}
											on:click={() => navigateToRecipe(recipe.id)}
										>
											View Recipe
										</Button>
										<button
											class="recipe-delete-btn"
											on:click={() => handleDeleteRecipe(recipe)}
											title="Delete Recipe"
											type="button"
										>
											<svg class="delete-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
												<path d="M3 6H5H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
												<path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
												<path d="M10 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
												<path d="M14 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
											</svg>
										</button>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</main>
</div>

<!-- Delete Confirmation Modal -->
<Modal
	bind:open={showDeleteModal}
	title="Delete Recipe"
	confirmText="Delete"
	cancelText="Cancel"
	confirmVariant="danger"
	loading={deletingRecipe}
	on:confirm={handleDeleteConfirm}
	on:cancel={handleDeleteCancel}
	on:close={handleDeleteCancel}
>
	<div class="text-center">
		<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
			<span class="text-2xl">⚠️</span>
		</div>
		<p class="text-gray-900 mb-2">
			Are you sure you want to delete 
			<strong class="font-semibold">"{recipeToDelete?.title}"</strong>?
		</p>
		<p class="text-sm text-gray-500">
			This action cannot be undone. The recipe will be permanently removed from your collection.
		</p>
	</div>
</Modal>

<!-- Multi-Delete Confirmation Modal -->
<Modal
	bind:open={showMultiDeleteModal}
	title="Delete Multiple Recipes"
	confirmText="Delete All"
	cancelText="Cancel"
	confirmVariant="danger"
	loading={deletingMultipleRecipes}
	on:confirm={handleMultiDeleteConfirm}
	on:cancel={handleMultiDeleteCancel}
	on:close={handleMultiDeleteCancel}
>
	<div class="text-center">
		<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
			<span class="text-2xl">⚠️</span>
		</div>
		<p class="text-gray-900 mb-2">
			Are you sure you want to delete 
			<strong class="font-semibold">{selectedRecipeIds.length}</strong> 
			selected recipe{selectedRecipeIds.length === 1 ? '' : 's'}?
		</p>
		<p class="text-sm text-gray-500 mb-3">
			This action cannot be undone. All selected recipes will be permanently removed from your collection.
		</p>
		{#if selectedRecipeIds.length > 0}
			<div class="text-xs text-gray-400 bg-gray-50 rounded-lg p-2 max-h-20 overflow-y-auto">
				<strong>Recipes to delete:</strong><br>
				{#each selectedRecipeIds.slice(0, 5) as recipeId}
					{@const recipe = $recipes.find(r => r.id === recipeId)}
					{recipe?.title || recipeId}<br>
				{/each}
				{#if selectedRecipeIds.length > 5}
					... and {selectedRecipeIds.length - 5} more
				{/if}
			</div>
		{/if}
	</div>
</Modal>

<style>
	/* Line clamp utility for consistent card heights */
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	/* Custom delete button with red styling */
	.recipe-delete-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		min-width: 36px;
		height: 36px;
		padding: 8px;
		background: transparent;
		border: 1px solid #fca5a5;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s ease;
		color: #dc2626;
		flex-shrink: 0;
	}

	.recipe-delete-btn:hover {
		background: #fef2f2;
		border-color: #f87171;
		color: #b91c1c;
	}

	.recipe-delete-btn:active {
		background: #fee2e2;
		border-color: #ef4444;
		transform: scale(0.95);
	}

	.recipe-delete-btn:focus {
		outline: none;
		ring: 2px solid #fca5a5;
		ring-offset: 2px;
	}

	.delete-icon {
		width: 18px;
		height: 18px;
		stroke-width: 2;
	}
</style>
