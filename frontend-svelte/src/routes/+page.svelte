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
	<main>
		{#if !$user}
			<!-- Landing Page for Non-Authenticated Users -->
			
			<!-- Hero Section -->
			<section class="hero-gradient py-20 lg:py-32">
				<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div class="text-center">
						<h1 class="text-5xl lg:text-7xl font-bold text-white mb-6 leading-tight">
							Transform Instagram <span class="text-yellow-300">Food Reels</span><br>
							into Organized Recipes
						</h1>
						<p class="text-xl lg:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
							AI-powered recipe extraction with multi-modal analysis that reads text, watches videos, and listens to audio for 95%+ accuracy
						</p>
						<div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
							<button
								on:click={handleLogin}
								class="btn-hero text-lg px-8 py-4 bg-yellow-400 text-gray-900 font-bold rounded-full hover:bg-yellow-300 transform hover:scale-105 transition-all duration-200 shadow-lg"
							>
								🚀 Start Extracting Recipes
							</button>
							<button
								on:click={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })}
								class="btn-secondary text-lg px-8 py-4 border-2 border-white text-black font-semibold rounded-full hover:bg-white hover:text-blue-600 transition-all duration-200"
							>
								See How It Works
							</button>
						</div>
						
					</div>
				</div>
			</section>

			<!-- Features Showcase Section -->
			<section id="features" class="py-20 bg-white">
				<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div class="text-center mb-16">
						<h2 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
							Powerful AI Features
						</h2>
						<p class="text-xl text-gray-600 max-w-3xl mx-auto">
							Our advanced technology stack combines multiple AI models to extract recipes with unprecedented accuracy
						</p>
					</div>
					
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
						<!-- Feature 1: AI-Powered Extraction -->
						<div class="feature-card">
							<div class="feature-icon">🤖</div>
							<h3 class="text-xl font-bold text-gray-900 mb-3">AI-Powered Extraction</h3>
							<ul class="text-gray-600 space-y-2 text-sm">
								<li>• Extract recipes from Instagram URLs instantly</li>
								<li>• Multi-modal analysis combining text, visual, and audio</li>
								<li>• Smart ingredient detection and instruction parsing</li>
							</ul>
						</div>

						<!-- Feature 2: Mobile-First Design -->
						<div class="feature-card">
							<div class="feature-icon">📱</div>
							<h3 class="text-xl font-bold text-gray-900 mb-3">Tablet Optimized</h3>
							<ul class="text-gray-600 space-y-2 text-sm">
								<li>• Optimized for 13-inch tablets and mobile devices</li>
								<li>• Touch-friendly interface with gesture support</li>
								<li>• Responsive design that works on any screen size</li>
							</ul>
						</div>

						<!-- Feature 3: Smart Organization -->
						<div class="feature-card">
							<div class="feature-icon">🎯</div>
							<h3 class="text-xl font-bold text-gray-900 mb-3">Smart Organization</h3>
							<ul class="text-gray-600 space-y-2 text-sm">
								<li>• Automatic categorization by meal type</li>
								<li>• Confidence scoring for extracted data</li>
								<li>• Easy editing and manual override capabilities</li>
							</ul>
						</div>

						<!-- Feature 4: Lightning Fast -->
						<div class="feature-card">
							<div class="feature-icon">⚡</div>
							<h3 class="text-xl font-bold text-gray-900 mb-3">Lightning Fast</h3>
							<ul class="text-gray-600 space-y-2 text-sm">
								<li>• Instant text-based preview in under 2 seconds</li>
								<li>• Progressive enhancement with background processing</li>
								<li>• Offline viewing of saved recipes</li>
							</ul>
						</div>
					</div>
				</div>
			</section>

			<!-- How It Works Section -->
			<section id="how-it-works" class="py-20 bg-gray-50">
				<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div class="text-center mb-16">
						<h2 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
							How It Works
						</h2>
						<p class="text-xl text-gray-600 max-w-3xl mx-auto">
							From Instagram reel to organized recipe in just 4 simple steps
						</p>
					</div>
					
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
						<!-- Step 1 -->
						<div class="step-card">
							<div class="step-number">1</div>
							<div class="step-icon">🔗</div>
							<h3 class="text-lg font-bold text-gray-900 mb-2">Paste Instagram URL</h3>
							<p class="text-gray-700 text-sm">Simple input with real-time validation and content preview</p>
						</div>

						<!-- Step 2 -->
						<div class="step-card">
							<div class="step-number">2</div>
							<div class="step-icon">🧠</div>
							<h3 class="text-lg font-bold text-gray-900 mb-2">AI Analysis</h3>
							<p class="text-gray-700 text-sm">Multi-modal processing with live progress indicator across 5 phases</p>
						</div>

						<!-- Step 3 -->
						<div class="step-card">
							<div class="step-number">3</div>
							<div class="step-icon">✏️</div>
							<h3 class="text-lg font-bold text-gray-900 mb-2">Review & Edit</h3>
							<p class="text-gray-700 text-sm">Smart editing interface with confidence scores and suggestions</p>
						</div>

						<!-- Step 4 -->
						<div class="step-card">
							<div class="step-number">4</div>
							<div class="step-icon">💾</div>
							<h3 class="text-lg font-bold text-gray-900 mb-2">Save & Organize</h3>
							<p class="text-gray-700 text-sm">Categorized recipe collection with search and filtering</p>
						</div>
					</div>
					
					<!-- CTA Section -->
					<div class="text-center mt-16">
						<button
							on:click={handleLogin}
							class="btn-hero text-xl px-10 py-5 bg-blue-600 text-white font-bold rounded-full hover:bg-blue-700 transform hover:scale-105 transition-all duration-200 shadow-xl"
						>
							Try It Now - It's Free! 🍴
						</button>
					</div>
				</div>
			</section>

			<!-- Footer -->
			<footer class="bg-gray-900 text-white py-16">
				<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
						<!-- About Section -->
						<div>
							<h3 class="text-2xl font-bold mb-4">🍴 ForkFlix</h3>
							<p class="text-gray-300 mb-4">
								Transform Instagram food content into organized recipes using cutting-edge AI technology. 
								Built with love for food enthusiasts who want to preserve and organize their favorite recipes.
							</p>
							<p class="text-gray-400 text-sm">
								Built with ❤️ in India, powered by FastAPI, Svelte, and AI
							</p>
						</div>

						<!-- Quick Links -->
						<div>
							<h4 class="text-lg font-semibold mb-4">Quick Links</h4>
							<ul class="space-y-2 text-gray-300">
								<li><button on:click={handleLogin} class="hover:text-white transition-colors">Get Started</button></li>
								<li><button on:click={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })} class="hover:text-white transition-colors">Features</button></li>
								<li><button on:click={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })} class="hover:text-white transition-colors">How It Works</button></li>
								<li><a href="/profile" class="hover:text-white transition-colors">Profile</a></li>
							</ul>
						</div>

						<!-- Contact & Social -->
						<div>
							<h4 class="text-lg font-semibold mb-4">Connect</h4>
							<div class="space-y-3">
								<p class="text-gray-300 text-sm">
									Questions or feedback? We'd love to hear from you!
								</p>
								<div class="flex space-x-4">
									<a href="mailto:mr.punitkr@gmail.com" class="text-gray-300 hover:text-white transition-colors">
										📧 Email
									</a>
									<a href="https://github.com/your-repo" class="text-gray-300 hover:text-white transition-colors" target="_blank">
										🔗 GitHub
									</a>
								</div>
								<p class="text-gray-400 text-xs mt-4">
									© 2025 ForkFlix. Made with passion for great food.
								</p>
							</div>
						</div>
					</div>
				</div>
			</footer>
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
	/* Landing Page Styles */
	.hero-gradient {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		position: relative;
		overflow: hidden;
	}

	.hero-gradient::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: 
			radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
			radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
		z-index: 1;
	}

	.hero-gradient > * {
		position: relative;
		z-index: 2;
	}

	.btn-hero {
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
	}

	.btn-secondary {
		backdrop-filter: blur(10px);
	}


	/* Feature Cards */
	.feature-card {
		background: white;
		padding: 2rem;
		border-radius: 16px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
		text-align: center;
		transition: transform 0.3s ease, box-shadow 0.3s ease;
		border: 1px solid #f1f5f9;
	}

	.feature-card:hover {
		transform: translateY(-5px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
	}

	.feature-icon {
		font-size: 3rem;
		margin-bottom: 1rem;
		display: inline-block;
		animation: float 3s ease-in-out infinite;
	}

	.feature-card:nth-child(2) .feature-icon {
		animation-delay: 0.5s;
	}

	.feature-card:nth-child(3) .feature-icon {
		animation-delay: 1s;
	}

	.feature-card:nth-child(4) .feature-icon {
		animation-delay: 1.5s;
	}

	/* Step Cards */
	.step-card {
		background: white;
		padding: 2rem;
		border-radius: 16px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
		text-align: center;
		position: relative;
		transition: transform 0.3s ease;
		border: 1px solid #f1f5f9;
	}

	.step-card:hover {
		transform: translateY(-3px);
	}

	.step-number {
		position: absolute;
		top: -15px;
		left: 50%;
		transform: translateX(-50%);
		width: 30px;
		height: 30px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: bold;
		font-size: 0.9rem;
	}

	.step-icon {
		font-size: 2.5rem;
		margin: 1rem 0;
		display: inline-block;
	}

	/* Animations */
	@keyframes bounce {
		0%, 20%, 50%, 80%, 100% {
			transform: translateY(0);
		}
		40% {
			transform: translateY(-10px);
		}
		60% {
			transform: translateY(-5px);
		}
	}


	@keyframes float {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-10px);
		}
	}

	/* Tablet touch targets only */
	@media (min-width: 768px) and (max-width: 1023px) {
		.btn-hero, .btn-secondary {
			min-height: 44px;
		}
	}

	/* Mobile Optimizations */
	@media (max-width: 767px) {
		.hero-gradient {
			padding: 3rem 0;
		}

		h1 {
			font-size: 2.5rem !important;
			line-height: 1.2;
		}

		.feature-card, .step-card {
			padding: 1.5rem;
		}
	}
	
	/* Line clamp utility for consistent card heights */
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		text-overflow: ellipsis;
	}
</style>