<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { user, loading, error } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { shoppingListService } from '$lib/services/shoppingListService.js';
	import { goto } from '$app/navigation';
	import Loading from '$lib/components/Loading.svelte';
	
	let recipe = null;
	let recipeLoading = true;
	let recipeError = '';
	let deleteConfirm = false;
	let isDeleting = false;
	let isCreatingShoppingList = false;
	let shoppingListSuccess = false;
	
	$: recipeId = $page.params.id;
	
	onMount(async () => {
		if (!$user) {
			goto('/login');
			return;
		}
		
		await loadRecipe();
	});
	
	async function loadRecipe() {
		try {
			recipeLoading = true;
			recipeError = '';
			recipe = await apiService.getRecipe(recipeId);
		} catch (err) {
			recipeError = 'Failed to load recipe: ' + err.message;
			console.error('Error loading recipe:', err);
		} finally {
			recipeLoading = false;
		}
	}
	
	function formatIngredients(ingredients) {
		if (!Array.isArray(ingredients)) return [];
		return ingredients.filter(ingredient => ingredient && ingredient.trim());
	}
	
	function formatInstructions(instructions) {
		if (!instructions) return [];
		
		// Handle array format (numbered steps)
		if (Array.isArray(instructions)) {
			return instructions
				.filter(step => step && step.trim())
				.map(step => step.trim());
		}
		
		// Handle string format - split by common step indicators
		let steps = instructions
			.split(/(?:Step \d+[:.]\s*|\d+\.\s*|^\d+\s*[-.)]\s*)/gm)
			.filter(line => line.trim())
			.map(line => line.trim());
		
		// If we didn't get good steps, split by newlines
		if (steps.length === 1) {
			steps = instructions
				.split('\n')
				.filter(line => line.trim())
				.map(line => line.trim().replace(/^(?:Step \d+[:.]\s*|\d+\.\s*|\d+\s*[-.)]\s*)/, ''));
		}
		
		return steps.filter(step => step.length > 0);
	}
	
	async function deleteRecipe() {
		if (!recipe?.id) return;
		
		try {
			isDeleting = true;
			await apiService.deleteRecipe(recipe.id);
			goto('/profile'); // Redirect to profile after deletion
		} catch (error) {
			console.error('Error deleting recipe:', error);
			recipeError = 'Failed to delete recipe: ' + error.message;
		} finally {
			isDeleting = false;
			deleteConfirm = false;
		}
	}
	
	function editRecipe() {
		// Navigate to edit page (could be add-recipe with pre-filled data)
		goto(`/add-recipe?edit=${recipe.id}`);
	}

	async function createShoppingListFromRecipe() {
		if (!recipe?.id) return;
		
		try {
			isCreatingShoppingList = true;
			
			const shoppingList = await shoppingListService.generateFromRecipes(
				[recipe.id],
				{
					listName: `${recipe.title} - Shopping List`,
					consolidateDuplicates: true,
					checkPantry: true,
					optimizeCategories: true,
					includeAlternatives: true
				}
			);
			
			shoppingListSuccess = true;
			
			// Show success for 2 seconds then navigate to shopping list page
			setTimeout(() => {
				goto('/shopping-list');
			}, 2000);
			
		} catch (err) {
			console.error('❌ Error creating shopping list:', err);
			recipeError = `Failed to create shopping list: ${err.message}`;
		} finally {
			isCreatingShoppingList = false;
		}
	}
</script>

<svelte:head>
	<title>{recipe?.title || 'Recipe'} - ForkFlix</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
	<!-- Compact Header -->
	<header class="bg-white/90 backdrop-blur-md shadow-lg border-b border-white/20 sticky top-0 z-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-14">
				<button
					on:click={() => goto('/')}
					class="flex items-center text-gray-600 hover:text-blue-600 transition-colors text-sm font-medium"
				>
					← Back
				</button>
				
				<!-- Action Buttons -->
				{#if recipe}
					<div class="flex items-center space-x-2">
						<button
							on:click={createShoppingListFromRecipe}
							disabled={isCreatingShoppingList}
							class="flex items-center px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
							title="Create Shopping List"
						>
							{#if isCreatingShoppingList}
								<span class="inline-flex items-center">
									<div class="inline-block animate-spin rounded-full h-3 w-3 border border-white border-b-transparent mr-2"></div>
									Creating...
								</span>
							{:else}
								🛒 Shopping List
							{/if}
						</button>
						<button
							on:click={editRecipe}
							class="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg text-sm font-medium"
							title="Edit Recipe"
						>
							✏️ Edit
						</button>
						<button
							on:click={() => deleteConfirm = true}
							class="flex items-center px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg text-sm font-medium"
							title="Delete Recipe"
						>
							🗑️ Delete
						</button>
					</div>
				{/if}
			</div>
		</div>
	</header>

	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Success Notification -->
		{#if shoppingListSuccess}
			<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-6 shadow-lg mb-6">
				<div class="flex items-center space-x-3">
					<div class="text-2xl">✅</div>
					<div>
						<p class="text-green-800 font-bold">Shopping List Created Successfully!</p>
						<p class="text-green-700">Redirecting you to the shopping list page...</p>
					</div>
				</div>
			</div>
		{/if}

		{#if recipeLoading}
			<div class="text-center py-16">
				<div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4 animate-spin">
					<div class="w-8 h-8 bg-white rounded-full"></div>
				</div>
				<p class="text-xl text-gray-600 font-medium">Loading your delicious recipe...</p>
			</div>
		{:else if recipeError}
			<div class="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-2xl p-6 shadow-lg">
				<div class="flex items-center space-x-3">
					<div class="text-2xl">⚠️</div>
					<p class="text-red-700 font-medium">{recipeError}</p>
				</div>
			</div>
		{:else if recipe}
			<!-- Recipe Header with Quick Info -->
			<div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-5 mb-6">
				<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
					<div class="flex-1">
						<h1 class="text-2xl lg:text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-3">{recipe.title}</h1>
						<div class="flex flex-wrap items-center gap-2 text-sm">
							<span class="bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 px-3 py-1.5 rounded-full font-semibold border border-blue-200 text-xs">
								{recipe.category}
							</span>
							<span class="bg-gradient-to-r from-green-100 to-emerald-200 text-green-800 px-3 py-1.5 rounded-full font-semibold border border-green-200 text-xs">
								⏱️ {recipe.cookingTime}min
							</span>
							<span class="bg-gradient-to-r from-purple-100 to-purple-200 text-purple-800 px-3 py-1.5 rounded-full font-semibold border border-purple-200 text-xs">
								📈 {recipe.difficulty}
							</span>
							{#if recipe.aiExtracted}
								<span class="bg-gradient-to-r from-yellow-100 to-amber-200 text-yellow-800 px-3 py-1.5 rounded-full font-semibold border border-yellow-200 text-xs">
									🤖 AI Generated
								</span>
							{/if}
						</div>
					</div>
					
					{#if recipe.instagramUrl}
						<div class="flex-shrink-0">
							<a 
								href={recipe.instagramUrl} 
								target="_blank" 
								rel="noopener noreferrer"
								class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg inline-flex items-center text-sm"
							>
								📱 Original
							</a>
						</div>
					{/if}
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<!-- Left Column: Video/Image (1/3 width) -->
				<div class="lg:col-span-1 order-2 lg:order-1">
					{#if recipe.embedCode}
						<div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-4 sticky top-6">
							<div class="instagram-embed">
								{@html recipe.embedCode}
							</div>
						</div>
					{:else if recipe.thumbnailUrl}
						<div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-4 sticky top-6">
							<img 
								src={recipe.thumbnailUrl} 
								alt={recipe.title}
								class="w-full h-64 object-cover rounded-xl shadow-lg"
							>
						</div>
					{/if}
				</div>

				<!-- Right Column: Recipe Content (2/3 width) -->
				<div class="lg:col-span-2 space-y-5 order-1 lg:order-2">
					<!-- Ingredients -->
					<div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
						<h2 class="text-xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-4 flex items-center">
							<span class="bg-gradient-to-r from-orange-100 to-orange-200 text-orange-600 p-2 rounded-lg mr-3 text-lg border border-orange-200">🥘</span>
							Ingredients <span class="text-gray-500 text-base ml-2">({formatIngredients(recipe.ingredients).length})</span>
						</h2>
						
						{#if formatIngredients(recipe.ingredients).length === 0}
							<div class="bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-xl p-4 shadow-lg">
								<div class="flex items-center space-x-3">
									<span class="text-2xl">⚠️</span>
									<p class="text-yellow-800 font-medium">No ingredients found. This might be due to extraction issues.</p>
								</div>
							</div>
						{:else}
							<div class="space-y-4">
								{#each formatIngredients(recipe.ingredients) as ingredient, index}
									<div class="flex items-center p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl hover:from-orange-50 hover:to-orange-100 transition-all duration-200 border border-gray-200 hover:border-orange-200 shadow-sm">
										<span class="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full text-sm flex items-center justify-center mr-4 font-bold shadow-lg">
											{index + 1}
										</span>
										<span class="text-gray-900 font-medium flex-1">{ingredient}</span>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Instructions -->
					<div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
						<h2 class="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4 flex items-center">
							<span class="bg-gradient-to-r from-green-100 to-emerald-200 text-green-600 p-2 rounded-lg mr-3 text-lg border border-green-200">👩‍🍳</span>
							Instructions
						</h2>
						
						{#if !recipe.instructions || formatInstructions(recipe.instructions).length === 0}
							<div class="bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-xl p-4 shadow-lg">
								<div class="flex items-center space-x-3">
									<span class="text-2xl">⚠️</span>
									<p class="text-yellow-800 font-medium">No instructions found. This might be due to extraction issues.</p>
								</div>
							</div>
						{:else}
							<div class="space-y-4">
								{#each formatInstructions(recipe.instructions) as step, index}
									<div class="flex items-start p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl hover:from-green-50 hover:to-emerald-50 transition-all duration-200 border border-gray-200 hover:border-green-200 shadow-sm">
										<span class="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-full text-sm flex items-center justify-center mr-4 font-bold shadow-lg">
											{index + 1}
										</span>
										<div class="flex-1">
											<p class="text-gray-900 leading-relaxed font-medium">{step}</p>
										</div>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Recipe Metadata -->
					<div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
						<h3 class="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4 flex items-center">
							<span class="bg-gradient-to-r from-blue-100 to-purple-200 text-blue-600 p-2 rounded-lg mr-3 text-base border border-blue-200">📊</span>
							Recipe Details
						</h3>
						<dl class="grid grid-cols-2 gap-4">
							<div class="text-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 shadow-sm">
								<dt class="text-blue-600 font-semibold text-xs mb-1">📅 Created</dt>
								<dd class="text-gray-900 font-bold text-base">
									{#if recipe.createdAt}
										{new Date(recipe.createdAt).toLocaleDateString()}
									{:else}
										Unknown
									{/if}
								</dd>
							</div>
							<div class="text-center p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 shadow-sm">
								<dt class="text-purple-600 font-semibold text-xs mb-1">🔢 Steps</dt>
								<dd class="text-gray-900 font-bold text-base">{formatInstructions(recipe.instructions).length}</dd>
							</div>
						</dl>
					</div>
				</div>
			</div>
		{:else}
			<div class="text-center py-20">
				<div class="bg-gradient-to-br from-gray-100 to-gray-200 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-8">
					<div class="text-6xl">😕</div>
				</div>
				<h2 class="text-3xl font-bold text-gray-900 mb-4">Recipe Not Found</h2>
				<p class="text-xl text-gray-600 mb-8 max-w-md mx-auto">The recipe you're looking for doesn't exist or has been removed.</p>
				<button
					on:click={() => goto('/')}
					class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-xl"
				>
					← Back to Recipes
				</button>
			</div>
		{/if}
	</main>
</div>

<!-- Delete Confirmation Modal -->
{#if deleteConfirm}
	<div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
		<div class="bg-white/95 backdrop-blur-md rounded-2xl p-8 max-w-md w-full shadow-2xl border border-white/20">
			<div class="text-center mb-6">
				<div class="bg-gradient-to-r from-red-100 to-pink-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
					<span class="text-3xl">🗑️</span>
				</div>
				<h3 class="text-2xl font-bold text-gray-900 mb-2">Delete Recipe</h3>
				<p class="text-gray-600">
					Are you sure you want to delete "<strong class="text-gray-900">{recipe?.title}</strong>"? This action cannot be undone.
				</p>
			</div>
			<div class="flex space-x-4">
				<button
					on:click={() => deleteConfirm = false}
					class="flex-1 py-3 border-2 border-gray-300 rounded-xl hover:bg-gray-50 font-semibold transition-all duration-200 text-gray-700"
					disabled={isDeleting}
				>
					Cancel
				</button>
				<button
					on:click={deleteRecipe}
					class="flex-1 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl hover:from-red-700 hover:to-red-800 font-semibold transition-all duration-200 disabled:opacity-50 shadow-lg"
					disabled={isDeleting}
				>
					{#if isDeleting}
						<span class="inline-flex items-center justify-center">
							<div class="inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-b-transparent mr-2"></div>
							Deleting...
						</span>
					{:else}
						Delete Recipe
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	:global(.instagram-embed iframe) {
		max-width: 100%;
		margin: 0 auto;
		display: block;
	}

	:global(.instagram-embed .instagram-media) {
		margin: 0 auto !important;
		max-width: 100% !important;
	}
</style>