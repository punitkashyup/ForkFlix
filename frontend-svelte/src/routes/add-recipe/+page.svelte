<script>
	import { onMount } from 'svelte';
	import { user, loading, error } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
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
	
	// Edit mode variables
	let editMode = false;
	let editRecipeId = null;
	let originalRecipe = null;
	
	// URL validation state
	let urlValidation = { valid: false, message: '', isValidating: false };
	let apiValidation = null;
	let validationTimeout = null;
	let lastValidatedUrl = '';
	
	// Form fields for manual input
	let title = '';
	let category = 'Main Course';
	let cookingTime = 30;
	let difficulty = 'Medium';
	let ingredients = [''];
	let instructions = '';
	
	// Duplicate detection
	let isDuplicateUrl = false;
	let duplicateRecipe = null;

	onMount(async () => {
		// Redirect if not logged in
		if (!$user) {
			goto('/login');
			return;
		}
		
		// Check if we're in edit mode
		const editId = $page.url.searchParams.get('edit');
		if (editId) {
			editMode = true;
			editRecipeId = editId;
			await loadRecipeForEdit(editId);
		}
	});
	
	async function loadRecipeForEdit(recipeId) {
		try {
			loading.set(true);
			originalRecipe = await apiService.getRecipe(recipeId);
			
			// Pre-populate form with existing recipe data
			instagramUrl = originalRecipe.instagramUrl || '';
			title = originalRecipe.title || '';
			category = originalRecipe.category || 'Main Course';
			cookingTime = originalRecipe.cookingTime || 30;
			difficulty = originalRecipe.difficulty || 'Medium';
			ingredients = originalRecipe.ingredients && originalRecipe.ingredients.length > 0 
				? originalRecipe.ingredients 
				: [''];
			instructions = originalRecipe.instructions || '';
			embedCode = originalRecipe.embedCode || '';
			thumbnailUrl = originalRecipe.thumbnailUrl || '';
			
			// Set up extracted data for smart editor
			extractedData = {
				title: originalRecipe.title,
				category: originalRecipe.category,
				cookingTime: originalRecipe.cookingTime,
				difficulty: originalRecipe.difficulty,
				ingredients: originalRecipe.ingredients || [],
				instructions: originalRecipe.instructions || '',
				confidence: originalRecipe.confidence || 0.8
			};
			
			// Show smart editor since we have data
			showSmartEditor = true;
			
			console.log('✅ Loaded recipe for editing:', originalRecipe.title);
		} catch (err) {
			extractionError = 'Failed to load recipe for editing: ' + err.message;
			console.error('Error loading recipe for edit:', err);
		} finally {
			loading.set(false);
		}
	}

	// Handlers for multi-modal extraction
	function handleMultiModalCompleted(event) {
		const { result } = event.detail;
		extractionData = result; // Keep original extraction data for confidence analysis
		isExtracting = false;
		showSmartEditor = true;
		
		console.log('🔍 DEBUG: Raw extraction result received:', JSON.stringify(result, null, 2));
		
		// Handle Phase 5 Mistral AI structured data or fallback to Phase 4
		let recipeData;
		if (result?.recipe_data) {
			// Phase 5: Mistral AI structured data
			recipeData = result.recipe_data;
			console.log('✅ Using Phase 5 Mistral AI data:', JSON.stringify(recipeData, null, 2));
		} else {
			// Phase 4: AI Fusion data (fallback)
			recipeData = result;
			console.log('⚠️ Using Phase 4 AI Fusion data:', JSON.stringify(recipeData, null, 2));
		}
		
		console.log('🔍 DEBUG: Recipe data before transformation:', JSON.stringify(recipeData, null, 2));
		
		// Transform data to SmartRecipeEditor expected format
		let transformedIngredients;
		console.log('🔍 DEBUG: Processing ingredients:', recipeData.ingredients);
		if (recipeData.ingredients && Array.isArray(recipeData.ingredients)) {
			if (recipeData.ingredients.length > 0 && typeof recipeData.ingredients[0] === 'object') {
				// Mistral AI format: [{name: "...", amount: "...", unit: "..."}]
				transformedIngredients = recipeData.ingredients.map(ing => 
					`${ing.amount || ''} ${ing.unit || ''} ${ing.name || ''}`.trim()
				).filter(ing => ing.length > 0);
				console.log('🔍 DEBUG: Transformed ingredients (object format):', transformedIngredients);
			} else {
				// Simple string array format
				transformedIngredients = recipeData.ingredients.filter(ing => ing && ing.trim());
				console.log('🔍 DEBUG: Transformed ingredients (string array):', transformedIngredients);
			}
		} else {
			transformedIngredients = [''];
			console.log('🔍 DEBUG: No ingredients found, using default empty array');
		}
		
		// Transform instructions
		let transformedInstructions;
		console.log('🔍 DEBUG: Processing instructions:', recipeData.instructions);
		if (recipeData.instructions && Array.isArray(recipeData.instructions)) {
			transformedInstructions = recipeData.instructions.join('\n');
			console.log('🔍 DEBUG: Transformed instructions (array format):', transformedInstructions);
		} else {
			transformedInstructions = recipeData.instructions || '';
			console.log('🔍 DEBUG: Transformed instructions (string format):', transformedInstructions);
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
		
		console.log('🔍 DEBUG: Final extractedData object:', JSON.stringify(extractedData, null, 2));
		
		// Populate basic form fields with structured data
		title = extractedData.title;
		category = extractedData.category;
		cookingTime = extractedData.cookingTime;
		difficulty = extractedData.difficulty;
		ingredients = extractedData.ingredients.length > 0 ? extractedData.ingredients : [''];
		instructions = extractedData.instructions;
		
		console.log('🔍 DEBUG: Form variables after population:');
		console.log('  - title:', title);
		console.log('  - category:', category);
		console.log('  - cookingTime:', cookingTime);
		console.log('  - difficulty:', difficulty);
		console.log('  - ingredients:', JSON.stringify(ingredients, null, 2));
		console.log('  - instructions:', instructions);
		
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
		console.log('🔍 DEBUG: saveRecipe called');
		console.log('🔍 DEBUG: Edit mode:', editMode);
		console.log('🔍 DEBUG: Current form state:');
		console.log('  - title:', title);
		console.log('  - category:', category);
		console.log('  - cookingTime:', cookingTime);
		console.log('  - difficulty:', difficulty);
		console.log('  - ingredients:', JSON.stringify(ingredients, null, 2));
		console.log('  - instructions:', instructions);
		console.log('🔍 DEBUG: extractedData:', JSON.stringify(extractedData, null, 2));
		
		// Use current form values or extracted data
		const currentTitle = title || extractedData?.title;
		const currentIngredients = ingredients.length > 0 && ingredients.some(i => i.trim()) 
			? ingredients 
			: extractedData?.ingredients || [];
		
		console.log('🔍 DEBUG: Computed values for save:');
		console.log('  - currentTitle:', currentTitle);
		console.log('  - currentIngredients:', JSON.stringify(currentIngredients, null, 2));
		
		if (!currentTitle || currentIngredients.filter(i => i.trim()).length === 0) {
			extractionError = 'Please provide a title and at least one ingredient';
			return;
		}

		try {
			loading.set(true);
			
			const recipeData = {
				instagramUrl,
				title: currentTitle.trim(),
				category: category || extractedData?.category,
				cookingTime: parseInt(cookingTime || extractedData?.cookingTime || 30),
				difficulty: difficulty || extractedData?.difficulty || 'Medium',
				ingredients: currentIngredients.filter(i => i.trim()),
				instructions: (instructions || extractedData?.instructions || '').trim(),
				embedCode,
				thumbnailUrl,
				aiExtracted: !!extractedData,
				isPublic: false,
				// Add extraction metadata
				extractionMethod: extractedData?._extractionMethod,
				confidence: extractedData?.confidence
			};

			console.log('🔍 DEBUG: Final recipe payload before API call:', JSON.stringify(recipeData, null, 2));

			if (editMode && editRecipeId) {
				// Update existing recipe
				await apiService.updateRecipe(editRecipeId, recipeData);
				alert('🎉 Recipe updated successfully! Redirecting to recipe details...');
				goto(`/recipe/${editRecipeId}`);
			} else {
				// Create new recipe
				await apiService.createRecipe(recipeData);
				alert('🎉 Recipe saved successfully! Redirecting to your collection...');
				goto('/');
			}
			
			// Show success message before redirect
			extractionError = '';
			
		} catch (err) {
			extractionError = `Failed to ${editMode ? 'update' : 'save'} recipe: ` + err.message;
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
		console.log('🔍 DEBUG: Smart editor save triggered with data:', JSON.stringify(editedData, null, 2));
		
		// Use edited data from smart editor
		extractedData = editedData;
		title = editedData.title;
		category = editedData.category;
		cookingTime = editedData.cookingTime;
		difficulty = editedData.difficulty;
		ingredients = editedData.ingredients;
		instructions = editedData.instructions;
		
		console.log('🔍 DEBUG: Form variables updated from smart editor:');
		console.log('  - title:', title);
		console.log('  - category:', category);
		console.log('  - cookingTime:', cookingTime);
		console.log('  - difficulty:', difficulty);
		console.log('  - ingredients:', JSON.stringify(ingredients, null, 2));
		console.log('  - instructions:', instructions);
		
		// Save the recipe
		saveRecipe();
	}
	
	function handleChangeStatus(event) {
		const { hasUnsavedChanges } = event.detail;
		// Handle unsaved changes status if needed
		console.log('Has unsaved changes:', hasUnsavedChanges);
	}
	
	// URL validation functions
	function validateUrlFormat(url) {
		const urlPattern = /^https?:\/\/(www\.)?instagram\.com\/(p|reel|tv)\/[A-Za-z0-9_-]+\/?/;
		
		if (!url || url.trim() === '') {
			return { valid: false, message: '' };
		}
		
		if (!urlPattern.test(url.trim())) {
			return { 
				valid: false, 
				message: 'Please enter a valid Instagram post, reel, or TV video URL' 
			};
		}
		
		return { valid: true, message: 'URL format looks good' };
	}
	
	function normalizeUrl(url) {
		if (!url) return '';
		
		let cleanUrl = url.trim();
		
		// Remove tracking parameters
		cleanUrl = cleanUrl.split('?')[0];
		
		// Ensure it starts with https://
		if (!cleanUrl.startsWith('http')) {
			cleanUrl = 'https://' + cleanUrl;
		}
		
		// Ensure it ends with / for consistency
		if (!cleanUrl.endsWith('/')) {
			cleanUrl += '/';
		}
		
		return cleanUrl;
	}
	
	// Reactive validation whenever URL changes with debouncing
	$: {
		if (instagramUrl) {
			urlValidation = validateUrlFormat(instagramUrl);
			
			// Only reset API validation if URL actually changed from user input
			// Don't trigger if it's just a normalization from API validation
			const normalizedUrl = normalizeUrl(instagramUrl);
			if (normalizedUrl !== lastValidatedUrl && !urlValidation.isValidating) {
				apiValidation = null;
				// Reset duplicate detection when URL changes
				isDuplicateUrl = false;
				duplicateRecipe = null;
				
				// Clear existing timeout
				if (validationTimeout) {
					clearTimeout(validationTimeout);
				}
				
				// Auto-validate after user stops typing (800ms delay)
				if (urlValidation.valid) {
					validationTimeout = setTimeout(() => {
						validateUrlWithAPI();
					}, 800);
				}
			}
		} else {
			urlValidation = { valid: false, message: '', isValidating: false };
			apiValidation = null;
			lastValidatedUrl = '';
			isDuplicateUrl = false;
			duplicateRecipe = null;
			if (validationTimeout) {
				clearTimeout(validationTimeout);
			}
		}
	}
	
	async function validateUrlWithAPI() {
		if (!urlValidation.valid) return;
		
		const normalizedUrl = normalizeUrl(instagramUrl);
		
		// Don't validate if already validating this URL or already validated
		if (urlValidation.isValidating || lastValidatedUrl === normalizedUrl) {
			return;
		}
		
		console.log('🔍 Starting API validation for:', normalizedUrl);
		urlValidation.isValidating = true;
		lastValidatedUrl = normalizedUrl;
		
		try {
			const result = await apiService.validateMultiModalUrl(normalizedUrl);
			console.log('✅ Validation result:', result);
			apiValidation = result;
			
			// Check for duplicate URLs (unless we're editing the same recipe)
			await checkForDuplicateUrl(normalizedUrl);
			
		} catch (error) {
			console.error('❌ Validation error:', error);
			apiValidation = {
				valid: false,
				message: 'Failed to validate URL. Please check your connection.',
				error: error.message
			};
		} finally {
			urlValidation.isValidating = false;
		}
	}
	
	async function checkForDuplicateUrl(url) {
		if (!url || editMode) return; // Skip duplicate check in edit mode
		
		try {
			// Get all user recipes to check for duplicates
			const response = await apiService.getRecipes({ page: 1, limit: 100 });
			const userRecipes = response.items || [];
			
			// Check if any existing recipe has the same Instagram URL
			const existingRecipe = userRecipes.find(recipe => 
				recipe.instagramUrl && 
				normalizeUrl(recipe.instagramUrl) === url
			);
			
			if (existingRecipe) {
				isDuplicateUrl = true;
				duplicateRecipe = existingRecipe;
				console.log('⚠️ Duplicate URL found:', existingRecipe.title);
			} else {
				isDuplicateUrl = false;
				duplicateRecipe = null;
			}
		} catch (error) {
			console.error('Error checking for duplicate URL:', error);
			// Don't block the user if duplicate check fails
		}
	}
	
	// Handle paste events for immediate validation
	async function handleUrlPaste(event) {
		console.log('📋 Paste event detected');
		// Wait for the paste to complete
		setTimeout(() => {
			const normalizedUrl = normalizeUrl(instagramUrl);
			if (urlValidation.valid && normalizedUrl !== lastValidatedUrl && !urlValidation.isValidating) {
				console.log('📋 Validating pasted URL immediately');
				// Clear any existing timeout and validate immediately on paste
				if (validationTimeout) {
					clearTimeout(validationTimeout);
				}
				validateUrlWithAPI();
			}
		}, 100);
	}
</script>

<svelte:head>
	<title>{editMode ? 'Edit Recipe' : 'Add Recipe'} - ForkFlix</title>
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
				<h1 class="text-2xl font-bold text-gray-900">
					{editMode ? `Edit Recipe${originalRecipe ? ': ' + originalRecipe.title : ''}` : 'Add New Recipe'}
				</h1>
				<div></div>
			</div>
		</div>
	</header>

	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Left Column: Instagram URL and AI Extraction -->
			<div class="space-y-6">
				<div class="card">
					<h2 class="text-xl font-semibold mb-4">🤖 Enhanced AI Recipe Extraction</h2>
					
					<div class="space-y-4">
						<div>
							<label for="instagram-url" class="block text-sm font-medium text-gray-700 mb-2">
								Instagram URL
							</label>
							<div class="relative">
								<input
									id="instagram-url"
									type="url"
									bind:value={instagramUrl}
									on:paste={handleUrlPaste}
									placeholder="https://www.instagram.com/reel/..."
									class="input pr-10 {
										instagramUrl && urlValidation.valid && apiValidation?.valid ? 'border-green-500' : 
										instagramUrl && !urlValidation.valid ? 'border-red-500' : 
										instagramUrl && urlValidation.valid && urlValidation.isValidating ? 'border-blue-500' : ''
									}"
								>
								
								<!-- Status indicators -->
								<div class="absolute right-3 top-3">
									{#if urlValidation.isValidating}
										<!-- Loading spinner -->
										<div class="animate-spin h-4 w-4 border-b-2 border-blue-500 rounded-full"></div>
									{:else if instagramUrl && urlValidation.valid && apiValidation?.valid}
										<!-- Success check -->
										<div class="h-4 w-4 text-green-500">✓</div>
									{:else if instagramUrl && !urlValidation.valid}
										<!-- Error X -->
										<div class="h-4 w-4 text-red-500">✗</div>
									{:else if instagramUrl && urlValidation.valid && apiValidation === null}
										<!-- Validating indicator -->
										<div class="h-4 w-4 text-blue-500">⏳</div>
									{/if}
								</div>
							</div>
							
							<!-- Validation Messages -->
							{#if instagramUrl && !urlValidation.valid}
								<div class="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">
									❌ {urlValidation.message}
								</div>
							{/if}
							
							{#if urlValidation.valid && !apiValidation && !urlValidation.isValidating}
								<div class="mt-2 text-sm text-blue-600 bg-blue-50 border border-blue-200 rounded p-2">
									⏱️ Auto-validating URL accessibility...
								</div>
							{/if}
							
							{#if urlValidation.isValidating}
								<div class="mt-2 text-sm text-blue-600 bg-blue-50 border border-blue-200 rounded p-2">
									🔍 Checking URL accessibility and content quality...
								</div>
							{/if}
							
							<!-- API Validation Results -->
							{#if apiValidation}
								{#if apiValidation.valid}
									<div class="mt-2 text-sm text-green-600 bg-green-50 border border-green-200 rounded p-3">
										<div class="font-medium">✅ {apiValidation.message}</div>
										<div class="flex items-center gap-2 mt-1">
											<span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
												{apiValidation.post_type?.toUpperCase() || 'POST'}
											</span>
											<span class="text-xs text-green-700">
												{apiValidation.accessible ? 'Accessible' : 'Format valid'}
											</span>
										</div>
										{#if apiValidation.extraction_estimate}
											<div class="mt-2 text-xs text-green-700">
												⏱️ Estimated extraction time: {apiValidation.extraction_estimate.estimated_time}
											</div>
										{/if}
									</div>
								{:else}
									<div class="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded p-3">
										<div class="font-medium">❌ {apiValidation.message}</div>
										{#if apiValidation.suggestions}
											<ul class="mt-2 text-xs space-y-1">
												{#each apiValidation.suggestions as suggestion}
													<li>• {suggestion}</li>
												{/each}
											</ul>
										{/if}
									</div>
								{/if}
							{/if}
							
							<!-- Duplicate URL Warning -->
							{#if isDuplicateUrl && duplicateRecipe}
								<div class="mt-2 text-sm text-orange-600 bg-orange-50 border border-orange-200 rounded p-3">
									<div class="font-medium">⚠️ Recipe Already Exists</div>
									<p class="mt-1 text-xs text-orange-700">
										You already have a recipe for this Instagram post: 
										<strong>"{duplicateRecipe.title}"</strong>
									</p>
									<div class="mt-2 flex gap-2">
										<button 
											on:click={() => goto(`/recipe/${duplicateRecipe.id}`)}
											class="text-xs bg-orange-100 hover:bg-orange-200 text-orange-800 px-2 py-1 rounded transition-colors"
										>
											View Existing Recipe
										</button>
										<button 
											on:click={() => goto(`/add-recipe?edit=${duplicateRecipe.id}`)}
											class="text-xs bg-orange-100 hover:bg-orange-200 text-orange-800 px-2 py-1 rounded transition-colors"
										>
											Edit Existing Recipe
										</button>
									</div>
								</div>
							{/if}
						</div>

						<!-- Extraction Method Toggle -->
						{#if !editMode}
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
						{:else}
							<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
								<div class="flex items-center space-x-3">
									<div class="h-4 w-4 bg-green-500 rounded-full flex items-center justify-center">
										<span class="text-white text-xs">✓</span>
									</div>
									<div>
										<span class="text-sm font-medium text-gray-700">
											Recipe Already Extracted
										</span>
										<p class="text-xs text-gray-600">
											Editing existing recipe data. No re-extraction needed.
										</p>
									</div>
								</div>
							</div>
						{/if}

						{#if useAdvancedExtraction}
							<!-- Multi-Modal Extraction Component -->
							{#if isDuplicateUrl}
								<div class="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
									<p class="text-orange-800 text-sm">
										⚠️ Cannot extract recipe - this Instagram URL is already saved. 
										Please use the buttons above to view or edit the existing recipe.
									</p>
								</div>
							{:else if apiValidation?.valid}
								<MultiModalExtraction
									bind:instagramUrl={instagramUrl}
									on:completed={handleMultiModalCompleted}
									on:error={handleMultiModalError}
									on:cancelled={handleMultiModalCancelled}
									on:phaseUpdate={handlePhaseUpdate}
								/>
							{:else}
								<div class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
									<p class="text-gray-600 text-sm">
										{#if !instagramUrl}
											Enter an Instagram URL to begin extraction
										{:else if !urlValidation.valid}
											Please enter a valid Instagram URL
										{:else if !apiValidation}
											Please validate the URL first
										{:else}
											URL validation failed - please fix the issues above
										{/if}
									</p>
								</div>
							{/if}
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
						
						<!-- Prominent Save Button Always Visible -->
						<div class="mt-6 pt-6 border-t border-gray-200">
							<div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
								<div class="flex items-center">
									<div class="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
										<span class="text-green-600">✓</span>
									</div>
									<div class="ml-3">
										<h4 class="text-sm font-medium text-green-800">Recipe extraction completed!</h4>
										<p class="text-sm text-green-700">Review the details above and save your recipe when ready.</p>
									</div>
								</div>
							</div>
							
							<button
								on:click={() => saveRecipe()}
								disabled={$loading}
								class="btn btn-primary w-full text-lg py-4 {$loading ? 'opacity-50 cursor-not-allowed' : ''}"
							>
								{#if $loading}
									<div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
								{/if}
								{editMode ? '✏️ Update Recipe' : '💾 Save Recipe to Collection'}
							</button>
							
							<p class="text-center text-sm text-gray-600 mt-3">
								You can always edit the recipe details above before {editMode ? 'updating' : 'saving'}
							</p>
						</div>
					</div>
				{:else}
					<!-- Basic Recipe Form -->
					<div class="card">
						<h2 class="text-xl font-semibold mb-4">📝 Recipe Details</h2>
					
					<form on:submit|preventDefault={saveRecipe} class="form-tablet">
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

						<div class="form-group-tablet">
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
							{editMode ? '✏️ Update Recipe' : '💾 Save Recipe'}
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