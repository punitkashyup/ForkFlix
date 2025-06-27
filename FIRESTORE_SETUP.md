# Firestore Setup for ForkFlix

This document explains how to set up the required Firestore indexes for ForkFlix to work properly.

## Required Firestore Indexes

Firestore requires composite indexes for queries that combine filtering and ordering. ForkFlix needs the following indexes:

### 1. Shopping Lists Index

**Collection:** `shopping_lists`
**Fields:**
- `user_id` (Ascending)
- `created_at` (Descending)
- `__name__` (Ascending)

#### How to Create:

**Option 1: Automatic Creation (Recommended)**
1. Run the ForkFlix app and try to view shopping lists
2. Check the server logs for an error message containing a Firebase Console URL
3. Click the URL to automatically create the index
4. Wait 2-5 minutes for the index to build

**Option 2: Manual Creation**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your ForkFlix project
3. Navigate to Firestore Database → Indexes
4. Click "Create Index"
5. Set:
   - Collection ID: `shopping_lists`
   - Add fields:
     - Field: `user_id`, Order: Ascending
     - Field: `created_at`, Order: Descending
6. Click "Create"

### 2. Future Indexes (if needed)

As you add more features, you may need additional indexes:

- **Recipes by user and category:**
  - Collection: `recipes`
  - Fields: `userId` (Ascending), `category` (Ascending), `createdAt` (Descending)

- **Shopping lists with status filter:**
  - Collection: `shopping_lists`  
  - Fields: `user_id` (Ascending), `status` (Ascending), `created_at` (Descending)

## Index Status

You can check the status of your indexes in the Firebase Console:

1. Go to Firestore Database → Indexes
2. Look for indexes with status:
   - ✅ **Ready** - Index is working
   - 🔄 **Building** - Index is being created (wait a few minutes)
   - ❌ **Error** - There was a problem (check the error message)

## Troubleshooting

### "The query requires an index" Error

If you see this error:
```
400 The query requires an index. You can create it here: https://console.firebase.google.com/...
```

**Solution:**
1. Copy the URL from the error message
2. Open it in your browser
3. Click "Create Index"
4. Wait for the index to build (2-5 minutes)
5. Try the operation again

### Index Taking Too Long

Indexes usually build in 2-5 minutes, but can take longer for large datasets:
- **Small datasets** (< 1000 documents): 1-2 minutes
- **Medium datasets** (1000-10000 documents): 2-5 minutes  
- **Large datasets** (> 10000 documents): 5-30 minutes

### App Still Not Working After Index Creation

1. **Wait a bit longer** - Indexes can take time to propagate
2. **Refresh the page** - Clear any cached errors
3. **Check the index status** in Firebase Console
4. **Restart the backend server** if using local development

## Best Practices

1. **Create indexes early** - Set them up during development
2. **Monitor index usage** - Firebase Console shows query performance
3. **Clean up unused indexes** - Delete indexes you're not using
4. **Use simple queries when possible** - Avoid complex multi-field queries

## Security Rules

Make sure your Firestore security rules allow authenticated users to access their data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Shopping lists - users can only access their own
    match /shopping_lists/{listId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
      allow create: if request.auth != null && request.auth.uid == resource.data.user_id;
    }
    
    // Recipes - users can only access their own
    match /recipes/{recipeId} {
      allow read, write: if request.auth != null && resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && request.auth.uid == resource.data.userId;
    }
  }
}
```

---

**Need help?** Check the [Firebase documentation](https://firebase.google.com/docs/firestore/query-data/indexing) for more details on Firestore indexing.