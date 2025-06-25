<script>
	import { onMount } from 'svelte';
	import { user, loading, recipes } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import Loading from '$lib/components/Loading.svelte';

	let userRecipes = [];
	let recipeStats = {
		totalRecipes: 0,
		categoryCounts: {},
		recentActivity: [],
		averageConfidence: 0
	};
	let isLoadingRecipes = true;
	let deleteConfirm = null;
	let selectedRecipes = new Set();
	let showBulkActions = false;

	onMount(() => {
		// Redirect if not logged in
		if (!$user) {
			goto('/login');
			return;
		}
		loadUserProfile();
	});

	async function loadUserProfile() {
		try {
			isLoadingRecipes = true;
			
			// Load user's recipes
			const response = await apiService.getRecipes({ userId: $user.uid });
			userRecipes = response.items || response.data || [];
			
			// Calculate statistics
			calculateRecipeStats();
			
		} catch (error) {
			console.error('Error loading profile:', error);
		} finally {
			isLoadingRecipes = false;
		}
	}

	function calculateRecipeStats() {
		recipeStats.totalRecipes = userRecipes.length;
		
		// Calculate category counts
		const categoryMap = {};
		let totalConfidence = 0;
		let confidenceCount = 0;
		
		userRecipes.forEach(recipe => {
			// Count categories
			const category = recipe.category || 'Other';
			categoryMap[category] = (categoryMap[category] || 0) + 1;
			
			// Calculate average confidence
			if (recipe.confidence) {
				totalConfidence += recipe.confidence;
				confidenceCount++;
			}
		});
		
		recipeStats.categoryCounts = categoryMap;
		recipeStats.averageConfidence = confidenceCount > 0 ? totalConfidence / confidenceCount : 0;
		
		// Get recent activity (last 5 recipes)
		recipeStats.recentActivity = userRecipes
			.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
			.slice(0, 5);
	}

	async function deleteRecipe(recipeId) {
		try {
			await apiService.deleteRecipe(recipeId);
			
			// Remove from local state
			userRecipes = userRecipes.filter(r => r.id !== recipeId);
			calculateRecipeStats();
			
			// Clear selection if recipe was selected
			selectedRecipes.delete(recipeId);
			selectedRecipes = new Set(selectedRecipes);
			
			deleteConfirm = null;
		} catch (error) {
			console.error('Error deleting recipe:', error);
			alert('Failed to delete recipe. Please try again.');
		}
	}

	async function bulkDeleteRecipes() {
		if (selectedRecipes.size === 0) return;
		
		const confirmDelete = confirm(`Are you sure you want to delete ${selectedRecipes.size} recipes? This action cannot be undone.`);
		if (!confirmDelete) return;
		
		try {
			// Delete each selected recipe
			const deletePromises = Array.from(selectedRecipes).map(id => apiService.deleteRecipe(id));
			await Promise.all(deletePromises);
			
			// Remove from local state
			userRecipes = userRecipes.filter(r => !selectedRecipes.has(r.id));
			calculateRecipeStats();
			
			// Clear selections
			selectedRecipes.clear();
			selectedRecipes = new Set();
			showBulkActions = false;
			
		} catch (error) {
			console.error('Error bulk deleting recipes:', error);
			alert('Failed to delete some recipes. Please try again.');
		}
	}

	function toggleRecipeSelection(recipeId) {
		if (selectedRecipes.has(recipeId)) {
			selectedRecipes.delete(recipeId);
		} else {
			selectedRecipes.add(recipeId);
		}
		selectedRecipes = new Set(selectedRecipes);
		showBulkActions = selectedRecipes.size > 0;
	}

	function selectAllRecipes() {
		if (selectedRecipes.size === userRecipes.length) {
			// Deselect all
			selectedRecipes.clear();
			showBulkActions = false;
		} else {
			// Select all
			userRecipes.forEach(recipe => selectedRecipes.add(recipe.id));
			showBulkActions = true;
		}
		selectedRecipes = new Set(selectedRecipes);
	}

	function getConfidenceColor(confidence) {
		if (confidence >= 0.8) return 'text-green-600 bg-green-100';
		if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
		return 'text-red-600 bg-red-100';
	}

	function formatDate(dateString) {
		if (!dateString) return 'Recently';
		
		try {
			const date = new Date(dateString);
			if (isNaN(date.getTime())) return 'Recently';
			
			return date.toLocaleDateString('en-US', {
				year: 'numeric',
				month: 'short',
				day: 'numeric'
			});
		} catch (error) {
			console.warn('Invalid date format:', dateString);
			return 'Recently';
		}
	}
</script>

<svelte:head>
	<title>Profile - ForkFlix</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<button
					on:click={() => goto('/')}
					class="flex items-center text-gray-600 hover:text-gray-900"
				>
					← Back to Home
				</button>
				<h1 class="text-2xl font-bold text-gray-900">My Profile</h1>
				<div></div>
			</div>
		</div>
	</header>

	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		{#if $user}
			<!-- User Information Section -->
			<div class="bg-white rounded-lg shadow-sm p-6 mb-8">
				<div class="flex items-center space-x-6">
					<div class="h-20 w-20 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center text-white text-2xl font-bold">
						{$user.displayName ? $user.displayName.charAt(0).toUpperCase() : $user.email.charAt(0).toUpperCase()}
					</div>
					<div class="flex-1">
						<h2 class="text-2xl font-bold text-gray-900">{$user.displayName || 'Recipe Enthusiast'}</h2>
						<p class="text-gray-600">{$user.email}</p>
						<p class="text-sm text-gray-500 mt-1">
							Member since {formatDate($user.metadata?.creationTime)}
						</p>
					</div>
					<div class="text-center">
						<div class="text-3xl font-bold text-purple-600">{recipeStats.totalRecipes}</div>
						<div class="text-sm text-gray-600">Recipes Saved</div>
					</div>
				</div>
			</div>

			<!-- Recipe Statistics Dashboard -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
				<!-- Total Recipes -->
				<div class="bg-white rounded-lg shadow-sm p-6">
					<div class="flex items-center">
						<div class="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center">
							<span class="text-purple-600">📄</span>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600">Total Recipes</p>
							<p class="text-2xl font-bold text-gray-900">{recipeStats.totalRecipes}</p>
						</div>
					</div>
				</div>

				<!-- Average Confidence -->
				<div class="bg-white rounded-lg shadow-sm p-6">
					<div class="flex items-center">
						<div class="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
							<span class="text-green-600">🎯</span>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600">Avg. Confidence</p>
							<p class="text-2xl font-bold text-gray-900">{Math.round(recipeStats.averageConfidence * 100)}%</p>
						</div>
					</div>
				</div>

				<!-- Most Common Category -->
				<div class="bg-white rounded-lg shadow-sm p-6">
					<div class="flex items-center">
						<div class="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
							<span class="text-blue-600">🍽️</span>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600">Favorite Category</p>
							<p class="text-lg font-bold text-gray-900">
								{Object.entries(recipeStats.categoryCounts).length > 0 
									? Object.entries(recipeStats.categoryCounts).sort((a, b) => b[1] - a[1])[0][0]
									: 'None yet'}
							</p>
						</div>
					</div>
				</div>

				<!-- Recent Activity -->
				<div class="bg-white rounded-lg shadow-sm p-6">
					<div class="flex items-center">
						<div class="h-8 w-8 bg-orange-100 rounded-lg flex items-center justify-center">
							<span class="text-orange-600">⚡</span>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600">Last Recipe</p>
							<p class="text-sm font-bold text-gray-900">
								{recipeStats.recentActivity.length > 0 
									? formatDate(recipeStats.recentActivity[0].createdAt)
									: 'No recipes yet'}
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Saved Recipes Collection -->
			<div class="bg-white rounded-lg shadow-sm p-6">
				<div class="flex justify-between items-center mb-6">
					<h3 class="text-xl font-bold text-gray-900">My Recipe Collection</h3>
					
					{#if userRecipes.length > 0}
						<div class="flex items-center space-x-4">
							{#if showBulkActions}
								<button
									on:click={bulkDeleteRecipes}
									class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium"
								>
									Delete Selected ({selectedRecipes.size})
								</button>
							{/if}
							<button
								on:click={selectAllRecipes}
								class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
							>
								{selectedRecipes.size === userRecipes.length ? 'Deselect All' : 'Select All'}
							</button>
						</div>
					{/if}
				</div>

				{#if isLoadingRecipes}
					<div class="py-12">
						<Loading message="Loading your recipes..." size="md" />
					</div>
				{:else if userRecipes.length === 0}
					<div class="text-center py-12">
						<div class="text-6xl mb-4">🍳</div>
						<h4 class="text-lg font-medium text-gray-900 mb-2">No recipes yet</h4>
						<p class="text-gray-600 mb-6">Start by extracting your first recipe from Instagram!</p>
						<button
							on:click={() => goto('/add-recipe')}
							class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
						>
							Extract Your First Recipe
						</button>
					</div>
				{:else}
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						{#each userRecipes as recipe}
							<div class="relative bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-purple-300 transition-all duration-200 overflow-hidden h-full flex flex-col">
								<!-- Selection Checkbox -->
								<div class="absolute top-3 left-3 z-10">
									<input
										type="checkbox"
										checked={selectedRecipes.has(recipe.id)}
										on:change={() => toggleRecipeSelection(recipe.id)}
										class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
									>
								</div>

								<!-- Delete Button -->
								<div class="absolute top-3 right-3 z-10">
									<button
										on:click={() => deleteConfirm = recipe.id}
										class="w-8 h-8 flex items-center justify-center bg-white/80 backdrop-blur-sm hover:bg-red-50 text-red-500 hover:text-red-700 rounded-full transition-colors"
										title="Delete recipe"
									>
										🗑️
									</button>
								</div>

								<!-- Recipe Thumbnail -->
								{#if recipe.thumbnailUrl}
									<div class="h-48 bg-gray-100 overflow-hidden">
										<img 
											src={recipe.thumbnailUrl} 
											alt={recipe.title}
											class="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
											loading="lazy"
										>
									</div>
								{:else}
									<div class="h-48 bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center">
										<span class="text-6xl opacity-60">🍽️</span>
									</div>
								{/if}

								<!-- Recipe Content -->
								<div class="p-4 flex-1 flex flex-col">
									<!-- Title -->
									<h4 class="font-bold text-gray-900 text-lg leading-snug mb-3 line-clamp-2 min-h-[3.5rem]">
										{recipe.title}
									</h4>

									<!-- Tags -->
									<div class="flex flex-wrap gap-2 mb-4">
										<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
											{recipe.category}
										</span>
										<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
											⏱️ {recipe.cookingTime}min
										</span>
										<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
											📈 {recipe.difficulty}
										</span>
									</div>

									<!-- Stats -->
									<div class="space-y-2 text-sm text-gray-600 mb-4 flex-1">
										<div class="flex items-center justify-between">
											<span class="flex items-center">
												<span class="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
												Created
											</span>
											<span class="font-medium">{formatDate(recipe.createdAt)}</span>
										</div>
										{#if recipe.confidence}
											<div class="flex items-center justify-between">
												<span class="flex items-center">
													<span class="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
													Confidence
												</span>
												<span class="px-2 py-1 rounded-full text-xs font-medium {getConfidenceColor(recipe.confidence)}">
													{Math.round(recipe.confidence * 100)}%
												</span>
											</div>
										{/if}
									</div>

									<!-- Action Button -->
									<button
										on:click={() => goto(`/recipe/${recipe.id}`)}
										class="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 font-medium text-sm transition-all duration-200 transform hover:scale-[1.02]"
									>
										View Recipe →
									</button>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{:else}
			<!-- Not logged in state -->
			<div class="text-center py-12">
				<h2 class="text-2xl font-bold text-gray-900 mb-4">Please Log In</h2>
				<p class="text-gray-600 mb-6">You need to be logged in to view your profile.</p>
				<button
					on:click={() => goto('/login')}
					class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
				>
					Go to Login
				</button>
			</div>
		{/if}
	</main>
</div>

<!-- Delete Confirmation Modal -->
{#if deleteConfirm}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white rounded-lg p-6 max-w-md w-full">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Delete Recipe</h3>
			<p class="text-gray-600 mb-6">
				Are you sure you want to delete this recipe? This action cannot be undone.
			</p>
			<div class="flex space-x-4">
				<button
					on:click={() => deleteConfirm = null}
					class="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
				>
					Cancel
				</button>
				<button
					on:click={() => deleteRecipe(deleteConfirm)}
					class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
				>
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Tablet touch targets only */
	@media (min-width: 768px) and (max-width: 1023px) {
		button {
			min-height: 44px;
		}
	}
	
	/* Line clamp utility for consistent card heights */
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	
	/* Recipe card hover effects */
	.recipe-card {
		transition: all 0.2s ease-in-out;
	}
	
	.recipe-card:hover {
		transform: translateY(-2px);
	}
</style>