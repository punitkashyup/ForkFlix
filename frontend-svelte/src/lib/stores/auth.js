import { writable } from 'svelte/store';

// User authentication store
export const user = writable(null);

// Auth initialization state (prevents FOUC)
export const authInitialized = writable(false);

// Loading states
export const loading = writable(false);

// Error states
export const error = writable(null);

// Recipes store
export const recipes = writable([]);

// Categories store
export const categories = writable([
	{ id: 'Starters', name: 'Starters', icon: '🥗', color: '#4ade80' },
	{ id: 'Main Course', name: 'Main Course', icon: '🍽️', color: '#3b82f6' },
	{ id: 'Desserts', name: 'Desserts', icon: '🍰', color: '#f59e0b' },
	{ id: 'Beverages', name: 'Beverages', icon: '🥤', color: '#06b6d4' },
	{ id: 'Snacks', name: 'Snacks', icon: '🍿', color: '#8b5cf6' }
]);