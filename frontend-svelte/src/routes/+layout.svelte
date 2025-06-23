<script>
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import '../app.css';
	
	// Global state stores
	import { user, recipes, loading, authInitialized } from '$lib/stores/auth.js';
	import { auth } from '$lib/config/firebase.js';
	import { onAuthStateChanged } from 'firebase/auth';
	import Loading from '$lib/components/Loading.svelte';
	
	onMount(() => {
		// Set up Firebase auth listener
		const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
			if (firebaseUser) {
				user.set({
					uid: firebaseUser.uid,
					email: firebaseUser.email,
					displayName: firebaseUser.displayName,
					photoURL: firebaseUser.photoURL
				});
			} else {
				user.set(null);
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