# Frontend Debug Guide

## Common Frontend Issues and Solutions

### 1. **TypeScript Errors**

If you see TypeScript compilation errors:

```bash
# Check for missing types
cd frontend
npm install @types/react @types/react-dom @types/node
```

### 2. **Missing Dependencies**

Make sure all dependencies are installed:

```bash
cd frontend
npm install
```

### 3. **Firebase Configuration Errors**

Check your `.env` file has all required Firebase variables:

```bash
# Required in frontend/.env
REACT_APP_FIREBASE_API_KEY=your_key_here
REACT_APP_FIREBASE_AUTH_DOMAIN=forkflix-9e6b2.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=forkflix-9e6b2
REACT_APP_FIREBASE_STORAGE_BUCKET=forkflix-9e6b2.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id
```

### 4. **Component Import Errors**

If you see "Module not found" errors for components:

```bash
# Check if the component file exists
ls frontend/src/components/common/
ls frontend/src/pages/
```

### 5. **API Connection Issues**

Make sure the backend is running on port 8000:

```bash
# In backend directory
uvicorn app.main:app --reload --port 8000
```

### 6. **Quick Frontend Test**

Create a minimal test file to check React setup:

```jsx
// frontend/src/TestApp.jsx
import React from 'react';

function TestApp() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Frontend Test</h1>
      <p>If you see this, React is working!</p>
    </div>
  );
}

export default TestApp;
```

Temporarily replace App.tsx import in index.tsx:

```jsx
// frontend/src/index.tsx
import TestApp from './TestApp';

root.render(<TestApp />);
```

### 7. **Tailwind CSS Issues**

If styles aren't loading:

```bash
# Check if Tailwind is properly configured
cat frontend/tailwind.config.js
cat frontend/postcss.config.js
```

### 8. **Development Server Issues**

Try starting with different options:

```bash
# Standard start
npm start

# With specific port
PORT=3001 npm start

# With debug info
DEBUG=true npm start
```

## Step-by-Step Debug Process

1. **Start Simple**: Use TestApp.jsx to verify React works
2. **Add Components Gradually**: Import one component at a time
3. **Check Console**: Look for specific error messages
4. **Verify Environment**: Ensure .env variables are loaded
5. **Check Network**: Verify API calls in browser dev tools

## Common Error Messages and Solutions

| Error | Solution |
|-------|----------|
| "Module not found" | Check file path and ensure file exists |
| "Cannot read property of undefined" | Check for missing props or state |
| "Firebase configuration" | Verify all Firebase env variables |
| "CORS error" | Ensure backend allows frontend origin |
| "TypeScript error" | Add proper type definitions |

## Emergency Fallback

If all else fails, start with a minimal setup:

```jsx
// Minimal App.tsx
import React from 'react';

function App() {
  return <div>Hello World</div>;
}

export default App;
```

Then gradually add features back until you find the issue.