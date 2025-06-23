<script>
	export let message = 'Loading...';
	export let size = 'md'; // sm, md, lg
	export let showLogo = false;
	
	const sizeClasses = {
		sm: 'h-4 w-4',
		md: 'h-8 w-8', 
		lg: 'h-12 w-12'
	};
</script>

<div class="flex items-center justify-center">
	<div class="text-center">
		<div class="inline-block animate-spin rounded-full border-b-2 border-blue-600 mb-4 {sizeClasses[size]}"></div>
		
		{#if showLogo}
			<h2 class="text-2xl font-bold text-gray-900 mb-2">🍴 ForkFlix</h2>
		{/if}
		
		<p class="text-gray-600">{message}</p>
	</div>
</div>