<script>
	import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
	import { auth } from '$lib/config/firebase.js';
	import { user, loading, error } from '$lib/stores/auth.js';
	import { goto } from '$app/navigation';
	
	let email = '';
	let password = '';
	let isSignUp = false;
	let localError = '';
	let successMessage = '';

	async function handleSubmit() {
		if (!email || !password) {
			localError = 'Please fill in all fields';
			return;
		}

		try {
			loading.set(true);
			localError = '';
			successMessage = '';
			
			if (isSignUp) {
				await createUserWithEmailAndPassword(auth, email, password);
				successMessage = 'Account created successfully! Redirecting...';
			} else {
				await signInWithEmailAndPassword(auth, email, password);
				successMessage = 'Login successful! Redirecting...';
			}
			
			// Small delay to show success message
			setTimeout(() => {
				goto('/');
			}, 1000);
		} catch (err) {
			// Make error messages more user-friendly
			if (err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password') {
				localError = 'Invalid email or password';
			} else if (err.code === 'auth/email-already-in-use') {
				localError = 'An account with this email already exists';
			} else if (err.code === 'auth/weak-password') {
				localError = 'Password should be at least 6 characters';
			} else if (err.code === 'auth/invalid-email') {
				localError = 'Invalid email address';
			} else {
				localError = err.message || 'Authentication failed';
			}
			console.error('Auth error:', err);
		} finally {
			loading.set(false);
		}
	}

	function toggleMode() {
		isSignUp = !isSignUp;
		localError = '';
		successMessage = '';
	}
</script>

<svelte:head>
	<title>{isSignUp ? 'Sign Up' : 'Login'} - ForkFlix</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
	<!-- Background decoration -->
	<div class="absolute inset-0 opacity-30">
		<div class="absolute top-20 left-20 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
		<div class="absolute top-40 right-20 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style="animation-delay: 2s;"></div>
		<div class="absolute bottom-20 left-40 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style="animation-delay: 4s;"></div>
	</div>
	
	<div class="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
		<div class="text-center">
			<h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">🍴 ForkFlix</h1>
			<h2 class="text-3xl font-bold text-gray-900 mb-2">
				{isSignUp ? 'Create your account' : 'Welcome back!'}
			</h2>
			<p class="text-gray-600 text-lg">
				{isSignUp ? 'Start organizing your recipe videos' : 'Sign in to your recipe collection'}
			</p>
		</div>
	</div>

	<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
		<div class="bg-white/90 backdrop-blur-md py-10 px-6 shadow-2xl rounded-2xl border border-white/20">
			<form on:submit|preventDefault={handleSubmit} class="space-y-8">
				{#if localError}
					<div class="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl p-4 shadow-lg">
						<div class="flex items-center space-x-3">
							<div class="text-xl">⚠️</div>
							<p class="text-red-700 font-medium">{localError}</p>
						</div>
					</div>
				{/if}

				{#if successMessage}
					<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 shadow-lg">
						<div class="flex items-center space-x-3">
							<div class="text-xl">✓</div>
							<p class="text-green-700 font-medium">{successMessage}</p>
						</div>
					</div>
				{/if}

				<div>
					<label for="email" class="block text-sm font-semibold text-gray-700 mb-3">
						📧 Email address
					</label>
					<input
						id="email"
						type="email"
						bind:value={email}
						required
						class="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 shadow-lg transition-all duration-200"
						placeholder="your@email.com"
					>
				</div>

				<div>
					<label for="password" class="block text-sm font-semibold text-gray-700 mb-3">
						🔒 Password
					</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						required
						class="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 shadow-lg transition-all duration-200"
						placeholder="••••••••"
					>
				</div>

				<div>
					<button
						type="submit"
						disabled={$loading}
						class="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02] shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
					>
						<span class="flex items-center justify-center space-x-3">
							{#if $loading}
								<div class="inline-block animate-spin rounded-full h-5 w-5 border-2 border-white border-b-transparent"></div>
							{:else}
								<span>{isSignUp ? '✨ Create Account' : '🚀 Sign In'}</span>
							{/if}
						</span>
					</button>
				</div>
			</form>

			<div class="mt-8">
				<div class="text-center">
					<button
						type="button"
						on:click={toggleMode}
						class="font-semibold text-blue-600 hover:text-purple-600 transition-colors duration-200 text-lg"
					>
						{isSignUp 
							? '👋 Already have an account? Sign in' 
							: "🎆 Don't have an account? Sign up"
						}
					</button>
				</div>
			</div>

			<div class="mt-6">
				<div class="text-center">
					<button
						type="button"
						on:click={() => goto('/landing')}
						class="text-gray-600 hover:text-blue-600 transition-colors duration-200 font-medium"
					>
						← Back to landing page
					</button>
				</div>
			</div>
		</div>
	</div>
</div>