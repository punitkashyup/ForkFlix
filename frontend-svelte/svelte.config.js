import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			// Options for adapter-static
			pages: 'build',
			assets: 'build',
			fallback: 'index.html',
			precompress: false,
			strict: true
		}),
		// Paths configuration
		paths: {
			base: '',
			assets: ''
		},
		// Environment variables
		env: {
			publicPrefix: 'PUBLIC_'
		},
		// Prerender configuration
		prerender: {
			handleHttpError: 'warn',
			handleMissingId: 'warn'
		}
	}
};

export default config;