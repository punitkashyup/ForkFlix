import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';

// Navigation loading state
export const navigationLoading = writable(false);
export const currentRoute = writable('');
export const navigationProgress = writable(0);

// Enhanced goto function with loading states
export async function enhancedGoto(url, options = {}) {
	try {
		navigationLoading.set(true);
		navigationProgress.set(0);
		
		// Simulate progress for better UX
		const progressInterval = setInterval(() => {
			navigationProgress.update(p => Math.min(p + Math.random() * 30, 85));
		}, 100);
		
		await goto(url, options);
		
		clearInterval(progressInterval);
		navigationProgress.set(100);
		
		// Small delay for smooth completion
		setTimeout(() => {
			navigationLoading.set(false);
			navigationProgress.set(0);
		}, 150);
		
	} catch (error) {
		navigationLoading.set(false);
		navigationProgress.set(0);
		throw error;
	}
}

// Navigation helper for buttons
export function createNavigationHandler(url, options = {}) {
	return () => enhancedGoto(url, options);
}

// Derived store for navigation state
export const isNavigating = derived(navigationLoading, $loading => $loading);