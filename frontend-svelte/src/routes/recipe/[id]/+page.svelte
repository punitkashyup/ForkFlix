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
					class="flex items-center text-gray-600 hover:text-gray-900"
				>
					← Back to Recipes
				</button>
				<h1 class="text-2xl font-bold text-gray-900">Recipe Details</h1>
				<div></div>
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
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
				<!-- Left Column: Recipe Details -->
				<div class="space-y-6">
					<!-- Recipe Header -->
					<div class="card">
						<h1 class="text-3xl font-bold text-gray-900 mb-4">{recipe.title}</h1>
						
						<div class="flex flex-wrap gap-4 mb-6">
							<span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
								{recipe.category}
							</span>
							<span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
								⏱️ {recipe.cookingTime} min
							</span>
							<span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
								📈 {recipe.difficulty}
							</span>
							{#if recipe.aiExtracted}
								<span class="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
									🤖 AI Extracted
								</span>
							{/if}
						</div>

						{#if recipe.thumbnailUrl}
							<img 
								src={recipe.thumbnailUrl} 
								alt={recipe.title}
								class="w-full h-64 object-cover rounded-lg mb-6 shadow-sm"
							>
						{/if}
					</div>

					<!-- Ingredients -->
					<div class="card">
						<h2 class="text-2xl font-semibold text-gray-900 mb-4">🥘 Ingredients</h2>
						<ul class="space-y-2">
							{#each formatIngredients(recipe.ingredients) as ingredient}
								<li class="flex items-start">
									<span class="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
									<span class="text-gray-700">{ingredient}</span>
								</li>
							{/each}
						</ul>
					</div>

					<!-- Instructions -->
					{#if recipe.instructions}
						<div class="card">
							<h2 class="text-2xl font-semibold text-gray-900 mb-4">👩‍🍳 Instructions</h2>
							<div class="prose prose-gray max-w-none">
								{@html recipe.instructions.replace(/\n/g, '<br>')}
							</div>
						</div>
					{/if}
				</div>

				<!-- Right Column: Instagram Embed -->
				<div class="space-y-6">
					{#if recipe.embedCode}
						<div class="card">
							<h2 class="text-2xl font-semibold text-gray-900 mb-4">📱 Original Instagram Post</h2>
							<div class="instagram-embed">
								{@html recipe.embedCode}
							</div>
						</div>
					{:else if recipe.instagramUrl}
						<div class="card">
							<h2 class="text-2xl font-semibold text-gray-900 mb-4">📱 Instagram Link</h2>
							<a 
								href={recipe.instagramUrl} 
								target="_blank" 
								rel="noopener noreferrer"
								class="btn btn-primary w-full"
							>
								View on Instagram →
							</a>
						</div>
					{/if}

					<!-- Recipe Metadata -->
					<div class="card">
						<h2 class="text-xl font-semibold text-gray-900 mb-4">📊 Recipe Info</h2>
						<dl class="space-y-2">
							<div class="flex justify-between">
								<dt class="text-gray-600">Category:</dt>
								<dd class="font-medium">{recipe.category}</dd>
							</div>
							<div class="flex justify-between">
								<dt class="text-gray-600">Cooking Time:</dt>
								<dd class="font-medium">{recipe.cookingTime} minutes</dd>
							</div>
							<div class="flex justify-between">
								<dt class="text-gray-600">Difficulty:</dt>
								<dd class="font-medium">{recipe.difficulty}</dd>
							</div>
							<div class="flex justify-between">
								<dt class="text-gray-600">Ingredients:</dt>
								<dd class="font-medium">{formatIngredients(recipe.ingredients).length} items</dd>
							</div>
							{#if recipe.createdAt}
								<div class="flex justify-between">
									<dt class="text-gray-600">Created:</dt>
									<dd class="font-medium">{new Date(recipe.createdAt).toLocaleDateString()}</dd>
								</div>
							{/if}
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