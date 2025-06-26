<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	
	// Get error information
	$: status = $page.status;
	$: message = $page.error?.message || 'Something went wrong';
	
	// Animation for the error illustration
	let bounceAnimation = false;
	
	// Start bounce animation after component mounts
	setTimeout(() => {
		bounceAnimation = true;
	}, 500);
	
	function goHome() {
		goto('/landing');
	}
	
	function goBack() {
		history.back();
	}
	
	// Different messages based on error status
	function getErrorMessage(status) {
		switch (status) {
			case 404:
				return {
					title: "Page Not Found",
					description: "Oops! The recipe you're looking for seems to have disappeared from our kitchen.",
					emoji: "🍳"
				};
			case 500:
				return {
					title: "Server Error",
					description: "Our kitchen is experiencing some technical difficulties. Please try again later.",
					emoji: "🔧"
				};
			case 403:
				return {
					title: "Access Denied",
					description: "You don't have permission to access this recipe.",
					emoji: "🔒"
				};
			default:
				return {
					title: "Something Went Wrong",
					description: "An unexpected error occurred while preparing your content.",
					emoji: "😕"
				};
		}
	}
	
	$: errorInfo = getErrorMessage(status);
</script>

<svelte:head>
	<title>Error {status} - ForkFlix</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4">
	<div class="max-w-2xl mx-auto text-center">
		<!-- Animated Error Illustration -->
		<div class="mb-8">
			<div 
				class="inline-flex items-center justify-center w-32 h-32 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full border-4 border-white shadow-lg {bounceAnimation ? 'animate-bounce' : ''}"
				style="animation-duration: 2s;"
			>
				<span class="text-6xl">{errorInfo.emoji}</span>
			</div>
		</div>
		
		<!-- Error Status -->
		<div class="mb-6">
			<h1 class="text-8xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
				{status}
			</h1>
			<h2 class="text-3xl font-bold text-gray-900 mb-4">
				{errorInfo.title}
			</h2>
			<p class="text-xl text-gray-600 max-w-lg mx-auto leading-relaxed">
				{errorInfo.description}
			</p>
		</div>
		
		<!-- Action Buttons -->
		<div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
			<button
				on:click={goHome}
				class="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-xl"
			>
				🏠 Go to Home
			</button>
			
			<button
				on:click={goBack}
				class="w-full sm:w-auto px-8 py-4 bg-white/80 backdrop-blur-sm text-gray-700 border-2 border-gray-200 rounded-2xl font-bold text-lg hover:bg-white hover:border-gray-300 transition-all duration-200 transform hover:scale-105 shadow-lg"
			>
				← Go Back
			</button>
		</div>
		
		<!-- Additional Help Text for 404 -->
		{#if status === 404}
			<div class="mt-12 p-6 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/30 shadow-lg">
				<h3 class="text-lg font-semibold text-gray-900 mb-3">🔍 Looking for something specific?</h3>
				<div class="text-sm text-gray-600 space-y-2">
					<p>• Check if the URL is spelled correctly</p>
					<p>• The recipe might have been moved or deleted</p>
					<p>• Try searching for recipes from our homepage</p>
				</div>
			</div>
		{/if}
		
		<!-- Decorative Elements -->
		<div class="absolute top-20 left-20 w-20 h-20 bg-blue-200 rounded-full opacity-20 animate-pulse"></div>
		<div class="absolute bottom-20 right-20 w-16 h-16 bg-purple-200 rounded-full opacity-20 animate-pulse" style="animation-delay: 1s;"></div>
		<div class="absolute top-1/3 right-10 w-12 h-12 bg-pink-200 rounded-full opacity-20 animate-pulse" style="animation-delay: 2s;"></div>
	</div>
</div>

<style>
	/* Custom bounce animation with longer duration */
	@keyframes bounce {
		0%, 20%, 53%, 80%, 100% {
			transform: translate3d(0,0,0);
		}
		40%, 43% {
			transform: translate3d(0,-15px,0);
		}
		70% {
			transform: translate3d(0,-8px,0);
		}
		90% {
			transform: translate3d(0,-3px,0);
		}
	}
</style>