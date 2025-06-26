<script>
	export let message = 'Loading...';
	export let size = 'md'; // sm, md, lg
	export let showLogo = false;
	
	const sizeClasses = {
		sm: 'h-6 w-6',
		md: 'h-10 w-10', 
		lg: 'h-16 w-16'
	};
</script>

<div class="flex items-center justify-center">
	<div class="text-center">
		<!-- Modern Gradient Spinner -->
		<div class="mb-4 flex justify-center">
			<div class="relative {sizeClasses[size]}">
				<div class="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full animate-spin"></div>
				<div class="absolute inset-2 bg-white rounded-full"></div>
			</div>
		</div>
		
		{#if showLogo}
			<h2 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">🍴 ForkFlix</h2>
		{/if}
		
		<p class="text-gray-600 font-medium">{message}</p>
	</div>
</div>

