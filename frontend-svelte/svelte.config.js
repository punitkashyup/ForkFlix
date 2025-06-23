import adapter from '@sveltejs/adapter-auto';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter(),
		// Paths configuration
		paths: {
			base: '',
			assets: ''
		},
		// Environment variables
		env: {
			publicPrefix: 'PUBLIC_'
		}
	}
};

export default config;