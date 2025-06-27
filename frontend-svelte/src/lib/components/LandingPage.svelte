<script>
	import { goto } from '$app/navigation';

	function handleLogin() {
		goto('/login');
	}
</script>

<!-- Landing Page for Non-Authenticated Users -->
			
<!-- Hero Section -->
<section class="hero-gradient py-20 lg:py-32">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
            <h1 class="text-5xl lg:text-7xl font-bold text-white mb-6 leading-tight">
                Your Favorite Food Videos, <br>
                <span class="text-yellow-300">Now Cookable</span>
            </h1>
            <p class="text-xl lg:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
                Stop scrolling, start cooking. ForkFlix turns video recipes into simple, step-by-step instructions.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button
                    on:click={handleLogin}
                    class="btn-hero text-lg px-8 py-4 bg-yellow-400 text-gray-900 font-bold rounded-full hover:bg-yellow-300 transform hover:scale-105 transition-all duration-200 shadow-lg"
                >
                    Get Started - It's Free
                </button>
                <button
                    on:click={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })}
                    class="btn-secondary text-lg px-8 py-4 border-2 border-white text-white font-semibold rounded-full hover:bg-white hover:text-blue-600 transition-all duration-200"
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
                Never Lose a Recipe Again
            </h2>
            <p class="text-xl text-gray-600 max-w-3xl mx-auto">
                ForkFlix is packed with features to make your cooking life easier.
            </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <!-- Feature 1: AI-Powered Extraction -->
            <div class="feature-card">
                <div class="feature-icon">✨</div>
                <h3 class="text-xl font-bold text-gray-900 mb-3">AI Recipe Extraction</h3>
                <p class="text-gray-600 text-sm">
                    Our AI scans videos to pull out ingredients and steps for you.
                </p>
            </div>

            <!-- Feature 2: Smart Shopping Lists -->
            <div class="feature-card">
                <div class="feature-icon">🛒</div>
                <h3 class="text-xl font-bold text-gray-900 mb-3">Smart Shopping Lists</h3>
                <p class="text-gray-600 text-sm">
                    Generate optimized shopping lists from multiple recipes with AI-powered cost and time optimization.
                </p>
            </div>

            <!-- Feature 3: Multi-Modal Analysis -->
            <div class="feature-card">
                <div class="feature-icon">🎥</div>
                <h3 class="text-xl font-bold text-gray-900 mb-3">Multi-Modal Analysis</h3>
                <p class="text-gray-600 text-sm">
                    Extract recipes from video, audio, and text with advanced AI processing for maximum accuracy.
                </p>
            </div>

            <!-- Feature 4: Pantry Management -->
            <div class="feature-card">
                <div class="feature-icon">🏠</div>
                <h3 class="text-xl font-bold text-gray-900 mb-3">Pantry Inventory</h3>
                <p class="text-gray-600 text-sm">
                    Track what you have at home and get shopping lists that account for your existing ingredients.
                </p>
            </div>
        </div>
    </div>
</section>

<!-- How It Works Section -->
<section id="how-it-works" class="py-20 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
            <h2 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
                Get Started in 3 Easy Steps
            </h2>
            <p class="text-xl text-gray-600 max-w-3xl mx-auto">
                Cooking from videos has never been this simple.
            </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Step 1 -->
            <div class="step-card">
                <div class="step-number">1</div>
                <div class="step-icon">🔗</div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Paste the Video Link</h3>
                <p class="text-gray-700 text-sm">Copy the link from Instagram, TikTok, or YouTube.</p>
            </div>

            <!-- Step 2 -->
            <div class="step-card">
                <div class="step-number">2</div>
                <div class="step-icon">✨</div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Let AI Do the Work</h3>
                <p class="text-gray-700 text-sm">Our AI extracts the recipe ingredients and instructions.</p>
            </div>

            <!-- Step 3 -->
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-icon">🍳</div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Start Cooking</h3>
                <p class="text-gray-700 text-sm">Get a simple, easy-to-follow recipe card.</p>
            </div>
        </div>
        
        <!-- CTA Section -->
        <div class="text-center mt-16">
            <button
                on:click={handleLogin}
                class="btn-hero text-xl px-10 py-5 bg-blue-600 text-white font-bold rounded-full hover:bg-blue-700 transform hover:scale-105 transition-all duration-200 shadow-xl"
            >
                Save Your First Recipe
            </button>
        </div>
    </div>
</section>

<!-- Smart Shopping Lists Feature Spotlight -->
<section class="py-20 bg-gradient-to-br from-green-50 to-blue-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <!-- Content -->
            <div>
                <h2 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
                    🛒 Smart Shopping Lists
                </h2>
                <p class="text-xl text-gray-700 mb-8">
                    Never forget an ingredient again. Generate intelligent shopping lists from your saved recipes with AI-powered optimization.
                </p>
                
                <div class="space-y-6">
                    <div class="flex items-start space-x-4">
                        <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <span class="text-white font-bold text-sm">✓</span>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-900 mb-1">Multi-Recipe Consolidation</h4>
                            <p class="text-gray-600 text-sm">Combine ingredients from multiple recipes with smart quantity calculation and deduplication.</p>
                        </div>
                    </div>
                    
                    <div class="flex items-start space-x-4">
                        <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <span class="text-white font-bold text-sm">✓</span>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-900 mb-1">Store Optimization</h4>
                            <p class="text-gray-600 text-sm">Organize items by grocery store sections with optimized shopping routes to save time.</p>
                        </div>
                    </div>
                    
                    <div class="flex items-start space-x-4">
                        <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <span class="text-white font-bold text-sm">✓</span>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-900 mb-1">Cost & Budget Optimization</h4>
                            <p class="text-gray-600 text-sm">Get bulk buying recommendations, seasonal alternatives, and budget tracking.</p>
                        </div>
                    </div>
                    
                    <div class="flex items-start space-x-4">
                        <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <span class="text-white font-bold text-sm">✓</span>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-900 mb-1">Pantry Integration</h4>
                            <p class="text-gray-600 text-sm">Automatically exclude items you already have at home from your shopping list.</p>
                        </div>
                    </div>
                </div>
                
                <div class="mt-8">
                    <button
                        on:click={handleLogin}
                        class="inline-flex items-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors duration-200"
                    >
                        Start Creating Smart Lists
                        <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </button>
                </div>
            </div>
            
            <!-- Visual/Mockup -->
            <div class="lg:text-center">
                <div class="bg-white rounded-2xl shadow-2xl p-6 max-w-md mx-auto">
                    <div class="border-b pb-4 mb-4">
                        <h3 class="font-bold text-gray-900 flex items-center">
                            🛒 Weekend Meal Prep
                            <span class="ml-auto text-sm text-green-600 font-normal">$67.45</span>
                        </h3>
                        <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                            <div class="bg-green-600 h-2 rounded-full" style="width: 75%"></div>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">15 of 20 items • 75% complete</p>
                    </div>
                    
                    <div class="space-y-3">
                        <div class="flex items-center space-x-3">
                            <span class="text-xl">🥬</span>
                            <div class="flex-1">
                                <p class="font-medium text-sm">Produce</p>
                                <div class="space-y-1">
                                    <div class="flex items-center text-xs">
                                        <input type="checkbox" checked class="mr-2" disabled>
                                        <span class="line-through text-gray-500">2 lbs Chicken Breast</span>
                                        <span class="ml-auto text-green-600">$12.99</span>
                                    </div>
                                    <div class="flex items-center text-xs">
                                        <input type="checkbox" class="mr-2" disabled>
                                        <span>1 bag Mixed Greens</span>
                                        <span class="ml-auto">$4.50</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="flex items-center space-x-3">
                            <span class="text-xl">🥫</span>
                            <div class="flex-1">
                                <p class="font-medium text-sm">Pantry</p>
                                <div class="flex items-center text-xs">
                                    <input type="checkbox" class="mr-2" disabled>
                                    <span>2 cans Diced Tomatoes</span>
                                    <span class="ml-auto">$3.98</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-yellow-50 border border-yellow-200 rounded p-2">
                            <p class="text-xs text-yellow-800">
                                💡 <strong>AI Tip:</strong> Buy chicken in bulk to save $4.50
                            </p>
                        </div>
                    </div>
                </div>
            </div>
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
                    The smart way to save and organize your favorite video recipes.
                </p>
                <p class="text-gray-400 text-sm">
                    © 2025 ForkFlix. All Rights Reserved.
                </p>
            </div>

            <!-- Quick Links -->
            <div>
                <h4 class="text-lg font-semibold mb-4">Menu</h4>
                <ul class="space-y-2 text-gray-300">
                    <li><button on:click={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })} class="hover:text-white transition-colors">Features</button></li>
                    <li><button on:click={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })} class="hover:text-white transition-colors">How It Works</button></li>
                    <li><button on:click={handleLogin} class="hover:text-white transition-colors">Login</button></li>
                </ul>
            </div>

            <!-- Contact & Social -->
            <div>
                <h4 class="text-lg font-semibold mb-4">Contact</h4>
                <div class="space-y-3">
                    <a href="mailto:mr.punitkr@gmail.com" class="text-gray-300 hover:text-white transition-colors">
                        mr.punitkr@gmail.com
                    </a>
                    <div class="flex space-x-4">
                        <a href="https://github.com/punit-kr/ForkFlix" class="text-gray-300 hover:text-white transition-colors" target="_blank">
                            GitHub
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</footer>

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
</style>
