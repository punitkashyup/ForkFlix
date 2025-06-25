<script>
	import { onMount, onDestroy } from 'svelte';
	import lottie from 'lottie-web';

	export let animationUrl = 'https://lottie.host/4f00edf8-40ff-4760-9032-2da56d2070af/GkBG1gfpsZ.lottie';
	export let width = 120;
	export let height = 120;
	export let autoplay = true;
	export let loop = true;
	export let speed = 1;
	export let className = '';

	let container;
	let animationInstance = null;
	let isLoaded = false;
	let hasError = false;

	onMount(async () => {
		if (!container) return;

		try {
			// Load the animation
			animationInstance = lottie.loadAnimation({
				container: container,
				renderer: 'svg',
				loop: loop,
				autoplay: autoplay,
				path: animationUrl,
				rendererSettings: {
					preserveAspectRatio: 'xMidYMid meet'
				}
			});

			// Set speed
			animationInstance.setSpeed(speed);

			// Handle load completion
			animationInstance.addEventListener('DOMLoaded', () => {
				isLoaded = true;
				console.log('✅ Lottie animation loaded successfully');
			});

			// Handle load errors
			animationInstance.addEventListener('data_failed', () => {
				hasError = true;
				console.error('❌ Failed to load Lottie animation');
			});

		} catch (error) {
			hasError = true;
			console.error('❌ Error initializing Lottie animation:', error);
		}
	});

	onDestroy(() => {
		if (animationInstance) {
			animationInstance.destroy();
			animationInstance = null;
		}
	});

	// Expose control methods
	export function play() {
		if (animationInstance) animationInstance.play();
	}

	export function pause() {
		if (animationInstance) animationInstance.pause();
	}

	export function stop() {
		if (animationInstance) animationInstance.stop();
	}

	export function restart() {
		if (animationInstance) {
			animationInstance.stop();
			animationInstance.play();
		}
	}
</script>

<div 
	class="lottie-container {className}"
	style="width: {width}px; height: {height}px;"
>
	{#if !isLoaded && !hasError}
		<!-- Loading fallback -->
		<div class="fallback-loading">
			<div class="spinner"></div>
		</div>
	{:else if hasError}
		<!-- Error fallback -->
		<div class="fallback-error">
			<div class="error-icon">⚠️</div>
			<div class="error-text">Animation failed to load</div>
		</div>
	{/if}
	
	<!-- Lottie animation container -->
	<div 
		bind:this={container}
		class="lottie-animation"
		style="width: 100%; height: 100%; opacity: {isLoaded ? 1 : 0};"
	></div>
</div>

<style>
	.lottie-container {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
	}

	.lottie-animation {
		transition: opacity 0.3s ease;
	}

	.fallback-loading, .fallback-error {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 8px;
	}

	.spinner {
		width: 24px;
		height: 24px;
		border: 3px solid #e5e7eb;
		border-top: 3px solid #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.error-icon {
		font-size: 24px;
	}

	.error-text {
		font-size: 12px;
		color: #6b7280;
		text-align: center;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}
</style>