<script>
	import { onMount } from 'svelte';
	import { user, recipes, loading, error, authInitialized } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import { PAGINATION } from '$lib/config/constants.js';
	import { signOut } from 'firebase/auth';
	import { auth } from '$lib/config/firebase.js';
	import Loading from '$lib/components/Loading.svelte';
	import LandingPage from '$lib/components/LandingPage.svelte';
	
	let searchTerm = '';
	let selectedCategory = '';
	let filteredRecipes = [];
	let showUserMenu = false;
	let hasAttemptedFetch = false;
	
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
		goto('/add-recipe');
	}

	async function handleLogout() {
		try {
			await signOut(auth);
			// The auth state listener in +layout.svelte will handle clearing the user store
			goto('/');
		} catch (err) {
			console.error('Logout error:', err);
			error.set('Failed to logout');
		}
	}

	// Close dropdown when clicking outside
	function handleClickOutside(event) {
		if (showUserMenu && !event.target.closest('.user-menu')) {
			showUserMenu = false;
		}
	}
</script>

<svelte:head>
	<title>ForkFlix - Recipe Manager</title>
</svelte:head>

<div class="min-h-screen bg-gray-50" on:click={handleClickOutside}>
	<!-- Header -->
	<header class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<h1 class="text-2xl font-bold text-gray-900">🍴 ForkFlix</h1>
				</div>
				
				<div class="flex items-center space-x-4">
					{#if $user}
						<button
							on:click={handleAddRecipe}
							class="btn btn-primary"
						>
							Add Recipe
						</button>
						<div class="relative user-menu">
							<button 
								on:click={() => showUserMenu = !showUserMenu}
								class="flex items-center space-x-2 hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors"
							>
								{#if $user.photoURL}
									<img 
										src={$user.photoURL} 
										alt="Profile" 
										class="w-8 h-8 rounded-full"
									>
								{:else}
									<div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
										{($user.displayName || $user.email || 'U').charAt(0).toUpperCase()}
									</div>
								{/if}
								<span class="text-sm font-medium">{$user.displayName || $user.email}</span>
								<svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
								</svg>
							</button>
							
							{#if showUserMenu}
								<div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border">
									<button
										on:click={() => { showUserMenu = false; goto('/profile'); }}
										class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
									>
										👤 Profile
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
						<button
							on:click={handleLogin}
							class="btn btn-primary"
						>
							Login
						</button>
					{/if}
				</div>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main>
		{#if !$user}
			<LandingPage />
		{:else}
			<!-- Logged-in user content -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<h2 class="heading-tablet-responsive font-bold text-gray-900 mb-6">Your Recipes</h2>
				
				<!-- Search and Filter -->
				<div class="flex flex-col sm:flex-row gap-4 mb-6">
					<input
						type="text"
						placeholder="Search recipes..."
						bind:value={searchTerm}
						class="input flex-1"
					>
					<select bind:value={selectedCategory} class="input sm:w-48">
						<option value="">All Categories</option>
						<option value="Starters">Starters</option>
						<option value="Main Course">Main Course</option>
						<option value="Desserts">Desserts</option>
						<option value="Beverages">Beverages</option>
						<option value="Snacks">Snacks</option>
					</select>
				</div>

				<!-- Loading State -->
				{#if $loading}
					<div class="text-center py-8">
						<Loading message="Loading recipes..." />
					</div>
				{:else if $error}
					<div class="bg-red-50 border border-red-200 rounded-lg p-4">
						<p class="text-red-700">{$error}</p>
					</div>
				{:else if filteredRecipes.length === 0}
					<!-- Empty State -->
					<div class="text-center py-16">
						<div class="text-6xl mb-4">🍳</div>
						<h3 class="text-xl font-semibold text-gray-900 mb-2">
							No recipes yet
						</h3>
						<p class="text-gray-600 mb-6">
							Start by adding your first recipe from Instagram!
						</p>
						<button
							on:click={handleAddRecipe}
							class="btn btn-primary"
						>
							Add Your First Recipe
						</button>
					</div>
				{:else}
					<!-- Recipe Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
						{#each filteredRecipes as recipe (recipe.id)}
							<div class="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden h-full flex flex-col">
								<!-- Recipe thumbnail -->
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
									<div class="h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
										<span class="text-4xl opacity-60">🍽️</span>
									</div>
								{/if}
								
								<!-- Recipe Content -->
								<div class="p-4 flex-1 flex flex-col">
									<!-- Title -->
									<h3 class="text-lg font-bold text-gray-900 mb-3 line-clamp-2 min-h-[3.5rem]">
										{recipe.title}
									</h3>
									
									<!-- Tags -->
									<div class="flex items-center flex-wrap gap-2 text-sm text-gray-600 mb-3">
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
									
									<!-- Ingredients Preview -->
									<p class="text-sm text-gray-600 mb-4 flex-1">
										<span class="font-medium">Ingredients: </span>
										{recipe.ingredients.slice(0, 3).join(', ')}
										{#if recipe.ingredients.length > 3}
											<span class="text-gray-400 font-medium">
												 +{recipe.ingredients.length - 3} more
											</span>
										{/if}
									</p>
									
									<!-- Action Button -->
									<button
										on:click={() => goto(`/recipe/${recipe.id}`)}
										class="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 font-medium text-sm transition-all duration-200 transform hover:scale-[1.02]"
									>
										View Recipe →
									</button>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</main>
</div>

<style>
	/* Line clamp utility for consistent card heights */
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		text-overflow: ellipsis;
	}
</style>
