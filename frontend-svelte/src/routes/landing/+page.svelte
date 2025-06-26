<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores/auth.js';
	import Lenis from 'lenis';

	let currentFeature = 0;
	let isVisible = false;

	const features = [
		{
			icon: '🔗',
			title: 'Paste & Extract',
			description: 'Just paste an Instagram Reel or YouTube Short link and watch the magic happen'
		},
		{
			icon: '🧠',
			title: 'AI-Powered Analysis',
			description: 'Our AI watches the video and extracts ingredients from audio and visuals - no internet scraping!'
		},
		{
			icon: '🍽️',
			title: 'Smart Organization',
			description: 'Auto-categorizes by meal type and cooking time so you can find recipes instantly'
		},
		{
			icon: '💾',
			title: 'Save & Replay',
			description: 'Never lose a recipe video again - all your favorites in one organized place'
		}
	];

	const steps = [
		{
			step: '1',
			title: 'Find a Recipe Video',
			description: 'Spot a delicious recipe on Instagram Reels or YouTube Shorts? Copy the link!',
			icon: '📱'
		},
		{
			step: '2',
			title: 'Paste & Process',
			description: 'Paste the link into ForkFlix and let our AI work its magic',
			icon: '✨'
		},
		{
			step: '3',
			title: 'Review & Save',
			description: 'Check the extracted ingredients and instructions, then save to your collection',
			icon: '📝'
		},
		{
			step: '4',
			title: 'Cook & Enjoy',
			description: 'Access your organized recipe collection anytime and start cooking!',
			icon: '👨‍🍳'
		}
	];

	onMount(() => {
		isVisible = true;
		
		// Initialize Lenis smooth scroll
		const lenis = new Lenis({
			duration: 1.2,
			easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
			direction: 'vertical',
			gestureDirection: 'vertical',
			smooth: true,
			mouseMultiplier: 1,
			smoothTouch: false,
			touchMultiplier: 2,
			infinite: false,
		});

		function raf(time) {
			lenis.raf(time);
			requestAnimationFrame(raf);
		}

		requestAnimationFrame(raf);
		
		// Cycle through features every 3 seconds
		const interval = setInterval(() => {
			currentFeature = (currentFeature + 1) % features.length;
		}, 3000);

		return () => {
			clearInterval(interval);
			lenis.destroy();
		};
	});

	function handleGetStarted() {
		if ($user) {
			goto('/add-recipe');
		} else {
			goto('/login');
		}
	}

	function handleTryDemo() {
		// Scroll to demo section using Lenis smooth scroll
		const target = document.getElementById('how-it-works');
		if (target) {
			target.scrollIntoView({ behavior: 'smooth' });
		}
	}
</script>

<svelte:head>
	<title>ForkFlix - Save & Organize Recipe Videos with AI Magic</title>
	<meta name="description" content="Turn Instagram Reels and YouTube Shorts into organized recipes with AI-powered ingredient extraction. Never lose a food video again!" />
	<meta name="keywords" content="recipe videos, Instagram reels, YouTube shorts, AI recipe extraction, food videos, cooking app" />
	
	<!-- Open Graph / Facebook -->
	<meta property="og:type" content="website" />
	<meta property="og:title" content="ForkFlix - Save & Organize Recipe Videos with AI Magic" />
	<meta property="og:description" content="Turn Instagram Reels and YouTube Shorts into organized recipes with AI-powered ingredient extraction." />
	<meta property="og:url" content="https://forkflix.app" />
	
	<!-- Twitter -->
	<meta property="twitter:card" content="summary_large_image" />
	<meta property="twitter:title" content="ForkFlix - Save & Organize Recipe Videos with AI Magic" />
	<meta property="twitter:description" content="Turn Instagram Reels and YouTube Shorts into organized recipes with AI-powered ingredient extraction." />
</svelte:head>

<div class="landing-page">
	<!-- Hero Section -->
	<section class="hero" class:visible={isVisible}>
		<div class="hero-content">
			<div class="hero-text">
				<h1 class="hero-title">
					Turn Recipe Videos Into 
					<span class="gradient-text">Organized Magic</span> ✨
				</h1>
				<p class="hero-subtitle">
					Stop losing those amazing food videos! ForkFlix uses AI to extract ingredients from Instagram Reels and YouTube Shorts, organizing your recipe collection automatically.
				</p>
				
				<div class="hero-stats">
					<div class="stat">
						<span class="stat-number">🔗</span>
						<span class="stat-text">Paste any video link</span>
					</div>
					<div class="stat">
						<span class="stat-number">🧠</span>
						<span class="stat-text">AI extracts ingredients</span>
					</div>
					<div class="stat">
						<span class="stat-number">📱</span>
						<span class="stat-text">Organized in seconds</span>
					</div>
				</div>

				<div class="hero-actions">
					<button class="btn-primary hero-cta" on:click={handleGetStarted}>
						🚀 Start Saving Recipes Free
					</button>
					<button class="btn-secondary" on:click={handleTryDemo}>
						👀 See How It Works
					</button>
				</div>

				<p class="hero-note">
					✅ No credit card required • ✅ Works with Instagram & YouTube • ✅ AI-powered extraction
				</p>
			</div>

			<div class="hero-visual">
				<div class="phone-mockup">
					<div class="phone-screen">
						<div class="video-preview">
							<div class="video-thumbnail">
								<div class="play-button">▶</div>
								<div class="video-title">Pasta Recipe 🍝</div>
							</div>
							<div class="extracted-ingredients">
								<h4>AI Extracted:</h4>
								<div class="ingredient-tags">
									<span class="tag">🍝 Pasta</span>
									<span class="tag">🍅 Tomatoes</span>
									<span class="tag">🧄 Garlic</span>
									<span class="tag">🧀 Cheese</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Features Section -->
	<section class="features" id="features">
		<div class="container">
			<div class="section-header">
				<h2>Why Recipe Lovers Choose ForkFlix</h2>
				<p>We solve the age-old problem: "I saved that recipe video somewhere but can't find it!"</p>
			</div>

			<div class="features-grid">
				{#each features as feature, index}
					<div class="feature-card" class:active={currentFeature === index}>
						<div class="feature-icon">{feature.icon}</div>
						<h3>{feature.title}</h3>
						<p>{feature.description}</p>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- How It Works Section -->
	<section class="how-it-works" id="how-it-works">
		<div class="container">
			<div class="section-header">
				<h2>How ForkFlix Works Its Magic</h2>
				<p>From video link to organized recipe in under 30 seconds</p>
			</div>

			<div class="steps-container">
				{#each steps as step, index}
					<div class="step-card">
						<div class="step-number">{step.step}</div>
						<div class="step-icon">{step.icon}</div>
						<h3>{step.title}</h3>
						<p>{step.description}</p>
						{#if index < steps.length - 1}
							<div class="step-arrow">→</div>
						{/if}
					</div>
				{/each}
			</div>

			<div class="demo-cta">
				<h3>Ready to try it yourself?</h3>
				<button class="btn-primary" on:click={handleGetStarted}>
					🎯 Extract Your First Recipe
				</button>
			</div>
		</div>
	</section>

	<!-- Problem/Solution Section -->
	<section class="problem-solution">
		<div class="container">
			<div class="split-layout">
				<div class="problem-side">
					<div class="emoji-big">😤</div>
					<h3>The Problem We All Face</h3>
					<ul class="problem-list">
						<li>📱 Saved 100+ recipe videos across platforms</li>
						<li>🔍 Can never find them when you want to cook</li>
						<li>⏰ Waste time scrolling through old bookmarks</li>
						<li>🤔 Forget what ingredients you need</li>
						<li>😩 End up ordering takeout instead</li>
					</ul>
				</div>
				<div class="solution-side">
					<div class="emoji-big">✨</div>
					<h3>The ForkFlix Solution</h3>
					<ul class="solution-list">
						<li>🎯 One organized place for all recipe videos</li>
						<li>🧠 AI automatically extracts ingredients</li>
						<li>🏷️ Smart categorization by meal type & time</li>
						<li>🔍 Find any recipe in seconds</li>
						<li>👨‍🍳 Actually cook those amazing recipes!</li>
					</ul>
				</div>
			</div>
		</div>
	</section>

	<!-- Testimonials Section -->
	<section class="testimonials">
		<div class="container">
			<div class="section-header">
				<h2>Recipe Lovers Are Raving</h2>
				<p>Join thousands who've organized their recipe chaos</p>
			</div>

			<div class="testimonials-grid">
				<div class="testimonial-card">
					<div class="quote">"Finally! I had 200+ saved recipe videos and could never find anything. ForkFlix organized them all in minutes!"</div>
					<div class="author">
						<div class="avatar">👩‍🍳</div>
						<div class="author-info">
							<div class="name">Sarah M.</div>
							<div class="title">Home Chef</div>
						</div>
					</div>
				</div>

				<div class="testimonial-card">
					<div class="quote">"The AI is scary good at extracting ingredients. It even caught spices I missed while watching the video!"</div>
					<div class="author">
						<div class="avatar">👨‍🍳</div>
						<div class="author-info">
							<div class="name">Mike R.</div>
							<div class="title">Food Blogger</div>
						</div>
					</div>
				</div>

				<div class="testimonial-card">
					<div class="quote">"I went from chaos to organized recipe collection overnight. Now I actually cook those Instagram recipes!"</div>
					<div class="author">
						<div class="avatar">🧑‍🍳</div>
						<div class="author-info">
							<div class="name">Alex K.</div>
							<div class="title">Busy Parent</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Final CTA Section -->
	<section class="final-cta">
		<div class="container">
			<div class="cta-content">
				<h2>Ready to Organize Your Recipe Videos?</h2>
				<p>Join thousands of home cooks who never lose a recipe video again</p>
				<button class="btn-primary btn-large" on:click={handleGetStarted}>
					🎉 Start Your Free Account
				</button>
				<p class="cta-note">
					Free forever • No credit card required • Works with Instagram & YouTube
				</p>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="footer">
		<div class="container">
			<div class="footer-content">
				<div class="footer-brand">
					<h3>🍴 ForkFlix</h3>
					<p>Turn recipe videos into organized magic</p>
				</div>
				
				<div class="footer-links">
					<div class="footer-section">
						<h4>Product</h4>
						<a href="/add-recipe">Add Recipe</a>
						<a href="/profile">My Recipes</a>
						<a href="#features">Features</a>
					</div>
					
					<div class="footer-section">
						<h4>Support</h4>
						<a href="mailto:mr.punitkr@gmail.com">Contact Us</a>
						<a href="#how-it-works">How It Works</a>
						<a href="/login">Sign In</a>
					</div>
				</div>
			</div>
			
			<div class="footer-bottom">
				<p>&copy; 2024 ForkFlix. Made with ❤️ for recipe lovers.</p>
				<p>Contact: <a href="mailto:mr.punitkr@gmail.com">mr.punitkr@gmail.com</a></p>
			</div>
		</div>
	</footer>
</div>

<style>
	/* Global Styles */
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
		line-height: 1.6;
		color: #333;
		overflow-x: hidden;
	}

	.landing-page {
		width: 100%;
		overflow-x: hidden;
	}

	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 20px;
	}

	/* Hero Section */
	.hero {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		min-height: 100vh;
		display: flex;
		align-items: center;
		position: relative;
		overflow: hidden;
		opacity: 0;
		transform: translateY(30px);
		transition: all 1s ease-out;
	}

	.hero.visible {
		opacity: 1;
		transform: translateY(0);
	}

	.hero::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.05"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
		pointer-events: none;
	}

	.hero-content {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 60px;
		align-items: center;
		width: 100%;
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 20px;
		position: relative;
		z-index: 1;
	}

	.hero-title {
		font-size: 3.5rem;
		font-weight: 800;
		line-height: 1.1;
		margin-bottom: 1.5rem;
		letter-spacing: -0.02em;
	}

	.gradient-text {
		background: linear-gradient(45deg, #ffd700, #ff6b6b);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.hero-subtitle {
		font-size: 1.25rem;
		margin-bottom: 2rem;
		opacity: 0.9;
		line-height: 1.6;
	}

	.hero-stats {
		display: flex;
		gap: 2rem;
		margin-bottom: 3rem;
	}

	.stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
	}

	.stat-number {
		font-size: 2rem;
		margin-bottom: 0.5rem;
	}

	.stat-text {
		font-size: 0.9rem;
		opacity: 0.8;
	}

	.hero-actions {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
		flex-wrap: wrap;
	}

	.btn-primary {
		background: linear-gradient(45deg, #ff6b6b, #ffd700);
		color: white;
		border: none;
		padding: 16px 32px;
		font-size: 1.1rem;
		font-weight: 600;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
	}

	.btn-primary:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
	}

	.btn-secondary {
		background: rgba(255, 255, 255, 0.1);
		color: white;
		border: 2px solid rgba(255, 255, 255, 0.3);
		padding: 14px 28px;
		font-size: 1rem;
		font-weight: 500;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.3s ease;
		backdrop-filter: blur(10px);
	}

	.btn-secondary:hover {
		background: rgba(255, 255, 255, 0.2);
		border-color: rgba(255, 255, 255, 0.5);
	}

	.hero-note {
		font-size: 0.9rem;
		opacity: 0.8;
	}

	/* Phone Mockup */
	.hero-visual {
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.phone-mockup {
		background: #1a1a1a;
		border-radius: 30px;
		padding: 20px;
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
		transform: rotate(5deg);
		animation: float 6s ease-in-out infinite;
	}

	@keyframes float {
		0%, 100% { transform: rotate(5deg) translateY(0px); }
		50% { transform: rotate(5deg) translateY(-20px); }
	}

	.phone-screen {
		background: white;
		border-radius: 20px;
		padding: 20px;
		width: 280px;
		height: 400px;
		overflow: hidden;
	}

	.video-preview {
		height: 100%;
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.video-thumbnail {
		background: linear-gradient(45deg, #667eea, #764ba2);
		border-radius: 12px;
		height: 200px;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		color: white;
		position: relative;
	}

	.play-button {
		background: rgba(255, 255, 255, 0.2);
		border-radius: 50%;
		width: 60px;
		height: 60px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.5rem;
		margin-bottom: 1rem;
		backdrop-filter: blur(10px);
	}

	.video-title {
		font-weight: 600;
		font-size: 1.1rem;
	}

	.extracted-ingredients h4 {
		color: #333;
		margin-bottom: 1rem;
		font-size: 1rem;
	}

	.ingredient-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.tag {
		background: #f0f9ff;
		color: #0369a1;
		padding: 6px 12px;
		border-radius: 20px;
		font-size: 0.85rem;
		font-weight: 500;
		border: 1px solid #bae6fd;
	}

	/* Features Section */
	.features {
		padding: 100px 0;
		background: #f8fafc;
	}

	.section-header {
		text-align: center;
		margin-bottom: 4rem;
	}

	.section-header h2 {
		font-size: 2.5rem;
		font-weight: 700;
		color: #1a202c;
		margin-bottom: 1rem;
	}

	.section-header p {
		font-size: 1.2rem;
		color: #64748b;
		max-width: 600px;
		margin: 0 auto;
	}

	.features-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 2rem;
	}

	.feature-card {
		background: white;
		padding: 2.5rem 2rem;
		border-radius: 16px;
		text-align: center;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
		transition: all 0.3s ease;
		border: 2px solid transparent;
	}

	.feature-card:hover,
	.feature-card.active {
		transform: translateY(-5px);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
		border-color: #667eea;
	}

	.feature-icon {
		font-size: 3rem;
		margin-bottom: 1.5rem;
		display: block;
	}

	.feature-card h3 {
		font-size: 1.5rem;
		font-weight: 600;
		color: #1a202c;
		margin-bottom: 1rem;
	}

	.feature-card p {
		color: #64748b;
		line-height: 1.6;
	}

	/* How It Works Section */
	.how-it-works {
		padding: 100px 0;
		background: white;
	}

	.steps-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 2rem;
		margin-bottom: 4rem;
	}

	.step-card {
		text-align: center;
		position: relative;
		padding: 2rem 1rem;
	}

	.step-number {
		background: linear-gradient(45deg, #667eea, #764ba2);
		color: white;
		width: 50px;
		height: 50px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 1.2rem;
		margin: 0 auto 1rem;
	}

	.step-icon {
		font-size: 2.5rem;
		margin-bottom: 1rem;
	}

	.step-card h3 {
		font-size: 1.3rem;
		font-weight: 600;
		color: #1a202c;
		margin-bottom: 1rem;
	}

	.step-card p {
		color: #64748b;
		line-height: 1.6;
	}

	.step-arrow {
		position: absolute;
		right: -1rem;
		top: 50%;
		transform: translateY(-50%);
		font-size: 2rem;
		color: #e2e8f0;
	}

	.demo-cta {
		text-align: center;
		background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
		padding: 3rem;
		border-radius: 20px;
		border: 1px solid #bae6fd;
	}

	.demo-cta h3 {
		font-size: 1.8rem;
		color: #1a202c;
		margin-bottom: 1.5rem;
	}

	/* Problem/Solution Section */
	.problem-solution {
		padding: 100px 0;
		background: #1a202c;
		color: white;
	}

	.split-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 4rem;
		align-items: center;
	}

	.emoji-big {
		font-size: 4rem;
		margin-bottom: 2rem;
	}

	.problem-side h3,
	.solution-side h3 {
		font-size: 2rem;
		margin-bottom: 2rem;
	}

	.problem-list,
	.solution-list {
		list-style: none;
		padding: 0;
	}

	.problem-list li,
	.solution-list li {
		padding: 0.75rem 0;
		font-size: 1.1rem;
		opacity: 0.9;
	}

	.solution-side {
		background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
		padding: 3rem;
		border-radius: 20px;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	/* Testimonials Section */
	.testimonials {
		padding: 100px 0;
		background: #f8fafc;
	}

	.testimonials-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
		gap: 2rem;
	}

	.testimonial-card {
		background: white;
		padding: 2rem;
		border-radius: 16px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
		border-left: 4px solid #667eea;
	}

	.quote {
		font-size: 1.1rem;
		line-height: 1.6;
		color: #1a202c;
		margin-bottom: 1.5rem;
		font-style: italic;
	}

	.author {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.avatar {
		font-size: 2rem;
	}

	.name {
		font-weight: 600;
		color: #1a202c;
	}

	.title {
		color: #64748b;
		font-size: 0.9rem;
	}

	/* Final CTA Section */
	.final-cta {
		padding: 100px 0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		text-align: center;
	}

	.cta-content h2 {
		font-size: 2.5rem;
		margin-bottom: 1rem;
	}

	.cta-content p {
		font-size: 1.2rem;
		margin-bottom: 2rem;
		opacity: 0.9;
	}

	.btn-large {
		font-size: 1.3rem;
		padding: 20px 40px;
	}

	.cta-note {
		margin-top: 1.5rem;
		font-size: 0.9rem;
		opacity: 0.8;
	}

	/* Footer */
	.footer {
		background: #1a202c;
		color: white;
		padding: 60px 0 20px;
	}

	.footer-content {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: 4rem;
		margin-bottom: 3rem;
	}

	.footer-brand h3 {
		font-size: 1.5rem;
		margin-bottom: 1rem;
	}

	.footer-brand p {
		opacity: 0.8;
	}

	.footer-links {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 2rem;
	}

	.footer-section h4 {
		margin-bottom: 1rem;
		color: #e2e8f0;
	}

	.footer-section a {
		display: block;
		color: #94a3b8;
		text-decoration: none;
		padding: 0.3rem 0;
		transition: color 0.3s ease;
	}

	.footer-section a:hover {
		color: white;
	}

	.footer-bottom {
		border-top: 1px solid #374151;
		padding-top: 2rem;
		text-align: center;
		opacity: 0.7;
	}

	.footer-bottom p {
		margin: 0.5rem 0;
	}

	.footer-bottom a {
		color: #667eea;
		text-decoration: none;
	}

	/* Responsive Design */
	@media (max-width: 768px) {
		.hero-content {
			grid-template-columns: 1fr;
			gap: 3rem;
			text-align: center;
		}

		.hero-title {
			font-size: 2.5rem;
		}

		.hero-stats {
			justify-content: center;
		}

		.phone-mockup {
			transform: none;
		}

		.phone-screen {
			width: 240px;
			height: 320px;
		}

		.split-layout {
			grid-template-columns: 1fr;
			gap: 3rem;
		}

		.footer-content {
			grid-template-columns: 1fr;
			gap: 2rem;
			text-align: center;
		}

		.steps-container {
			grid-template-columns: 1fr;
		}

		.step-arrow {
			display: none;
		}

		.testimonials-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 480px) {
		.hero-title {
			font-size: 2rem;
		}

		.hero-actions {
			flex-direction: column;
			align-items: center;
		}

		.btn-primary,
		.btn-secondary {
			width: 100%;
			max-width: 300px;
		}

		.container {
			padding: 0 15px;
		}

		.section-header h2 {
			font-size: 2rem;
		}
	}
</style>