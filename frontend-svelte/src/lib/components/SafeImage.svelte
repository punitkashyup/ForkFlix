<script>
	export let src = '';
	export let alt = '';
	export let fallbackText = '';
	export let className = '';
	export let size = 'md';
	
	let imageLoaded = false;
	let imageError = false;
	
	// Size classes
	const sizeClasses = {
		sm: 'w-8 h-8 text-sm',
		md: 'w-12 h-12 text-base',
		lg: 'w-16 h-16 text-lg',
		xl: 'w-20 h-20 text-xl'
	};
	
	// Get initials from fallback text
	function getInitials(text) {
		if (!text) return '?';
		return text
			.split(' ')
			.map(word => word.charAt(0))
			.join('')
			.toUpperCase()
			.slice(0, 2);
	}
	
	// Handle image load success
	function handleLoad() {
		imageLoaded = true;
		imageError = false;
	}
	
	// Handle image load error
	function handleError() {
		imageError = true;
		imageLoaded = false;
		console.log('Image failed to load:', src);
	}
	
	// Process Google profile image URL to be more reliable
	function processGoogleImageUrl(url) {
		if (!url || !url.includes('googleusercontent.com')) {
			return url;
		}
		
		try {
			// Remove size parameters and add our own smaller size to reduce load
			const baseUrl = url.split('=')[0];
			// Use smaller size and add referrer policy parameters
			return `${baseUrl}=s96-c-k-no`;
		} catch (error) {
			console.warn('Error processing Google image URL:', error);
			return url;
		}
	}
	
	// Reset state when src changes
	$: if (src) {
		imageLoaded = false;
		imageError = false;
	}
	
	$: processedSrc = processGoogleImageUrl(src);
	$: showImage = src && imageLoaded && !imageError;
	$: showFallback = !src || imageError;
</script>

<div class="relative {sizeClasses[size]} {className}">
	{#if src}
		<img
			src={processedSrc}
			{alt}
			class="w-full h-full object-cover rounded-full border-2 border-blue-200 transition-opacity duration-300 {showImage ? 'opacity-100' : 'opacity-0'}"
			on:load={handleLoad}
			on:error={handleError}
			referrerpolicy="no-referrer"
			crossorigin="anonymous"
		>
	{/if}
	
	{#if showFallback}
		<div class="absolute inset-0 w-full h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold border-2 border-blue-200">
			{getInitials(fallbackText || alt)}
		</div>
	{/if}
	
	{#if src && !imageLoaded && !imageError}
		<!-- Loading state -->
		<div class="absolute inset-0 rounded-full bg-gray-200 animate-pulse border-2 border-blue-200"></div>
	{/if}
</div>