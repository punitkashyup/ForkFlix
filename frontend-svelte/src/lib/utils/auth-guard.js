import { get } from 'svelte/store';
import { goto } from '$app/navigation';
import { user, authInitialized } from '$lib/stores/auth.js';

/**
 * Auth guard utility to protect routes and redirect unauthorized users
 */
export function requireAuth() {
	const currentUser = get(user);
	const isInitialized = get(authInitialized);
	
	// If auth is still initializing, wait
	if (!isInitialized) {
		return false;
	}
	
	// If no user, redirect to landing page
	if (!currentUser) {
		goto('/landing');
		return false;
	}
	
	return true;
}

/**
 * Redirect authenticated users away from public pages
 */
export function redirectIfAuthenticated() {
	const currentUser = get(user);
	const isInitialized = get(authInitialized);
	
	// If auth is still initializing, wait
	if (!isInitialized) {
		return false;
	}
	
	// If user is authenticated, redirect to home
	if (currentUser) {
		goto('/');
		return false;
	}
	
	return true;
}

/**
 * Safe logout function that ensures proper redirect
 */
export async function safeLogout(auth, signOut) {
	try {
		await signOut(auth);
		// Force navigation to landing page
		goto('/landing', { replaceState: true });
	} catch (error) {
		console.error('Logout error:', error);
		// Even on error, try to redirect
		goto('/landing', { replaceState: true });
	}
}