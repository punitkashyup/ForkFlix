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
		if (!instructions) return '';
		
		// Handle array format (numbered steps)
		if (Array.isArray(instructions)) {
			return instructions
				.filter(step => step && step.trim())
				.map((step, index) => `${index + 1}. ${step.trim()}`)
				.join('\n');
		}
		
		// Handle string format with better formatting
		return instructions
			.split('\n')
			.filter(line => line.trim())
			.map(line => line.trim())
			.join('\n');
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
	<!-- Header -->
	<header class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<button
					on:click={() => goto('/')}
					class="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
				>
					← Back to Recipes
				</button>
				<h1 class="text-2xl font-bold text-gray-900">Recipe Details</h1>
				
				<!-- Action Buttons -->
				{#if recipe}
					<div class="flex items-center space-x-3">
						<button
							on:click={editRecipe}
							class="flex items-center px-4 py-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
							title="Edit Recipe"
						>
							✏️ Edit
						</button>
						<button
							on:click={() => deleteConfirm = true}
							class="flex items-center px-4 py-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
							title="Delete Recipe"
						>
							🗑️ Delete
						</button>
					</div>
				{:else}
					<div></div>
				{/if}
			</div>
		</div>
	</header>

	<main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		{#if recipeLoading}
			<div class="text-center py-8">
				<Loading message="Loading recipe..." />
			</div>
		{:else if recipeError}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4">
				<p class="text-red-700">{recipeError}</p>
			</div>
		{:else if recipe}
			<div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
				<!-- Left Column: Instagram Video/Post (1/3 width) -->
				<div class="xl:col-span-1 space-y-6">
					{#if recipe.embedCode}
						<div class="card sticky top-8">
							<h2 class="text-xl font-semibold text-gray-900 mb-4">📱 Original Post</h2>
							<div class="instagram-embed">
								{@html recipe.embedCode}
							</div>
						</div>
					{:else if recipe.instagramUrl}
						<div class="card sticky top-8">
							<h2 class="text-xl font-semibold text-gray-900 mb-4">📱 Instagram Link</h2>
							<a 
								href={recipe.instagramUrl} 
								target="_blank" 
								rel="noopener noreferrer"
								class="btn btn-primary w-full mb-4"
							>
								View on Instagram →
							</a>
							<!-- Show thumbnail only if no embed available -->
							{#if recipe.thumbnailUrl}
								<img 
									src={recipe.thumbnailUrl} 
									alt={recipe.title}
									class="w-full h-48 object-cover rounded-lg shadow-sm"
								>
							{/if}
						</div>
					{:else if recipe.thumbnailUrl}
						<!-- Fallback thumbnail when no Instagram data available -->
						<div class="card sticky top-8">
							<h2 class="text-xl font-semibold text-gray-900 mb-4">🖼️ Recipe Image</h2>
							<img 
								src={recipe.thumbnailUrl} 
								alt={recipe.title}
								class="w-full h-64 object-cover rounded-lg shadow-sm"
							>
						</div>
					{/if}

					<!-- Recipe Metadata -->
					<div class="card">
						<h2 class="text-lg font-semibold text-gray-900 mb-4">📊 Recipe Info</h2>
						<dl class="space-y-3">
							<div class="flex justify-between items-center">
								<dt class="text-gray-600 text-sm">Category:</dt>
								<dd class="font-medium text-sm">
									<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
										{recipe.category}
									</span>
								</dd>
							</div>
							<div class="flex justify-between items-center">
								<dt class="text-gray-600 text-sm">Time:</dt>
								<dd class="font-medium text-sm">
									<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
										⏱️ {recipe.cookingTime} min
									</span>
								</dd>
							</div>
							<div class="flex justify-between items-center">
								<dt class="text-gray-600 text-sm">Difficulty:</dt>
								<dd class="font-medium text-sm">
									<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">
										📈 {recipe.difficulty}
									</span>
								</dd>
							</div>
							<div class="flex justify-between items-center">
								<dt class="text-gray-600 text-sm">Ingredients:</dt>
								<dd class="font-medium text-sm">{formatIngredients(recipe.ingredients).length} items</dd>
							</div>
							{#if recipe.aiExtracted}
								<div class="flex justify-between items-center">
									<dt class="text-gray-600 text-sm">Extraction:</dt>
									<dd class="font-medium text-sm">
										<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">
											🤖 AI Extracted
										</span>
									</dd>
								</div>
							{/if}
							{#if recipe.createdAt}
								<div class="flex justify-between items-center">
									<dt class="text-gray-600 text-sm">Created:</dt>
									<dd class="font-medium text-sm">{new Date(recipe.createdAt).toLocaleDateString()}</dd>
								</div>
							{/if}
						</dl>
					</div>
				</div>

				<!-- Right Column: Recipe Content (2/3 width) -->
				<div class="xl:col-span-2 space-y-6">
					<!-- Recipe Header -->
					<div class="card">
						<h1 class="text-4xl font-bold text-gray-900 mb-2">{recipe.title}</h1>
						<p class="text-gray-600 text-lg">
							A delicious {recipe.category.toLowerCase()} recipe 
							{#if recipe.aiExtracted}extracted using AI{/if}
						</p>
					</div>

					<!-- Ingredients -->
					<div class="card">
						<h2 class="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
							<span class="bg-orange-100 text-orange-600 p-2 rounded-lg mr-3">🥘</span>
							Ingredients ({formatIngredients(recipe.ingredients).length})
						</h2>
						
						{#if formatIngredients(recipe.ingredients).length === 0}
							<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
								<p class="text-yellow-800">No ingredients found. This might be due to extraction issues.</p>
							</div>
						{:else}
							<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
								{#each formatIngredients(recipe.ingredients) as ingredient, index}
									<div class="flex items-start p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
										<span class="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full text-xs flex items-center justify-center mr-3 mt-0.5">
											{index + 1}
										</span>
										<span class="text-gray-800 font-medium">{ingredient}</span>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Instructions -->
					<div class="card">
						<h2 class="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
							<span class="bg-green-100 text-green-600 p-2 rounded-lg mr-3">👩‍🍳</span>
							Instructions
						</h2>
						
						{#if !recipe.instructions || !formatInstructions(recipe.instructions)}
							<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
								<p class="text-yellow-800">No instructions found. This might be due to extraction issues.</p>
							</div>
						{:else}
							<div class="prose prose-lg max-w-none">
								<div class="bg-gray-50 rounded-lg p-6">
									{@html formatInstructions(recipe.instructions).replace(/\n/g, '<br>')}
								</div>
							</div>
						{/if}
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