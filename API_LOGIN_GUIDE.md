# Recipe Reel Manager API - Login & Authentication Guide

## Overview

The Recipe Reel Manager API uses Firebase Authentication for user management. The API is designed to work with Firebase ID tokens for production, but includes development mode features for testing.

## Accessing Swagger UI

1. **Start the Backend Server**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open Swagger Documentation**
   - Navigate to: `http://localhost:8000/docs`
   - Alternative ReDoc format: `http://localhost:8000/redoc`

## Authentication Methods

### Method 1: Development Mode (Recommended for Testing)

In development mode, the API automatically provides mock authentication, making it easy to test all endpoints.

**How it works:**
- The API automatically uses a mock user when no authentication is provided
- All protected endpoints will work without requiring real Firebase tokens
- Mock user details:
  - UID: `dev_user_123`
  - Email: `dev@example.com`
  - Name: `Development User`

**To use in Swagger:**
1. Go to any protected endpoint (marked with 🔒)
2. Click "Try it out"
3. Execute the request directly - no additional setup needed!

### Method 2: Bearer Token Authentication

For testing with actual authentication headers:

1. **Click the "Authorize" button** in Swagger UI (top right)
2. **Enter any bearer token** (in development mode, any value works):
   ```
   Bearer your-test-token-here
   ```
3. **Click "Authorize"**
4. **Try protected endpoints** - they will now use the mock authenticated user

### Method 3: Production Firebase Authentication

For production use with real Firebase tokens:

1. **Get a Firebase ID Token** from your frontend application:
   ```javascript
   import { getAuth } from 'firebase/auth';
   
   const auth = getAuth();
   const user = auth.currentUser;
   if (user) {
     const idToken = await user.getIdToken();
     console.log('Firebase ID Token:', idToken);
   }
   ```

2. **Use the token in Swagger:**
   - Click "Authorize" in Swagger UI
   - Enter: `Bearer YOUR_FIREBASE_ID_TOKEN`
   - Click "Authorize"

## API Endpoints Overview

### Authentication Endpoints (`/api/v1/auth/`)

- **POST /auth/login** - Login endpoint (documentation only - actual auth handled by Firebase)
- **POST /auth/logout** - Logout user (requires authentication)
- **GET /auth/profile** - Get user profile (requires authentication)
- **PUT /auth/profile** - Update user profile (requires authentication)
- **GET /auth/stats** - Get user statistics (requires authentication)

### Recipe Endpoints (`/api/v1/recipes/`)

- **GET /recipes/** - Get all recipes (requires authentication)
- **POST /recipes/** - Create a new recipe (requires authentication)
- **GET /recipes/{recipe_id}** - Get specific recipe (requires authentication)
- **PUT /recipes/{recipe_id}** - Update recipe (requires authentication)
- **DELETE /recipes/{recipe_id}** - Delete recipe (requires authentication)

### Instagram Endpoints (`/api/v1/instagram/`)

- **POST /instagram/validate** - Validate Instagram URL
- **POST /instagram/embed** - Get Instagram embed code
- **GET /instagram/metadata/{url}** - Get Instagram post metadata

### AI Endpoints (`/api/v1/ai/`)

- **POST /ai/extract-ingredients** - Extract recipe from Instagram post
- **POST /ai/categorize** - Categorize recipe content

## Testing Workflow

### 1. Test Public Endpoints (No Auth Required)
```bash
# Health check
curl http://localhost:8000/health

# Validate Instagram URL
curl -X POST "http://localhost:8000/api/v1/instagram/validate" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/p/EXAMPLE123/"}'
```

### 2. Test Protected Endpoints (With Mock Auth)

In development mode, simply call protected endpoints directly:

```bash
# Get user profile (auto-authenticates with mock user)
curl http://localhost:8000/api/v1/auth/profile

# Get recipes
curl http://localhost:8000/api/v1/recipes/
```

### 3. Test with Bearer Token

```bash
# Using any bearer token in development
curl -H "Authorization: Bearer test-token" \
  http://localhost:8000/api/v1/auth/profile
```

## Frontend Integration

The frontend uses the API with Firebase authentication:

1. **User logs in** via Firebase Auth in the frontend
2. **Frontend gets Firebase ID token** from the authenticated user
3. **Frontend sends requests** with the token in the Authorization header:
   ```javascript
   const response = await fetch('/api/v1/recipes/', {
     headers: {
       'Authorization': `Bearer ${firebaseIdToken}`,
       'Content-Type': 'application/json'
     }
   });
   ```

## Environment Configuration

### Development Environment
- Mock authentication enabled
- All endpoints accessible without real tokens
- Debug logging enabled

### Production Environment  
- Real Firebase token verification required
- Secure authentication enforced
- Error details limited for security

## Troubleshooting

### Common Issues

1. **"Authentication required" error**
   - Ensure you're in development mode, or
   - Provide a valid Bearer token in the Authorization header

2. **CORS errors**
   - The API includes CORS middleware allowing all origins in development
   - For production, configure specific allowed origins

3. **Firebase initialization errors**
   - Check that Firebase credentials are properly configured
   - Verify the Firebase project settings

### Checking Authentication Status

Test the authentication system:

```bash
# Check if you're authenticated
curl http://localhost:8000/api/v1/auth/profile

# Expected response in development:
{
  "uid": "dev_user_123",
  "email": "dev@example.com",
  "displayName": "Development User",
  "photoURL": null,
  "recipeCount": 0,
  "preferences": {
    "defaultCategory": "Main Course",
    "aiAutoExtract": true,
    "publicRecipes": false
  }
}
```

## Security Notes

- In production, all authentication goes through Firebase
- Development mode should never be used in production
- API keys and secrets should be properly configured via environment variables
- All endpoints validate user permissions before executing operations

---

**Need Help?**
- Check the Swagger documentation at `http://localhost:8000/docs`
- Review the API source code for detailed implementation
- Test with curl commands or use the interactive Swagger interface