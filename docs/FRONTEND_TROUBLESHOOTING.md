# Frontend Compilation Issues - Troubleshooting Guide

This guide helps resolve common React/TypeScript compilation issues in the Recipe Reel Manager frontend.

## 🚨 Quick Fixes

### 1. **Automated Fix Script**
```bash
python scripts/fix_frontend_compilation.py
```

### 2. **Manual Quick Fixes**

#### Clear Everything and Reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### TypeScript Check:
```bash
cd frontend
npx tsc --noEmit --skipLibCheck
```

## 🔍 Common Issues & Solutions

### **Issue 1: Import/Export Mismatches**

**Error:**
```
Module has no exported member 'ComponentName'. Did you mean to use 'import ComponentName from...' instead?
```

**Solutions:**

1. **Check Export Type in Component:**
   ```tsx
   // Default export
   export default function MyComponent() { ... }
   
   // Named export  
   export function MyComponent() { ... }
   ```

2. **Fix Import Statement:**
   ```tsx
   // For default exports
   import MyComponent from './MyComponent';
   
   // For named exports
   import { MyComponent } from './MyComponent';
   ```

### **Issue 2: Missing .jsx Files**

**Error:**
```
File '/path/to/Component.jsx' is not a module.
```

**Solutions:**

1. **Convert .jsx to .tsx:**
   ```bash
   # Rename files
   mv src/components/MyComponent.jsx src/components/MyComponent.tsx
   ```

2. **Add TypeScript types:**
   ```tsx
   import React from 'react';
   
   interface Props {
     title: string;
     children?: React.ReactNode;
   }
   
   export default function MyComponent({ title, children }: Props) {
     return <div>{title}{children}</div>;
   }
   ```

### **Issue 3: Props Interface Mismatches**

**Error:**
```
Property 'propertyName' does not exist on type 'ComponentProps'
```

**Solutions:**

1. **Add Missing Props:**
   ```tsx
   interface ComponentProps {
     existingProp: string;
     missingProp?: string; // Add this
   }
   ```

2. **Update Component Usage:**
   ```tsx
   // Remove invalid props or add them to interface
   <Component validProp="value" />
   ```

### **Issue 4: Firebase User Type Conflicts**

**Error:**
```
Property 'updateProfile' does not exist on type 'User'
```

**Solutions:**

1. **Use Correct Firebase User Type:**
   ```tsx
   import { User as FirebaseUser } from 'firebase/auth';
   
   // Use FirebaseUser for auth operations
   const user: FirebaseUser = getCurrentUser();
   ```

2. **Type Assertions When Needed:**
   ```tsx
   import { User as FirebaseUser } from 'firebase/auth';
   
   const firebaseUser = user as FirebaseUser;
   await firebaseUser.updateProfile({ displayName: 'New Name' });
   ```

### **Issue 5: Service Worker Type Issues**

**Error:**
```
Property 'sync' does not exist on type 'ServiceWorkerRegistration'
```

**Solutions:**

1. **Add Type Declaration:**
   ```tsx
   // Create types/sw.d.ts
   declare global {
     interface ServiceWorkerRegistration {
       sync?: {
         register(tag: string): Promise<void>;
       };
     }
   }
   ```

2. **Use Type Guards:**
   ```tsx
   if ('sync' in registration) {
     await registration.sync.register('background-sync');
   }
   ```

## 🛠 Systematic Debugging Process

### Step 1: Identify Error Type

Run TypeScript compiler to see all errors:
```bash
cd frontend
npx tsc --noEmit
```

### Step 2: Categorize Errors

- **Import/Export errors**: Fix import statements
- **Type errors**: Add or fix TypeScript interfaces
- **Missing files**: Create missing components or fix paths
- **Dependency errors**: Update package.json

### Step 3: Fix in Order

1. **Fix file structure issues first**
2. **Then fix import/export issues**
3. **Finally fix type annotations**

### Step 4: Test Incrementally

```bash
# After each fix, test compilation
npx tsc --noEmit

# Test build
npm run build

# Test development server
npm start
```

## 📁 File Structure Requirements

Ensure you have these critical files:

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── index.tsx
│   ├── App.tsx
│   ├── App.css
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx (or .jsx)
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBanner.tsx (or .jsx)
│   │   └── layout/
│   │       └── Navbar.tsx (or .jsx)
│   ├── pages/
│   │   ├── Home.tsx (or .jsx)
│   │   ├── Profile.tsx
│   │   └── RecipeDetail.tsx
│   ├── context/
│   │   └── AppContext.tsx
│   └── types/
│       └── index.ts
├── package.json
├── tsconfig.json
└── tailwind.config.js
```

## 🎯 Component Export Patterns

### Recommended Pattern:

```tsx
// ComponentName.tsx
import React from 'react';

interface ComponentNameProps {
  title: string;
  children?: React.ReactNode;
}

function ComponentName({ title, children }: ComponentNameProps) {
  return (
    <div>
      <h1>{title}</h1>
      {children}
    </div>
  );
}

export default ComponentName;
```

### Import Pattern:

```tsx
import ComponentName from './ComponentName';

// Usage
<ComponentName title="Hello">Content</ComponentName>
```

## 🔧 Package.json Dependencies

Ensure you have compatible versions:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.15.0",
    "typescript": "^4.9.5",
    "@types/react": "^18.2.22",
    "@types/react-dom": "^18.2.7"
  }
}
```

**Note:** Remove conflicting type packages:
- Remove `@types/react-router-dom` (v6 has built-in types)

## 🚀 Prevention Tips

1. **Use Consistent Export Patterns**
   - Stick to either default or named exports per component
   - Document your team's export conventions

2. **Set Up Proper TypeScript Config**
   ```json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true,
       "skipLibCheck": true
     }
   }
   ```

3. **Use IDE Extensions**
   - Auto Import - TypeScript Importer
   - ES7+ React/Redux/React-Native snippets

4. **Regular Type Checking**
   ```bash
   # Add to package.json scripts
   "type-check": "tsc --noEmit",
   "type-check:watch": "npm run type-check -- --watch"
   ```

## 🆘 Emergency Fixes

If everything is broken:

1. **Reset to Basic App:**
   ```bash
   cd frontend
   npx create-react-app temp-app --template typescript
   cp temp-app/src/App.tsx src/App.tsx
   cp temp-app/src/index.tsx src/index.tsx
   rm -rf temp-app
   ```

2. **Gradual Migration:**
   - Start with working App.tsx
   - Add components one by one
   - Test after each addition

3. **Check for Circular Dependencies:**
   ```bash
   npm install --save-dev madge
   npx madge --circular src/
   ```

## 📞 Getting Help

1. **Check Build Output:** Look for specific file names and line numbers
2. **Use TypeScript Playground:** Test type definitions at [typescriptlang.org/play](https://www.typescriptlang.org/play)
3. **Check React DevTools:** Install React Developer Tools browser extension
4. **Review Console Errors:** Browser console often has more details

Remember: Fix one error at a time, test frequently, and commit working states!