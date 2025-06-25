<script>
	import LottieLoader from './LottieLoader.svelte';
	
	export let message = 'Loading...';
	export let size = 'md'; // sm, md, lg
	export let showLogo = false;
	export let useLottie = true; // Use Lottie animation by default
	
	const sizeDimensions = {
		sm: { width: 32, height: 32 },
		md: { width: 64, height: 64 }, 
		lg: { width: 96, height: 96 }
	};
	
	const sizeClasses = {
		sm: 'h-4 w-4',
		md: 'h-8 w-8', 
		lg: 'h-12 w-12'
	};
</script>

<div class="flex items-center justify-center">
	<div class="text-center">
		{#if useLottie}
			<!-- Lottie Animation -->
			<div class="mb-4 flex justify-center">
				<LottieLoader 
					width={sizeDimensions[size].width}
					height={sizeDimensions[size].height}
					className="lottie-loading"
				/>
			</div>
		{:else}
			<!-- Fallback Spinner -->
			<div class="inline-block animate-spin rounded-full border-b-2 border-blue-600 mb-4 {sizeClasses[size]}"></div>
		{/if}
		
		{#if showLogo}
			<h2 class="text-2xl font-bold text-gray-900 mb-2">🍴 ForkFlix</h2>
		{/if}
		
		<p class="text-gray-600">{message}</p>
	</div>
</div>

<style>
	:global(.lottie-loading) {
		filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
	}
</style>