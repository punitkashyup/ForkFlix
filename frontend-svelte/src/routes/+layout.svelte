<script>
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import '../app.css';
	
	// Global state stores
	import { user, recipes, loading, authInitialized, userProfile } from '$lib/stores/auth.js';
	import { navigationLoading, navigationProgress } from '$lib/stores/navigation.js';
	import { auth } from '$lib/config/firebase.js';
	import { onAuthStateChanged } from 'firebase/auth';
	import Loading from '$lib/components/Loading.svelte';
	
	onMount(() => {
		// Set up Firebase auth listener
		const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
			if (firebaseUser) {
				// Set basic user data
				user.set({
					uid: firebaseUser.uid,
					email: firebaseUser.email,
					displayName: firebaseUser.displayName,
					photoURL: firebaseUser.photoURL
				});
				
				// Set enhanced user profile data from social login
				userProfile.set({
					uid: firebaseUser.uid,
					email: firebaseUser.email,
					displayName: firebaseUser.displayName,
					photoURL: firebaseUser.photoURL,
					phoneNumber: firebaseUser.phoneNumber,
					providerData: firebaseUser.providerData.map(provider => ({
						providerId: provider.providerId,
						uid: provider.uid,
						displayName: provider.displayName,
						email: provider.email,
						photoURL: provider.photoURL,
						phoneNumber: provider.phoneNumber
					})),
					metadata: {
						creationTime: firebaseUser.metadata.creationTime,
						lastSignInTime: firebaseUser.metadata.lastSignInTime
					},
					customClaims: null // Will be populated if needed
				});
				
				// Log social login provider information
				if (firebaseUser.providerData.length > 0) {
					console.log('User signed in with providers:', firebaseUser.providerData.map(p => p.providerId));
				}
			} else {
				user.set(null);
				userProfile.set({
					uid: null,
					email: null,
					displayName: null,
					photoURL: null,
					phoneNumber: null,
					providerData: [],
					metadata: null,
					customClaims: null
				});
			}
			
			// Mark auth as initialized after first callback
			authInitialized.set(true);
		});
		
		return unsubscribe;
	});
</script>

<style>
	.app-container {
		position: relative;
		overflow-x: hidden;
	}

	.auth-loading-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}

	.main-content {
		min-height: 100vh;
		position: relative;
	}

	/* Prevent layout shift during transitions */
	:global(body) {
		margin: 0;
		padding: 0;
		overflow-x: hidden;
	}

	/* Smooth page transitions */
	:global(.page-transition-enter) {
		opacity: 0;
		transform: translateY(10px);
	}

	:global(.page-transition-enter-active) {
		opacity: 1;
		transform: translateY(0);
		transition: opacity 0.3s ease, transform 0.3s ease;
	}

	:global(.page-transition-exit) {
		opacity: 1;
		transform: translateY(0);
	}

	:global(.page-transition-exit-active) {
		opacity: 0;
		transform: translateY(-10px);
		transition: opacity 0.2s ease, transform 0.2s ease;
	}
</style>

<!-- Global Navigation Progress Bar -->
{#if $navigationLoading}
	<div class="fixed top-0 left-0 w-full h-1 bg-gray-200 z-50" transition:fade={{ duration: 100 }}>
		<div 
			class="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-200 ease-out"
			style="width: {$navigationProgress}%"
		></div>
	</div>
{/if}

<!-- Persistent Layout Structure -->
<div class="app-container min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
	{#if !$authInitialized}
		<!-- Auth loading screen with persistent layout -->
		<div class="auth-loading-overlay" transition:fade={{ duration: 300 }}>
			<Loading message="Initializing..." showLogo={true} size="lg" />
		</div>
	{:else}
		<!-- Main app content with smooth transitions -->
		<main class="main-content" transition:fade={{ duration: 200, delay: 100 }}>
			<slot />
		</main>
	{/if}
</div>