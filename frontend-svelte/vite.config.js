import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 3000,
		host: true
	},
	define: {
		global: 'globalThis'
	},
	optimizeDeps: {
		include: ['firebase/app', 'firebase/auth']
	}
});