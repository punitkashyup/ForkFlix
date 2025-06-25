<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { user, loading, error } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import Loading from '$lib/components/Loading.svelte';
	
	let recipe = null;
	let recipeLoading = true;
	let recipeError = '';
	let deleteConfirm = false;
	let isDeleting = false;
	
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
</script>

<svelte:head>
	<title>{recipe?.title || 'Recipe'} - ForkFlix</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Compact Header -->
	<header class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-14">
				<button
					on:click={() => goto('/')}
					class="flex items-center text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
				>
					← Back
				</button>
				
				<!-- Action Buttons -->
				{#if recipe}
					<div class="flex items-center space-x-2">
						<button
							on:click={editRecipe}
							class="flex items-center px-3 py-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors text-sm font-medium"
							title="Edit Recipe"
						>
							✏️ Edit
						</button>
						<button
							on:click={() => deleteConfirm = true}
							class="flex items-center px-3 py-1.5 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
							title="Delete Recipe"
						>
							🗑️ Delete
						</button>
					</div>
				{/if}
			</div>
		</div>
	</header>

	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
		{#if recipeLoading}
			<div class="text-center py-8">
				<Loading message="Loading recipe..." />
			</div>
		{:else if recipeError}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4">
				<p class="text-red-700">{recipeError}</p>
			</div>
		{:else if recipe}
			<!-- Recipe Header with Quick Info -->
			<div class="bg-white rounded-xl shadow-sm border p-4 mb-4">
				<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
					<div class="flex-1">
						<h1 class="text-xl lg:text-2xl font-bold text-gray-900 mb-2">{recipe.title}</h1>
						<div class="flex flex-wrap items-center gap-2 text-xs">
							<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-medium">
								{recipe.category}
							</span>
							<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
								⏱️ {recipe.cookingTime}min
							</span>
							<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded-full font-medium">
								📈 {recipe.difficulty}
							</span>
							{#if recipe.aiExtracted}
								<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full font-medium">
									🤖 AI
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
								class="btn btn-primary text-sm py-2 px-3 inline-flex items-center"
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
						<div class="bg-white rounded-xl shadow-sm border p-4 sticky top-6">
							<div class="instagram-embed">
								{@html recipe.embedCode}
							</div>
						</div>
					{:else if recipe.thumbnailUrl}
						<div class="bg-white rounded-xl shadow-sm border p-4 sticky top-6">
							<img 
								src={recipe.thumbnailUrl} 
								alt={recipe.title}
								class="w-full h-64 object-cover rounded-lg"
							>
						</div>
					{/if}
				</div>

				<!-- Right Column: Recipe Content (2/3 width) -->
				<div class="lg:col-span-2 space-y-4 order-1 lg:order-2">
					<!-- Ingredients -->
					<div class="bg-white rounded-xl shadow-sm border p-5">
						<h2 class="text-lg font-bold text-gray-900 mb-3 flex items-center">
							<span class="bg-orange-100 text-orange-600 p-1.5 rounded-lg mr-2 text-base">🥘</span>
							Ingredients <span class="text-gray-500 text-sm ml-1">({formatIngredients(recipe.ingredients).length})</span>
						</h2>
						
						{#if formatIngredients(recipe.ingredients).length === 0}
							<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
								<p class="text-yellow-800 text-sm">⚠️ No ingredients found. This might be due to extraction issues.</p>
							</div>
						{:else}
							<div class="space-y-2">
								{#each formatIngredients(recipe.ingredients) as ingredient, index}
									<div class="flex items-center p-2.5 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
										<span class="flex-shrink-0 w-5 h-5 bg-orange-500 text-white rounded-full text-xs flex items-center justify-center mr-3 font-medium">
											{index + 1}
										</span>
										<span class="text-gray-900 text-sm font-medium flex-1">{ingredient}</span>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Instructions -->
					<div class="bg-white rounded-xl shadow-sm border p-5">
						<h2 class="text-lg font-bold text-gray-900 mb-3 flex items-center">
							<span class="bg-green-100 text-green-600 p-1.5 rounded-lg mr-2 text-base">👩‍🍳</span>
							Instructions
						</h2>
						
						{#if !recipe.instructions || formatInstructions(recipe.instructions).length === 0}
							<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
								<p class="text-yellow-800 text-sm">⚠️ No instructions found. This might be due to extraction issues.</p>
							</div>
						{:else}
							<div class="space-y-3">
								{#each formatInstructions(recipe.instructions) as step, index}
									<div class="flex items-start p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
										<span class="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full text-xs flex items-center justify-center mr-3 font-bold">
											{index + 1}
										</span>
										<div class="flex-1">
											<p class="text-gray-900 text-sm leading-relaxed">{step}</p>
										</div>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Recipe Metadata -->
					<div class="bg-white rounded-xl shadow-sm border p-5">
						<h3 class="text-base font-bold text-gray-900 mb-3">📊 Details</h3>
						<dl class="grid grid-cols-2 gap-3 text-xs">
							<div class="text-center p-2 bg-gray-50 rounded-lg">
								<dt class="text-gray-600 font-medium">Created</dt>
								<dd class="text-gray-900 font-bold mt-1">
									{#if recipe.createdAt}
										{new Date(recipe.createdAt).toLocaleDateString()}
									{:else}
										Unknown
									{/if}
								</dd>
							</div>
							<div class="text-center p-2 bg-gray-50 rounded-lg">
								<dt class="text-gray-600 font-medium">Steps</dt>
								<dd class="text-gray-900 font-bold mt-1">{formatInstructions(recipe.instructions).length}</dd>
							</div>
						</dl>
					</div>
				</div>
			</div>
		{:else}
			<div class="text-center py-16">
				<h2 class="text-2xl font-bold text-gray-900 mb-4">Recipe Not Found</h2>
				<p class="text-gray-600 mb-6">The recipe you're looking for doesn't exist or has been removed.</p>
				<button
					on:click={() => goto('/')}
					class="btn btn-primary"
				>
					← Back to Recipes
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
				Are you sure you want to delete "<strong>{recipe?.title}</strong>"? This action cannot be undone.
			</p>
			<div class="flex space-x-4">
				<button
					on:click={() => deleteConfirm = false}
					class="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition-colors"
					disabled={isDeleting}
				>
					Cancel
				</button>
				<button
					on:click={deleteRecipe}
					class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors disabled:opacity-50"
					disabled={isDeleting}
				>
					{#if isDeleting}
						<span class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
						Deleting...
					{:else}
						Delete
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