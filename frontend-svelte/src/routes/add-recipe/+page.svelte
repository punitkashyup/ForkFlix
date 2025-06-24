<script>
	import { onMount } from 'svelte';
	import { user, loading, error } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	
	let instagramUrl = '';
	let extractedData = null;
	let isExtracting = false;
	let extractionError = '';
	let embedCode = '';
	let thumbnailUrl = '';
	let metadata = null;
	
	// Form fields for manual input
	let title = '';
	let category = 'Main Course';
	let cookingTime = 30;
	let difficulty = 'Medium';
	let ingredients = [''];
	let instructions = '';

	onMount(() => {
		// Redirect if not logged in
		if (!$user) {
			goto('/login');
		}
	});

	async function extractFromInstagram() {
		if (!instagramUrl) {
			extractionError = 'Please enter an Instagram URL';
			return;
		}

		try {
			isExtracting = true;
			extractionError = '';
			
			// Validate URL first
			const validation = await apiService.validateInstagramUrl(instagramUrl);
			if (!validation.isValid) {
				extractionError = validation.message;
				return;
			}

			// Get metadata (including thumbnail)
			try {
				metadata = await apiService.getInstagramMetadata(instagramUrl);
				thumbnailUrl = metadata.thumbnailUrl || '';
			} catch (err) {
				console.warn('Failed to get metadata:', err);
			}

			// Get embed code
			try {
				const embedResponse = await apiService.getInstagramEmbed(instagramUrl);
				embedCode = embedResponse.embedCode;
				console.log('🎬 Embed response:', embedResponse);
				console.log('📱 Embed code:', embedCode);
			} catch (err) {
				console.warn('Failed to get embed code:', err);
			}

			// Extract recipe data with AI
			const extraction = await apiService.extractRecipeFromInstagram(instagramUrl);
			extractedData = extraction;
			
			// Populate form with extracted data
			title = extractedData.ingredients?.slice(0, 3).join(', ') + ' Recipe' || '';
			category = extractedData.category || 'Main Course';
			cookingTime = extractedData.cookingTime || 30;
			difficulty = extractedData.difficulty || 'Medium';
			ingredients = extractedData.ingredients || [''];
			instructions = extractedData.instructions || '';

		} catch (err) {
			extractionError = 'Failed to extract recipe: ' + err.message;
			console.error('Extraction error:', err);
		} finally {
			isExtracting = false;
		}
	}

	async function saveRecipe() {
		if (!title || ingredients.filter(i => i.trim()).length === 0) {
			extractionError = 'Please provide a title and at least one ingredient';
			return;
		}

		try {
			loading.set(true);
			
			const recipeData = {
				instagramUrl,
				title: title.trim(),
				category,
				cookingTime: parseInt(cookingTime),
				difficulty,
				ingredients: ingredients.filter(i => i.trim()),
				instructions: instructions.trim(),
				embedCode,
				thumbnailUrl,
				aiExtracted: !!extractedData,
				isPublic: false
			};

			await apiService.createRecipe(recipeData);
			goto('/'); // Redirect to home after successful creation
			
		} catch (err) {
			extractionError = 'Failed to save recipe: ' + err.message;
			console.error('Save error:', err);
		} finally {
			loading.set(false);
		}
	}

	function addIngredient() {
		ingredients = [...ingredients, ''];
	}

	function removeIngredient(index) {
		ingredients = ingredients.filter((_, i) => i !== index);
	}
</script>

<svelte:head>
	<title>Add Recipe - ForkFlix</title>
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
				<h1 class="text-2xl font-bold text-gray-900">Add New Recipe</h1>
				<div></div>
			</div>
		</div>
	</header>

	<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
			<!-- Left Column: Instagram URL and AI Extraction -->
			<div class="space-y-6">
				<div class="card">
					<h2 class="text-xl font-semibold mb-4">🤖 AI Recipe Extraction</h2>
					
					<div class="space-y-4">
						<div>
							<label for="instagram-url" class="block text-sm font-medium text-gray-700 mb-2">
								Instagram URL
							</label>
							<input
								id="instagram-url"
								type="url"
								bind:value={instagramUrl}
								placeholder="https://www.instagram.com/reel/..."
								class="input"
							>
						</div>

						<button
							on:click={extractFromInstagram}
							disabled={isExtracting || !instagramUrl}
							class="btn btn-primary w-full {isExtracting ? 'opacity-50 cursor-not-allowed' : ''}"
						>
							{#if isExtracting}
								<div class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
								Extracting...
							{:else}
								🎯 Extract Recipe with AI
							{/if}
						</button>

						{#if extractionError}
							<div class="bg-red-50 border border-red-200 rounded-lg p-4">
								<p class="text-red-700 text-sm">{extractionError}</p>
							</div>
						{/if}

						{#if extractedData}
							<div class="bg-green-50 border border-green-200 rounded-lg p-4">
								<p class="text-green-700 text-sm">
									✅ Recipe extracted successfully! Confidence: {Math.round(extractedData.confidence * 100)}%
								</p>
							</div>
						{/if}
					</div>
				</div>

				<!-- Instagram Preview -->
				{#if embedCode || thumbnailUrl}
					<div class="card">
						<h3 class="text-lg font-semibold mb-4">📱 Instagram Preview</h3>
						{#if embedCode}
							<div class="instagram-embed">
								{@html embedCode}
							</div>
						{:else if thumbnailUrl}
							<!-- Fallback: show thumbnail if embed fails -->
							<img 
								src={thumbnailUrl} 
								alt="Recipe preview"
								class="w-full max-w-sm mx-auto rounded-lg shadow-sm"
							>
							<p class="text-sm text-gray-600 mt-2 text-center">
								Preview from Instagram
							</p>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Right Column: Recipe Form -->
			<div class="space-y-6">
				<div class="card">
					<h2 class="text-xl font-semibold mb-4">📝 Recipe Details</h2>
					
					<form on:submit|preventDefault={saveRecipe} class="space-y-4">
						<div>
							<label for="title" class="block text-sm font-medium text-gray-700 mb-2">
								Recipe Title *
							</label>
							<input
								id="title"
								type="text"
								bind:value={title}
								placeholder="Enter recipe title..."
								class="input"
								required
							>
						</div>

						<div class="grid grid-cols-2 gap-4">
							<div>
								<label for="category" class="block text-sm font-medium text-gray-700 mb-2">
									Category
								</label>
								<select id="category" bind:value={category} class="input">
									<option value="Starters">Starters</option>
									<option value="Main Course">Main Course</option>
									<option value="Desserts">Desserts</option>
									<option value="Beverages">Beverages</option>
									<option value="Snacks">Snacks</option>
								</select>
							</div>

							<div>
								<label for="difficulty" class="block text-sm font-medium text-gray-700 mb-2">
									Difficulty
								</label>
								<select id="difficulty" bind:value={difficulty} class="input">
									<option value="Easy">Easy</option>
									<option value="Medium">Medium</option>
									<option value="Hard">Hard</option>
								</select>
							</div>
						</div>

						<div>
							<label for="cooking-time" class="block text-sm font-medium text-gray-700 mb-2">
								Cooking Time (minutes)
							</label>
							<input
								id="cooking-time"
								type="number"
								bind:value={cookingTime}
								min="1"
								max="1440"
								class="input"
							>
						</div>

						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">
								Ingredients *
							</label>
							{#each ingredients as ingredient, index}
								<div class="flex gap-2 mb-2">
									<input
										type="text"
										bind:value={ingredients[index]}
										placeholder="Enter ingredient..."
										class="input flex-1"
									>
									{#if ingredients.length > 1}
										<button
											type="button"
											on:click={() => removeIngredient(index)}
											class="btn btn-secondary px-3"
										>
											✕
										</button>
									{/if}
								</div>
							{/each}
							<button
								type="button"
								on:click={addIngredient}
								class="btn btn-secondary text-sm"
							>
								+ Add Ingredient
							</button>
						</div>

						<div>
							<label for="instructions" class="block text-sm font-medium text-gray-700 mb-2">
								Instructions
							</label>
							<textarea
								id="instructions"
								bind:value={instructions}
								rows="6"
								placeholder="Enter cooking instructions..."
								class="input resize-y"
							></textarea>
						</div>

						<button
							type="submit"
							disabled={$loading}
							class="btn btn-primary w-full {$loading ? 'opacity-50 cursor-not-allowed' : ''}"
						>
							{#if $loading}
								<div class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
							{/if}
							💾 Save Recipe
						</button>
					</form>
				</div>
			</div>
		</div>
	</main>
</div>

<style>
	:global(.instagram-embed iframe) {
		max-width: 100%;
		margin: 0 auto;
	}
</style>