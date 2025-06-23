# ForkFlix SvelteKit Frontend

A modern, fast, and simple frontend for the ForkFlix recipe management application built with SvelteKit.

## Features

- 🔥 **Firebase Authentication** - Email/password login and signup
- 🤖 **AI Recipe Extraction** - Extract recipes from Instagram URLs using AI
- 📱 **Responsive Design** - Works on all devices
- ⚡ **Fast Performance** - SvelteKit's optimized runtime
- 🎨 **Tailwind CSS** - Modern, utility-first styling
- 📦 **Simple State Management** - Svelte stores without complexity

## Setup

1. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

2. **Update .env with your Firebase config:**
   - Get Firebase configuration from [Firebase Console](https://console.firebase.google.com)
   - Update the PUBLIC_FIREBASE_* variables

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

## Environment Variables

All public environment variables in SvelteKit must start with `PUBLIC_`:

- `PUBLIC_FIREBASE_API_KEY` - Firebase API key
- `PUBLIC_FIREBASE_AUTH_DOMAIN` - Firebase auth domain
- `PUBLIC_FIREBASE_PROJECT_ID` - Firebase project ID
- `PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## Project Structure

```
src/
├── routes/
│   ├── +layout.svelte           # Main layout with auth
│   ├── +page.svelte             # Home page
│   ├── login/+page.svelte       # Login/signup
│   └── add-recipe/+page.svelte  # Add recipe with AI
├── lib/
│   ├── stores/auth.js           # Svelte stores for state
│   ├── config/
│   │   ├── firebase.js          # Firebase configuration
│   │   └── constants.js         # App constants
│   └── services/api.js          # API service
└── app.css                      # Global styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Differences from React Version

- ✅ **No hooks complexity** - No useEffect, useCallback, dependency arrays
- ✅ **Simpler state management** - Reactive variables and stores
- ✅ **Better performance** - Faster loading and runtime
- ✅ **Less boilerplate** - More concise code
- ✅ **Easier debugging** - Simpler component lifecycle