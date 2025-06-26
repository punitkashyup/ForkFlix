<script>
	import { onMount } from 'svelte';
	import { user, recipes, loading, error, authInitialized } from '$lib/stores/auth.js';
	import { apiService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import { PAGINATION } from '$lib/config/constants.js';
	import { signOut } from 'firebase/auth';
	import { auth } from '$lib/config/firebase.js';
	import Loading from '$lib/components/Loading.svelte';
	import { goto as gotoPage } from '$app/navigation';
	
	// Redirect to landing page for non-authenticated users
	$: if (!$user && $authInitialized) {
		gotoPage('/landing');
	}
	
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

<div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50" on:click={handleClickOutside} on:keydown={handleClickOutside} role="main">
	<!-- Header -->
	<header class="bg-white/90 backdrop-blur-md shadow-lg border-b border-white/20 sticky top-0 z-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">🍴 ForkFlix</h1>
				</div>
				
				<div class="flex items-center space-x-4">
					{#if $user}
						<button
							on:click={handleAddRecipe}
							class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
						>
							✨ Add Recipe
						</button>
						<div class="relative user-menu">
							<button 
								on:click={() => showUserMenu = !showUserMenu}
								class="flex items-center space-x-2 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 rounded-xl px-3 py-2 transition-all duration-200"
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
		{#if $user}
			<!-- Logged-in user content -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
				<div class="text-center mb-12">
					<h2 class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-4">Your Recipe Collection</h2>
					<p class="text-xl text-gray-600 max-w-2xl mx-auto">Discover, organize, and cook your favorite recipes</p>
				</div>
				
				<!-- Search and Filter -->
				<div class="flex flex-col sm:flex-row gap-6 mb-8">
					<div class="relative flex-1">
						<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
							</svg>
						</div>
						<input
							type="text"
							placeholder="Search your recipes..."
							bind:value={searchTerm}
							class="w-full pl-12 pr-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 shadow-lg transition-all duration-200"
						>
					</div>
					<select 
						bind:value={selectedCategory} 
						class="sm:w-64 px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 shadow-lg transition-all duration-200"
					>
						<option value="">🍽️ All Categories</option>
						<option value="Starters">🥗 Starters</option>
						<option value="Main Course">🍖 Main Course</option>
						<option value="Desserts">🍰 Desserts</option>
						<option value="Beverages">🥤 Beverages</option>
						<option value="Snacks">🍿 Snacks</option>
					</select>
				</div>

				<!-- Loading State -->
				{#if $loading}
					<div class="text-center py-16">
						<div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4 animate-spin">
							<div class="w-8 h-8 bg-white rounded-full"></div>
						</div>
						<p class="text-xl text-gray-600 font-medium">Loading your delicious recipes...</p>
					</div>
				{:else if $error}
					<div class="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-2xl p-6 shadow-lg">
						<div class="flex items-center space-x-3">
							<div class="text-2xl">⚠️</div>
							<p class="text-red-700 font-medium">{$error}</p>
						</div>
					</div>
				{:else if filteredRecipes.length === 0}
					<!-- Empty State -->
					<div class="text-center py-20">
						<div class="bg-gradient-to-br from-blue-100 to-purple-100 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-8">
							<div class="text-6xl">🍳</div>
						</div>
						<h3 class="text-3xl font-bold text-gray-900 mb-4">
							No recipes yet
						</h3>
						<p class="text-xl text-gray-600 mb-8 max-w-md mx-auto">
							Start building your collection by adding your first recipe from Instagram or YouTube!
						</p>
						<button
							on:click={handleAddRecipe}
							class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-xl"
						>
							✨ Add Your First Recipe
						</button>
					</div>
				{:else}
					<!-- Recipe Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
						{#each filteredRecipes as recipe (recipe.id)}
							<div class="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer overflow-hidden h-full flex flex-col border border-white/20 hover:border-blue-200 transform hover:scale-[1.02]">
								<!-- Recipe thumbnail -->
								{#if recipe.thumbnailUrl}
									<div class="h-40 bg-gradient-to-br from-gray-100 to-gray-200 overflow-hidden relative">
										<img 
											src={recipe.thumbnailUrl} 
											alt={recipe.title}
											class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
											loading="lazy"
										>
										<div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
									</div>
								{:else}
									<div class="h-40 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center relative overflow-hidden">
										<span class="text-4xl opacity-80 group-hover:scale-110 transition-transform duration-300">🍽️</span>
										<div class="absolute inset-0 bg-gradient-to-t from-white/20 to-transparent"></div>
									</div>
								{/if}
								
								<!-- Recipe Content -->
								<div class="p-4 flex-1 flex flex-col">
									<!-- Title -->
									<h3 class="text-lg font-bold text-gray-900 mb-3 line-clamp-2 min-h-[3rem] group-hover:text-blue-600 transition-colors duration-200">
										{recipe.title}
									</h3>
									
									<!-- Tags -->
									<div class="flex items-center flex-wrap gap-1.5 text-sm text-gray-600 mb-3">
										<span class="bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold border border-blue-200">
											{recipe.category}
										</span>
										<span class="bg-gradient-to-r from-green-100 to-emerald-200 text-green-800 px-2 py-1 rounded-full text-xs font-semibold border border-green-200">
											⏱️ {recipe.cookingTime}min
										</span>
										<span class="bg-gradient-to-r from-purple-100 to-purple-200 text-purple-800 px-2 py-1 rounded-full text-xs font-semibold border border-purple-200">
											📈 {recipe.difficulty}
										</span>
									</div>
									
									<!-- Ingredients Preview -->
									<div class="mb-4 flex-1">
										<p class="text-xs text-gray-600 font-medium mb-1">🥘 Ingredients:</p>
										<p class="text-sm text-gray-700 leading-relaxed">
											{recipe.ingredients.slice(0, 2).join(', ')}
											{#if recipe.ingredients.length > 2}
												<span class="text-blue-600 font-semibold">
													 +{recipe.ingredients.length - 2} more
												</span>
											{/if}
										</p>
									</div>
									
									<!-- Action Button -->
									<button
										on:click={() => goto(`/recipe/${recipe.id}`)}
										class="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 font-semibold text-sm transition-all duration-200 transform group-hover:scale-[1.02] shadow-lg hover:shadow-xl"
									>
										<span class="flex items-center justify-center space-x-2">
											<span>View Recipe</span>
											<span class="transform group-hover:translate-x-1 transition-transform duration-200">→</span>
										</span>
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
