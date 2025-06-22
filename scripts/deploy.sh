#!/bin/bash

echo "Deploying ForkFlix..."

echo "Building frontend..."
cd frontend
npm run build
cd ..

echo "Deploying to Firebase..."
cd firebase
firebase deploy
cd ..

echo "Deployment complete!"