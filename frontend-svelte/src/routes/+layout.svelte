<script>
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import '../app.css';
	
	// Global state stores
	import { user, recipes, loading, authInitialized, userProfile } from '$lib/stores/auth.js';
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

{#if !$authInitialized}
	<!-- Auth loading screen -->
	<div class="min-h-screen bg-gray-50 flex items-center justify-center" transition:fade={{ duration: 300 }}>
		<Loading message="Initializing..." showLogo={true} size="lg" />
	</div>
{:else}
	<main class="min-h-screen bg-gray-50" transition:fade={{ duration: 300 }}>
		<slot />
	</main>
{/if}