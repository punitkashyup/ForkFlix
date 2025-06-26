from typing import List, Optional, Dict, Any
from google.cloud.firestore import Query, FieldFilter
from firebase_admin import firestore
from app.core.database import get_firestore_db
from app.models.recipe import Recipe, RecipeCategory
from app.models.user import User
from app.schemas.recipe import RecipeListQuery, PaginatedRecipeResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FirebaseService:
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Get Firestore database instance"""
        if not self.db:
            self.db = get_firestore_db()
        return self.db
    
    # Recipe operations
    async def create_recipe(self, recipe_data: Dict[str, Any]) -> str:
        """Create a new recipe in Firestore"""
        try:
            db = self._get_db()
            if not db:
                logger.error("Firestore not available")
                raise Exception("Database connection failed")
            
            # Add timestamp
            recipe_data['createdAt'] = datetime.utcnow()
            recipe_data['updatedAt'] = datetime.utcnow()
            
            # Create recipe document
            doc_ref = db.collection('recipes').add(recipe_data)
            recipe_id = doc_ref[1].id
            
            # Update user recipe count
            await self._increment_user_recipe_count(recipe_data['userId'])
            
            logger.info(f"Recipe created with ID: {recipe_id}")
            return recipe_id
            
        except Exception as e:
            logger.error(f"Error creating recipe: {e}")
            raise
    
    async def get_recipe(self, recipe_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a recipe by ID"""
        try:
            db = self._get_db()
            if not db:
                logger.error("Firestore not available")
                return None
            
            doc_ref = db.collection('recipes').document(recipe_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            recipe_data = doc.to_dict()
            recipe_data['id'] = doc.id
            
            # Check access permissions
            if not recipe_data.get('isPublic', False) and recipe_data.get('userId') != user_id:
                return None
            
            return recipe_data
            
        except Exception as e:
            logger.error(f"Error getting recipe {recipe_id}: {e}")
            raise
    
    async def update_recipe(self, recipe_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a recipe"""
        try:
            logger.info(f"🔍 DEBUG: Firebase update_recipe called for {recipe_id} with data: {update_data}")
            
            db = self._get_db()
            if not db:
                logger.error("Firestore not available")
                return False
            
            doc_ref = db.collection('recipes').document(recipe_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.error(f"Recipe {recipe_id} does not exist")
                return False
            
            recipe_data = doc.to_dict()
            logger.info(f"🔍 DEBUG: Current recipe data: {recipe_data}")
            
            if recipe_data.get('userId') != user_id:
                logger.error(f"User {user_id} does not own recipe {recipe_id}")
                return False
            
            # Add update timestamp
            update_data['updatedAt'] = datetime.utcnow()
            
            logger.info(f"🔍 DEBUG: Final update_data being written to Firestore: {update_data}")
            doc_ref.update(update_data)
            
            # Verify the update
            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            logger.info(f"🔍 DEBUG: Updated recipe data after write: {updated_data}")
            
            logger.info(f"Recipe {recipe_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating recipe {recipe_id}: {e}")
            raise
    
    async def delete_recipe(self, recipe_id: str, user_id: str) -> bool:
        """Delete a recipe"""
        try:
            db = self._get_db()
            if not db:
                logger.error("Firestore not available")
                return False
            
            doc_ref = db.collection('recipes').document(recipe_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            recipe_data = doc.to_dict()
            if recipe_data.get('userId') != user_id:
                return False
            
            doc_ref.delete()
            
            # Decrement user recipe count
            await self._decrement_user_recipe_count(user_id)
            
            logger.info(f"Recipe {recipe_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting recipe {recipe_id}: {e}")
            raise
    
    async def list_recipes(
        self, 
        query_params: RecipeListQuery, 
        user_id: Optional[str] = None
    ) -> PaginatedRecipeResponse:
        """List recipes with pagination and filtering"""
        try:
            db = self._get_db()
            if not db:
                logger.error("Firestore not available")
                return PaginatedRecipeResponse(
                    items=[],
                    total=0,
                    page=query_params.page,
                    limit=query_params.limit,
                    pages=1,
                    hasNext=False,
                    hasPrev=False
                )
            
            collection_ref = db.collection('recipes')
            
            # Start with base query
            query = collection_ref
            
            # Add user filter if provided and not requesting public only
            if user_id and not query_params.public_only:
                query = query.where(filter=FieldFilter('userId', '==', user_id))
            elif query_params.public_only:
                query = query.where(filter=FieldFilter('isPublic', '==', True))
            
            # Order by creation date (newest first)
            try:
                query = query.order_by('createdAt', direction=firestore.Query.DESCENDING)
            except Exception as e:
                logger.warning(f"Order by failed, using default order: {e}")
            
            # Get total count (for pagination)
            total_docs = len(list(query.stream()))
            
            # Apply pagination
            offset = (query_params.page - 1) * query_params.limit
            query = query.offset(offset).limit(query_params.limit)
            
            # Execute query
            docs = list(query.stream())
            
            # Convert to response format
            recipes = []
            for doc in docs:
                recipe_data = doc.to_dict()
                recipe_data['id'] = doc.id
                recipes.append(recipe_data)
            
            # Calculate pagination metadata
            total_pages = max(1, (total_docs + query_params.limit - 1) // query_params.limit) if total_docs > 0 else 1
            has_next = query_params.page < total_pages and total_docs > 0
            has_prev = query_params.page > 1
            
            return PaginatedRecipeResponse(
                items=recipes,
                total=total_docs,
                page=query_params.page,
                limit=query_params.limit,
                pages=total_pages,
                hasNext=has_next,
                hasPrev=has_prev
            )
            
        except Exception as e:
            logger.error(f"Error listing recipes: {e}")
            raise
    
    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user in Firestore"""
        try:
            user_data['createdAt'] = datetime.utcnow()
            user_data['recipeCount'] = 0
            
            doc_ref = self.db.collection('users').document(user_data['uid'])
            doc_ref.set(user_data)
            
            logger.info(f"User created with UID: {user_data['uid']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            user_data = doc.to_dict()
            user_data['uid'] = doc.id
            return user_data
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update(update_data)
            
            logger.info(f"User {user_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    # Category operations
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all recipe categories"""
        try:
            docs = self.db.collection('categories').stream()
            categories = []
            
            for doc in docs:
                category_data = doc.to_dict()
                category_data['id'] = doc.id
                categories.append(category_data)
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise
    
    # Helper methods
    async def _increment_user_recipe_count(self, user_id: str):
        """Increment user's recipe count"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update({'recipeCount': firestore.Increment(1)})
        except Exception as e:
            logger.error(f"Error incrementing recipe count for user {user_id}: {e}")
    
    async def _decrement_user_recipe_count(self, user_id: str):
        """Decrement user's recipe count"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update({'recipeCount': firestore.Increment(-1)})
        except Exception as e:
            logger.error(f"Error decrementing recipe count for user {user_id}: {e}")
    
    async def search_recipes(self, search_term: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search recipes by title or ingredients"""
        try:
            # This is a simplified search - in production, use Algolia or Elasticsearch
            collection_ref = self.db.collection('recipes')
            
            # Search in title
            title_query = collection_ref.where(filter=FieldFilter('title', '>=', search_term)).where(filter=FieldFilter('title', '<=', search_term + '\uf8ff'))
            title_results = list(title_query.stream())
            
            # Search in tags (array contains)
            tag_query = collection_ref.where(filter=FieldFilter('tags', 'array_contains', search_term))
            tag_results = list(tag_query.stream())
            
            # Combine results and remove duplicates
            all_results = {}
            for doc in title_results + tag_results:
                recipe_data = doc.to_dict()
                recipe_data['id'] = doc.id
                
                # Check access permissions
                if recipe_data.get('isPublic', False) or recipe_data.get('userId') == user_id:
                    all_results[doc.id] = recipe_data
            
            return list(all_results.values())
            
        except Exception as e:
            logger.error(f"Error searching recipes: {e}")
            raise
    


# Global instance
firebase_service = FirebaseService()