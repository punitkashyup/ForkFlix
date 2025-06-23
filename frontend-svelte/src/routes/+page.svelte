<script>
	import { onMount } from 'svelte';
	import { user, recipes, loading, error, authInitialized } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import { PAGINATION } from '$lib/config/constants.js';
	import { signOut } from 'firebase/auth';
	import { auth } from '$lib/config/firebase.js';
	import Loading from '$lib/components/Loading.svelte';
	
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
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		{#if !$user}
			<!-- Welcome section for non-logged-in users -->
			<div class="text-center py-16">
				<h2 class="text-4xl font-bold text-gray-900 mb-4">
					Welcome to ForkFlix
				</h2>
				<p class="text-lg text-gray-600 mb-8">
					Transform Instagram recipe videos into organized, searchable recipes
				</p>
				<button
					on:click={handleLogin}
					class="btn btn-primary text-lg px-8 py-3"
				>
					Get Started
				</button>
			</div>
		{:else}
			<!-- Logged-in user content -->
			<div class="mb-8">
				<h2 class="text-3xl font-bold text-gray-900 mb-6">Your Recipes</h2>
				
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
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						{#each filteredRecipes as recipe (recipe.id)}
							<div class="card hover:shadow-lg transition-shadow cursor-pointer">
								<!-- Recipe thumbnail -->
								{#if recipe.thumbnailUrl}
									<img 
										src={recipe.thumbnailUrl} 
										alt={recipe.title}
										class="w-full h-48 object-cover rounded-lg mb-4"
									>
								{:else}
									<div class="w-full h-48 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
										<span class="text-4xl">🍽️</span>
									</div>
								{/if}
								
								<h3 class="text-lg font-semibold text-gray-900 mb-2">
									{recipe.title}
								</h3>
								
								<div class="flex items-center text-sm text-gray-600 mb-2">
									<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
										{recipe.category}
									</span>
									<span class="ml-2">⏱️ {recipe.cookingTime}min</span>
									<span class="ml-2">📈 {recipe.difficulty}</span>
								</div>
								
								<p class="text-sm text-gray-600 mb-4">
									{recipe.ingredients.slice(0, 3).join(', ')}
									{#if recipe.ingredients.length > 3}
										<span class="text-gray-400">
											+{recipe.ingredients.length - 3} more
										</span>
									{/if}
								</p>
								
								<button
									on:click={() => goto(`/recipe/${recipe.id}`)}
									class="btn btn-primary w-full"
								>
									View Recipe
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</main>
</div>