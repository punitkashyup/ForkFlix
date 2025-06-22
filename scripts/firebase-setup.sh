#!/bin/bash

echo "🔥 Firebase Setup Script for Recipe Reel Manager"
echo "================================================"

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "📦 Installing Firebase CLI..."
    npm install -g firebase-tools
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Firebase CLI globally. Try with sudo or install locally:"
        echo "   npx firebase-tools"
        exit 1
    fi
fi

echo "✅ Firebase CLI is available"

# Login to Firebase (if not already logged in)
echo "🔐 Logging into Firebase..."
firebase login --no-localhost

# Initialize Firebase in the project (if not already done)
echo "🚀 Setting up Firebase project..."
cd firebase

# Check if firebase.json exists, if not initialize
if [ ! -f "firebase.json" ]; then
    echo "📝 Initializing Firebase project..."
    firebase init
else
    echo "✅ Firebase project already initialized"
fi

# Deploy Firestore rules
echo "📋 Deploying Firestore security rules..."
firebase deploy --only firestore:rules

# Deploy Firestore indexes
echo "📊 Deploying Firestore indexes..."
firebase deploy --only firestore:indexes

# Create initial collections and seed data
echo "🌱 Setting up initial Firestore collections..."
node -e "
const admin = require('firebase-admin');
const serviceAccount = require('./firebase-admin-key.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://forkflix-9e6b2-default-rtdb.firebaseio.com'
});

const db = admin.firestore();

// Create categories collection
const categories = [
  { id: 'starters', name: 'Starters', icon: '🥗', color: '#4ade80', description: 'Appetizers and light bites' },
  { id: 'main-course', name: 'Main Course', icon: '🍽️', color: '#3b82f6', description: 'Main dishes and entrees' },
  { id: 'desserts', name: 'Desserts', icon: '🍰', color: '#f59e0b', description: 'Sweet treats and desserts' },
  { id: 'beverages', name: 'Beverages', icon: '🥤', color: '#06b6d4', description: 'Drinks and beverages' },
  { id: 'snacks', name: 'Snacks', icon: '🍿', color: '#8b5cf6', description: 'Quick snacks and finger foods' }
];

async function setupCategories() {
  for (const category of categories) {
    await db.collection('categories').doc(category.id).set({
      ...category,
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    });
  }
  console.log('✅ Categories created successfully');
  process.exit(0);
}

setupCategories().catch(console.error);
"

echo ""
echo "🎉 Firebase setup completed!"
echo ""
echo "Next steps:"
echo "1. Get your Firebase config from the console and update frontend/.env"
echo "2. Make sure your Hugging Face API key is set in backend/.env"
echo "3. Start your development servers:"
echo "   - Backend: cd backend && uvicorn app.main:app --reload"
echo "   - Frontend: cd frontend && npm start"