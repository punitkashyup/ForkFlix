<script>
	import { onMount } from 'svelte';
	import { user, loading, error } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import MultiModalExtraction from '$lib/components/MultiModalExtraction.svelte';
	import SmartRecipeEditor from '$lib/components/SmartRecipeEditor.svelte';
	
	let instagramUrl = '';
	let extractedData = null;
	let extractionData = null;
	let isExtracting = false;
	let extractionError = '';
	let embedCode = '';
	let thumbnailUrl = '';
	let metadata = null;
	let useAdvancedExtraction = true;
	let showSmartEditor = false;
	
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

	// Handlers for multi-modal extraction
	function handleMultiModalCompleted(event) {
		const { result } = event.detail;
		extractionData = result; // Keep original extraction data for confidence analysis
		isExtracting = false;
		showSmartEditor = true;
		
		// Handle Phase 5 Mistral AI structured data or fallback to Phase 4
		let recipeData;
		if (result?.recipe_data) {
			// Phase 5: Mistral AI structured data
			recipeData = result.recipe_data;
			console.log('✅ Using Phase 5 Mistral AI data:', recipeData);
		} else {
			// Phase 4: AI Fusion data (fallback)
			recipeData = result;
			console.log('⚠️ Using Phase 4 AI Fusion data:', recipeData);
		}
		
		// Transform data to SmartRecipeEditor expected format
		let transformedIngredients;
		if (recipeData.ingredients && Array.isArray(recipeData.ingredients)) {
			if (recipeData.ingredients.length > 0 && typeof recipeData.ingredients[0] === 'object') {
				// Mistral AI format: [{name: "...", amount: "...", unit: "..."}]
				transformedIngredients = recipeData.ingredients.map(ing => 
					`${ing.amount || ''} ${ing.unit || ''} ${ing.name || ''}`.trim()
				).filter(ing => ing.length > 0);
			} else {
				// Simple string array format
				transformedIngredients = recipeData.ingredients.filter(ing => ing && ing.trim());
			}
		} else {
			transformedIngredients = [''];
		}
		
		// Transform instructions
		let transformedInstructions;
		if (recipeData.instructions && Array.isArray(recipeData.instructions)) {
			transformedInstructions = recipeData.instructions.join('\n');
		} else {
			transformedInstructions = recipeData.instructions || '';
		}
		
		// Create transformed data for SmartRecipeEditor
		extractedData = {
			title: recipeData.recipe_name || recipeData.title || '',
			category: recipeData.category || 'Main Course',
			cookingTime: recipeData.cooking_time?.total_minutes || recipeData.cookingTime || 30,
			difficulty: recipeData.difficulty || 'Medium',
			ingredients: transformedIngredients,
			instructions: transformedInstructions,
			// Keep original data for reference
			_originalData: recipeData,
			_extractionMethod: result?.recipe_data ? 'mistral_ai' : 'ai_fusion',
			confidence: result.confidence || 0.8
		};
		
		// Populate basic form fields with structured data
		title = extractedData.title;
		category = extractedData.category;
		cookingTime = extractedData.cookingTime;
		difficulty = extractedData.difficulty;
		ingredients = extractedData.ingredients.length > 0 ? extractedData.ingredients : [''];
		instructions = extractedData.instructions;
		
		console.log('✅ Transformed data for SmartRecipeEditor:', extractedData);
	}
	
	function handleMultiModalError(event) {
		const { error } = event.detail;
		extractionError = error;
		isExtracting = false;
	}
	
	function handleMultiModalCancelled() {
		isExtracting = false;
	}
	
	function handlePhaseUpdate(event) {
		// Handle real-time phase updates if needed
		console.log('Phase update:', event.detail);
	}

	async function extractFromInstagram() {
		if (!instagramUrl) {
			extractionError = 'Please enter an Instagram URL';
			return;
		}

		try {
			isExtracting = true;
			extractionError = '';
			
			// Get metadata for embed code
			try {
				metadata = await apiService.getInstagramMetadata(instagramUrl);
				thumbnailUrl = metadata.thumbnailUrl || '';
				
				const embedResponse = await apiService.getInstagramEmbed(instagramUrl);
				embedCode = embedResponse.embedCode;
			} catch (err) {
				console.warn('Failed to get metadata/embed:', err);
			}

			if (useAdvancedExtraction) {
				// Multi-modal extraction will be handled by the component
				return;
			}

			// Legacy extraction method
			const validation = await apiService.validateInstagramUrl(instagramUrl);
			if (!validation.isValid) {
				extractionError = validation.message;
				return;
			}

			const extraction = await apiService.extractRecipeFromInstagram(instagramUrl);
			extractedData = extraction;
			
			// Populate form with extracted data (legacy format)
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
			if (!useAdvancedExtraction) {
				isExtracting = false;
			}
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
	
	// Smart editor handlers
	function handleSmartEditorSave(event) {
		const { editedData } = event.detail;
		// Use edited data from smart editor
		extractedData = editedData;
		title = editedData.title;
		category = editedData.category;
		cookingTime = editedData.cookingTime;
		difficulty = editedData.difficulty;
		ingredients = editedData.ingredients;
		instructions = editedData.instructions;
		
		// Save the recipe
		saveRecipe();
	}
	
	function handleChangeStatus(event) {
		const { hasUnsavedChanges } = event.detail;
		// Handle unsaved changes status if needed
		console.log('Has unsaved changes:', hasUnsavedChanges);
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
					<h2 class="text-xl font-semibold mb-4">🤖 Enhanced AI Recipe Extraction</h2>
					
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

						<!-- Extraction Method Toggle -->
						<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
							<label class="flex items-center space-x-3">
								<input
									type="checkbox"
									bind:checked={useAdvancedExtraction}
									class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
								>
								<div>
									<span class="text-sm font-medium text-blue-900">
										Use Advanced Multi-Modal Extraction + Mistral AI
									</span>
									<p class="text-xs text-blue-700">
										5-phase processing: text, video, audio, AI fusion + Mistral AI for 95%+ accuracy
									</p>
								</div>
							</label>
						</div>

						{#if useAdvancedExtraction}
							<!-- Multi-Modal Extraction Component -->
							<MultiModalExtraction
								bind:instagramUrl={instagramUrl}
								on:completed={handleMultiModalCompleted}
								on:error={handleMultiModalError}
								on:cancelled={handleMultiModalCancelled}
								on:phaseUpdate={handlePhaseUpdate}
							/>
						{:else}
							<!-- Legacy Extraction -->
							<button
								on:click={extractFromInstagram}
								disabled={isExtracting || !instagramUrl}
								class="btn btn-primary w-full {isExtracting ? 'opacity-50 cursor-not-allowed' : ''}"
							>
								{#if isExtracting}
									<div class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
									Extracting...
								{:else}
									🎯 Extract Recipe with Basic AI
								{/if}
							</button>
						{/if}

						{#if extractionError}
							<div class="bg-red-50 border border-red-200 rounded-lg p-4">
								<p class="text-red-700 text-sm">{extractionError}</p>
							</div>
						{/if}

						{#if extractedData && !useAdvancedExtraction}
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
				{#if showSmartEditor && extractedData}
					<!-- Smart Recipe Editor with Confidence Scores -->
					<div class="card">
						<SmartRecipeEditor
							bind:recipeData={extractedData}
							bind:extractionData={extractionData}
							on:save={handleSmartEditorSave}
							on:changeStatus={handleChangeStatus}
						/>
					</div>
				{:else}
					<!-- Basic Recipe Form -->
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
				{/if}
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