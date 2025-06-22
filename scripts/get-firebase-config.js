#!/usr/bin/env node

/**
 * Firebase Configuration Helper
 * 
 * This script helps you get the Firebase configuration values needed for your app.
 * Run this after setting up your Firebase project in the console.
 */

const readline = require('readline');
const fs = require('fs');
const path = require('path');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🔥 Firebase Configuration Helper');
console.log('================================\n');

console.log('Please get these values from Firebase Console:');
console.log('1. Go to https://console.firebase.google.com');
console.log('2. Select your project: forkflix-9e6b2');
console.log('3. Go to Project Settings > General');
console.log('4. Scroll down to "Your apps" section');
console.log('5. Click on the web app (</>) or create one if needed\n');

const questions = [
  {
    key: 'REACT_APP_FIREBASE_API_KEY',
    prompt: 'Enter your Firebase API Key: ',
    description: 'Found in Firebase Console > Project Settings > General > Web API Key'
  },
  {
    key: 'REACT_APP_FIREBASE_MESSAGING_SENDER_ID',
    prompt: 'Enter your Messaging Sender ID: ',
    description: 'Found in Firebase Console > Project Settings > Cloud Messaging'
  },
  {
    key: 'REACT_APP_FIREBASE_APP_ID',
    prompt: 'Enter your App ID: ',
    description: 'Found in Firebase Console > Project Settings > General > App ID'
  },
  {
    key: 'HUGGINGFACE_API_KEY',
    prompt: 'Enter your Hugging Face API Key (optional, press Enter to skip): ',
    description: 'Get from https://huggingface.co/settings/tokens',
    optional: true
  },
  {
    key: 'SECRET_KEY',
    prompt: 'Enter a secret key for JWT tokens (or press Enter for random): ',
    description: 'Used for signing JWT tokens (minimum 32 characters)',
    optional: true,
    default: () => require('crypto').randomBytes(32).toString('hex')
  }
];

async function askQuestion(question) {
  return new Promise((resolve) => {
    console.log(`\n📝 ${question.description}`);
    rl.question(question.prompt, (answer) => {
      if (!answer && question.optional) {
        if (question.default) {
          answer = question.default();
          console.log(`Generated: ${answer}`);
        } else {
          console.log('Skipped');
        }
      }
      resolve({ key: question.key, value: answer });
    });
  });
}

async function main() {
  const config = {};
  
  // Set known values
  config.FIREBASE_PROJECT_ID = 'forkflix-9e6b2';
  config.REACT_APP_FIREBASE_AUTH_DOMAIN = 'forkflix-9e6b2.firebaseapp.com';
  config.REACT_APP_FIREBASE_PROJECT_ID = 'forkflix-9e6b2';
  config.REACT_APP_FIREBASE_STORAGE_BUCKET = 'forkflix-9e6b2.appspot.com';
  
  // Ask for user input
  for (const question of questions) {
    const result = await askQuestion(question);
    if (result.value) {
      config[result.key] = result.value;
    }
  }
  
  // Update frontend .env
  const frontendEnvPath = path.join(__dirname, '..', 'frontend', '.env');
  let frontendEnv = `REACT_APP_API_URL=http://localhost:8000

# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=${config.REACT_APP_FIREBASE_API_KEY || 'your_firebase_api_key_here'}
REACT_APP_FIREBASE_AUTH_DOMAIN=${config.REACT_APP_FIREBASE_AUTH_DOMAIN}
REACT_APP_FIREBASE_PROJECT_ID=${config.REACT_APP_FIREBASE_PROJECT_ID}
REACT_APP_FIREBASE_STORAGE_BUCKET=${config.REACT_APP_FIREBASE_STORAGE_BUCKET}
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=${config.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || 'your_sender_id_here'}
REACT_APP_FIREBASE_APP_ID=${config.REACT_APP_FIREBASE_APP_ID || 'your_app_id_here'}
`;

  // Update backend .env
  const backendEnvPath = path.join(__dirname, '..', 'backend', '.env');
  let backendEnv = `FIREBASE_PROJECT_ID=${config.FIREBASE_PROJECT_ID}
FIREBASE_CREDENTIALS_PATH=../firebase/firebase-admin-key.json

# Hugging Face API Key
HUGGINGFACE_API_KEY=${config.HUGGINGFACE_API_KEY || 'your_huggingface_api_key_here'}

# Security
SECRET_KEY=${config.SECRET_KEY || 'your_very_secure_secret_key_here_min_32_chars'}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
AI_RATE_LIMIT_PER_MINUTE=10
`;

  try {
    fs.writeFileSync(frontendEnvPath, frontendEnv);
    fs.writeFileSync(backendEnvPath, backendEnv);
    
    console.log('\n✅ Configuration files updated successfully!');
    console.log(`📄 Frontend config: ${frontendEnvPath}`);
    console.log(`📄 Backend config: ${backendEnvPath}`);
    
    console.log('\n🚀 Next steps:');
    console.log('1. Start your backend: cd backend && uvicorn app.main:app --reload');
    console.log('2. Start your frontend: cd frontend && npm start');
    console.log('3. Visit http://localhost:3000 to see your app!');
    
  } catch (error) {
    console.error('❌ Error writing configuration files:', error.message);
  }
  
  rl.close();
}

main().catch(console.error);