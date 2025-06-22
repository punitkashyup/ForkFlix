# 🔥 Firebase Setup Guide for Recipe Reel Manager

This guide will help you set up all Firebase services required for the Recipe Reel Manager project.

## 📋 Prerequisites

- Node.js 16+ installed
- Firebase account
- Firebase project created (you have: `forkflix-9e6b2`)

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the configuration helper script:

```bash
node scripts/get-firebase-config.js
```

This will guide you through getting all the necessary Firebase configuration values.

### Option 2: Manual Setup

Follow the detailed steps below.

## 🔧 Detailed Setup Steps

### Step 1: Firebase Console Configuration

1. **Go to Firebase Console**: https://console.firebase.google.com
2. **Select your project**: `forkflix-9e6b2`

### Step 2: Enable Required Services

#### A. Authentication
1. Go to **Authentication** → **Sign-in method**
2. Enable **Email/Password**
3. Enable **Google** (optional)
4. Configure authorized domains if needed

#### B. Firestore Database
1. Go to **Firestore Database**
2. Click **Create database**
3. Choose **Start in production mode**
4. Select your preferred region (choose closest to users)

#### C. Storage
1. Go to **Storage**
2. Click **Get started**
3. Choose **Start in production mode**
4. Use same region as Firestore

### Step 3: Get Web App Configuration

1. Go to **Project Settings** (gear icon) → **General**
2. Scroll down to **Your apps** section
3. If no web app exists:
   - Click **Add app** → Web (</>) icon
   - Enter app nickname: "Recipe Reel Manager Web"
   - Enable Firebase Hosting (optional)
   - Click **Register app**

4. Copy the configuration values:
   ```javascript
   const firebaseConfig = {
     apiKey: "your-api-key",
     authDomain: "forkflix-9e6b2.firebaseapp.com",
     projectId: "forkflix-9e6b2",
     storageBucket: "forkflix-9e6b2.appspot.com",
     messagingSenderId: "your-sender-id",
     appId: "your-app-id"
   };
   ```

### Step 4: Update Environment Files

#### Frontend Environment (`frontend/.env`):
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_FIREBASE_API_KEY=your_api_key_here
REACT_APP_FIREBASE_AUTH_DOMAIN=forkflix-9e6b2.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=forkflix-9e6b2
REACT_APP_FIREBASE_STORAGE_BUCKET=forkflix-9e6b2.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
REACT_APP_FIREBASE_APP_ID=your_app_id_here
```

#### Backend Environment (`backend/.env`):
```bash
FIREBASE_PROJECT_ID=forkflix-9e6b2
FIREBASE_CREDENTIALS_PATH=../firebase/firebase-admin-key.json
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
SECRET_KEY=your_secret_key_min_32_chars
CORS_ORIGINS=http://localhost:3000
```

### Step 5: Get Additional API Keys

#### Hugging Face API Key (for AI features):
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read permissions
3. Copy the token to your backend `.env` file

#### Generate Secret Key:
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 6: Deploy Firebase Configuration

1. **Install Firebase CLI** (if not installed):
   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**:
   ```bash
   firebase login
   ```

3. **Deploy Firestore rules and indexes**:
   ```bash
   cd firebase
   firebase deploy --only firestore:rules,firestore:indexes
   ```

### Step 7: Initialize Database Collections

The app will automatically create the necessary collections when you first use it, but you can also run the setup script:

```bash
# Run the automated Firebase setup
./scripts/firebase-setup.sh
```

## 📚 Firebase Services Used

### 1. **Authentication**
- **Email/Password**: Primary authentication method
- **Google Sign-In**: Optional social login
- **JWT Tokens**: Handled by Firebase Admin SDK

### 2. **Firestore Database**
Collections structure:
```
/recipes/{recipeId}
  - id: string
  - userId: string
  - title: string
  - instagramUrl: string
  - category: string
  - ingredients: array
  - ...

/users/{userId}
  - uid: string
  - email: string
  - displayName: string
  - preferences: object
  - recipeCount: number
  - ...

/categories/{categoryId}
  - id: string
  - name: string
  - icon: string
  - color: string
  - description: string
```

### 3. **Storage**
- **Recipe Thumbnails**: Auto-generated from Instagram videos
- **User Profile Pictures**: Optional profile images
- **Cached Images**: For offline functionality

### 4. **Security Rules**
- Users can only access their own data
- Public recipes are readable by all authenticated users
- Write operations require authentication and ownership

## 🔒 Security Configuration

### Firestore Rules
The rules are automatically deployed and include:
- User data isolation
- Recipe ownership verification
- Public recipe sharing
- Category read-only access

### Storage Rules
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## 🧪 Testing Your Setup

1. **Start the backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Test authentication**:
   - Visit http://localhost:3000
   - Try signing up with a new account
   - Try logging in

4. **Test recipe creation**:
   - Add a recipe with an Instagram URL
   - Check if data appears in Firestore console

## 🚨 Troubleshooting

### Common Issues

1. **"Permission denied" errors**:
   - Check Firestore rules
   - Verify user authentication
   - Ensure proper project ID in config

2. **"Firebase config not found"**:
   - Verify all environment variables are set
   - Check `.env` file locations
   - Restart development servers

3. **"Admin SDK errors"**:
   - Verify service account key path
   - Check key permissions
   - Ensure project ID matches

4. **CORS errors**:
   - Add your domain to authorized domains in Firebase Console
   - Update CORS_ORIGINS in backend `.env`

### Debug Commands

```bash
# Check Firebase project status
firebase projects:list

# Test Firestore rules
firebase firestore:rules:debug

# Validate firebase.json
firebase use forkflix-9e6b2
```

## 📞 Support

If you encounter issues:
1. Check the [Firebase Documentation](https://firebase.google.com/docs)
2. Review error messages in browser console
3. Check server logs for backend errors
4. Verify all environment variables are correctly set

## 🎉 Next Steps

Once Firebase is set up:
1. Configure your Hugging Face API key for AI features
2. Test the Instagram URL processing
3. Deploy to production (Vercel for frontend, Railway/Render for backend)
4. Set up monitoring and analytics