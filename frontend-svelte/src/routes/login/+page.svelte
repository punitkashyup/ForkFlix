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

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
	<div class="sm:mx-auto sm:w-full sm:max-w-md">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">🍴 ForkFlix</h1>
			<h2 class="text-2xl font-bold text-gray-900">
				{isSignUp ? 'Create your account' : 'Sign in to your account'}
			</h2>
		</div>
	</div>

	<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
		<div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				{#if localError}
					<div class="bg-red-50 border border-red-200 rounded-lg p-4">
						<p class="text-red-700 text-sm">{localError}</p>
					</div>
				{/if}

				{#if successMessage}
					<div class="bg-green-50 border border-green-200 rounded-lg p-4">
						<p class="text-green-700 text-sm">{successMessage}</p>
					</div>
				{/if}

				<div>
					<label for="email" class="block text-sm font-medium text-gray-700">
						Email address
					</label>
					<div class="mt-1">
						<input
							id="email"
							type="email"
							bind:value={email}
							required
							class="input"
							placeholder="your@email.com"
						>
					</div>
				</div>

				<div>
					<label for="password" class="block text-sm font-medium text-gray-700">
						Password
					</label>
					<div class="mt-1">
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							class="input"
							placeholder="••••••••"
						>
					</div>
				</div>

				<div>
					<button
						type="submit"
						disabled={$loading}
						class="btn btn-primary w-full {$loading ? 'opacity-50 cursor-not-allowed' : ''}"
					>
						{#if $loading}
							<div class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
						{/if}
						{isSignUp ? 'Create Account' : 'Sign In'}
					</button>
				</div>
			</form>

			<div class="mt-6">
				<div class="text-center">
					<button
						type="button"
						on:click={toggleMode}
						class="font-medium text-blue-600 hover:text-blue-500"
					>
						{isSignUp 
							? 'Already have an account? Sign in' 
							: "Don't have an account? Sign up"
						}
					</button>
				</div>
			</div>

			<div class="mt-6">
				<div class="text-center">
					<button
						type="button"
						on:click={() => goto('/')}
						class="text-sm text-gray-600 hover:text-gray-500"
					>
						← Back to home
					</button>
				</div>
			</div>
		</div>
	</div>
</div>