import { 
	PUBLIC_APP_NAME,
	PUBLIC_APP_VERSION,
	PUBLIC_ENVIRONMENT,
	PUBLIC_DEBUG 
} from '$env/static/public';

export const APP_NAME = PUBLIC_APP_NAME || 'ForkFlix';
export const APP_VERSION = PUBLIC_APP_VERSION || '1.0.0';
export const ENVIRONMENT = PUBLIC_ENVIRONMENT || 'development';
export const DEBUG = PUBLIC_DEBUG === 'true';

export const RECIPE_CATEGORIES = [
	{ id: 'Starters', name: 'Starters', icon: '🥗', color: '#4ade80' },
	{ id: 'Main Course', name: 'Main Course', icon: '🍽️', color: '#3b82f6' },
	{ id: 'Desserts', name: 'Desserts', icon: '🍰', color: '#f59e0b' },
	{ id: 'Beverages', name: 'Beverages', icon: '🥤', color: '#06b6d4' },
	{ id: 'Snacks', name: 'Snacks', icon: '🍿', color: '#8b5cf6' }
];

export const DIETARY_OPTIONS = [
	'vegetarian',
	'vegan', 
	'gluten-free',
	'dairy-free',
	'nut-free',
	'keto',
	'paleo'
];

export const DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard'];

export const PAGINATION = {
	DEFAULT_LIMIT: 12,
	MAX_LIMIT: 50
};