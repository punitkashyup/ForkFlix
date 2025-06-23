<script>
	import { onMount } from 'svelte';
	import '../app.css';
	
	// Global state stores
	import { user, recipes, loading } from '$lib/stores/auth.js';
	import { auth } from '$lib/config/firebase.js';
	import { onAuthStateChanged } from 'firebase/auth';
	
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
		});
		
		return unsubscribe;
	});
</script>

<main class="min-h-screen bg-gray-50">
	<slot />
</main>