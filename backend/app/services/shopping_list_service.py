import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from firebase_admin import firestore
from app.models.shopping_list import ShoppingList, IngredientItem, Unit, ItemCategory, ShoppingOptimization
from app.schemas.shopping_list import (
    ShoppingListCreate, GenerateShoppingListRequest, ShoppingListOptimizationRequest
)
from app.services.ingredient_processor import ingredient_processor
from app.core.database import firebase_service

logger = logging.getLogger(__name__)


class ShoppingListService:
    """Service for managing shopping lists with AI-powered optimization."""
    
    def __init__(self):
        self.db = None
        self.unit_conversions = self._setup_unit_conversions()
        self.store_layout = self._setup_store_layout()
    
    def _get_db(self):
        """Get database connection, initialize if needed."""
        if self.db is None:
            self.db = firebase_service.get_db()
        return self.db
    
    def _setup_unit_conversions(self) -> Dict[str, Dict[str, float]]:
        """Setup unit conversion factors."""
        return {
            'volume': {
                Unit.CUP: 1.0,
                Unit.CUPS: 1.0,
                Unit.TABLESPOON: 1/16,
                Unit.TABLESPOONS: 1/16,
                Unit.TEASPOON: 1/48,
                Unit.TEASPOONS: 1/48,
                Unit.FLUID_OUNCE: 1/8,
                Unit.FLUID_OUNCES: 1/8,
                Unit.LITER: 4.227,
                Unit.LITERS: 4.227,
                Unit.MILLILITER: 0.004227,
                Unit.MILLILITERS: 0.004227,
            },
            'weight': {
                Unit.POUND: 1.0,
                Unit.POUNDS: 1.0,
                Unit.OUNCE: 1/16,
                Unit.OUNCES: 1/16,
                Unit.GRAM: 0.00220462,
                Unit.GRAMS: 0.00220462,
                Unit.KILOGRAM: 2.20462,
                Unit.KILOGRAMS: 2.20462,
            }
        }
    
    def _setup_store_layout(self) -> Dict[ItemCategory, int]:
        """Setup typical grocery store layout order."""
        return {
            ItemCategory.PRODUCE: 1,
            ItemCategory.BAKERY: 2,
            ItemCategory.MEAT_SEAFOOD: 3,
            ItemCategory.DAIRY_EGGS: 4,
            ItemCategory.FROZEN: 5,
            ItemCategory.PANTRY: 6,
            ItemCategory.BEVERAGES: 7,
            ItemCategory.SNACKS: 8,
            ItemCategory.HOUSEHOLD: 9,
            ItemCategory.OTHER: 10,
        }
    
    
    async def generate_shopping_list(self, user_id: str, request: GenerateShoppingListRequest) -> ShoppingList:
        """Generate a smart shopping list from multiple recipes."""
        try:
            # Check if shopping lists already exist for any of these recipes
            existing_lists = await self._check_existing_shopping_lists(user_id, request.recipe_ids)
            if existing_lists:
                recipe_names = [r['recipe_title'] for r in existing_lists]
                raise ValueError(f"Shopping lists already exist for: {', '.join(recipe_names)}. Please use the existing lists or delete them first.")
            
            # Get recipes
            recipes = await self._get_recipes(user_id, request.recipe_ids)
            if not recipes:
                raise ValueError("No valid recipes found")
            
            # Extract and process all ingredients
            all_ingredients = []
            for recipe in recipes:
                for ingredient_text in recipe.get('ingredients', []):
                    processed = ingredient_processor.process_ingredient(ingredient_text, recipe['id'])
                    all_ingredients.append(processed)
            
            # Consolidate duplicate ingredients
            if request.consolidate_duplicates:
                all_ingredients = await self._consolidate_ingredients(all_ingredients)
            
            # Convert to shopping list items
            shopping_items = []
            for ingredient in all_ingredients:
                # Ensure we have valid quantity (default to 1 if missing or invalid)
                quantity = ingredient.quantity if ingredient.quantity and ingredient.quantity > 0 else 1.0
                
                item = IngredientItem(
                    name=ingredient.name,
                    quantity=quantity,
                    unit=ingredient.unit or Unit.ITEM,
                    category=ingredient.category or ItemCategory.OTHER,
                    recipe_ids=[rid for rid in request.recipe_ids if rid],
                    alternatives=ingredient.alternatives or []
                )
                shopping_items.append(item)
            
            # Optimize categories and ordering
            shopping_items = self._optimize_item_order(shopping_items)
            
            # Create shopping list
            list_name = request.list_name or f"Shopping List - {datetime.now().strftime('%m/%d/%Y')}"
            
            shopping_list = ShoppingList(
                user_id=user_id,
                name=list_name,
                items=shopping_items,
                recipe_ids=request.recipe_ids,
                total_items=len(shopping_items),
                checked_items=0,
                optimization=None,
                notes=None
            )
            
            # Save to database
            shopping_list_id = await self._save_shopping_list(shopping_list)
            shopping_list.id = shopping_list_id
            
            return shopping_list
            
        except Exception as e:
            logger.error(f"Error generating shopping list: {e}")
            raise
    
    async def optimize_shopping_list(self, user_id: str, request: ShoppingListOptimizationRequest) -> Dict[str, Any]:
        """Optimize an existing shopping list for efficiency and cost."""
        try:
            # Get shopping list
            shopping_list = await self._get_shopping_list(user_id, request.shopping_list_id)
            if not shopping_list:
                raise ValueError("Shopping list not found")
            
            # Generate optimization recommendations
            optimization = await self._generate_optimization(shopping_list, request)
            
            # Apply optimizations to create new optimized list
            optimized_items = await self._apply_optimizations(shopping_list.items, optimization)
            
            # Update shopping list with optimizations
            shopping_list.items = optimized_items
            shopping_list.estimated_total = sum(item.estimated_price or 0 for item in optimized_items)
            shopping_list.updated_at = datetime.utcnow()
            
            # Save updated list
            await self._update_shopping_list(shopping_list)
            
            # Generate savings summary
            savings_summary = self._calculate_savings_summary(shopping_list, optimization)
            
            # Generate shopping route
            shopping_route = self._generate_shopping_route(shopping_list.items, request.store_preference)
            
            return {
                'optimized_list': shopping_list,
                'optimization_data': optimization,
                'savings_summary': savings_summary,
                'shopping_route': shopping_route
            }
            
        except Exception as e:
            logger.error(f"Error optimizing shopping list: {e}")
            raise
    
    async def _get_recipes(self, user_id: str, recipe_ids: List[str]) -> List[Dict]:
        """Get recipes from database."""
        recipes = []
        try:
            db = self._get_db()
            if not db:
                logger.error("❌ Database connection not available")
                raise RuntimeError("Database service is not available")
            
            for recipe_id in recipe_ids:
                doc = db.collection('recipes').document(recipe_id).get()
                if doc.exists:
                    recipe_data = doc.to_dict()
                    if recipe_data.get('userId') == user_id:
                        recipe_data['id'] = doc.id
                        recipes.append(recipe_data)
                        logger.info(f"✅ Found recipe: {recipe_data.get('title', recipe_id)}")
                    else:
                        logger.warning(f"⚠️ Recipe {recipe_id} belongs to different user")
                else:
                    logger.warning(f"⚠️ Recipe {recipe_id} not found")
            
            if not recipes:
                logger.error(f"❌ No valid recipes found for user {user_id} with IDs: {recipe_ids}")
                raise ValueError("No valid recipes found for the provided recipe IDs")
                
        except Exception as e:
            logger.error(f"❌ Error fetching recipes: {e}")
            raise
        
        return recipes
    
    async def _check_existing_shopping_lists(self, user_id: str, recipe_ids: List[str]) -> List[Dict]:
        """Check if shopping lists already exist for any of the given recipes."""
        existing_lists = []
        try:
            db = self._get_db()
            if not db:
                logger.warning("Database not available - skipping duplicate check")
                return []
            
            # Query shopping lists that contain any of the recipe IDs
            query = db.collection('shopping_lists').where('user_id', '==', user_id)
            docs = query.get()
            
            for doc in docs:
                data = doc.to_dict()
                list_recipe_ids = data.get('recipe_ids', [])
                
                # Check if any of the requested recipe IDs already exist in this list
                overlapping_recipes = set(recipe_ids) & set(list_recipe_ids)
                if overlapping_recipes:
                    # Get recipe titles for better error message
                    for recipe_id in overlapping_recipes:
                        recipes = await self._get_recipes(user_id, [recipe_id])
                        if recipes:
                            existing_lists.append({
                                'list_id': doc.id,
                                'list_name': data.get('name', 'Unnamed List'),
                                'recipe_id': recipe_id,
                                'recipe_title': recipes[0].get('title', 'Unknown Recipe')
                            })
            
        except Exception as e:
            logger.error(f"Error checking existing shopping lists: {e}")
            # Don't fail the whole operation if we can't check duplicates
            return []
        
        return existing_lists
    
    async def _consolidate_ingredients(self, ingredients: List) -> List:
        """Consolidate duplicate ingredients with smart merging."""
        consolidated = {}
        
        for ingredient in ingredients:
            key = ingredient.name.lower().strip()
            
            if key in consolidated:
                # Merge quantities if units are compatible
                existing = consolidated[key]
                if self._units_compatible(existing.unit, ingredient.unit):
                    # Convert to common unit and add quantities
                    existing_qty = self._convert_to_base_unit(existing.quantity or 0, existing.unit)
                    new_qty = self._convert_to_base_unit(ingredient.quantity or 0, ingredient.unit)
                    total_qty = existing_qty + new_qty
                    
                    # Use the more precise unit
                    better_unit = self._choose_better_unit(existing.unit, ingredient.unit, total_qty)
                    final_qty = self._convert_from_base_unit(total_qty, better_unit)
                    
                    existing.quantity = final_qty
                    existing.unit = better_unit
                    
                    # Merge recipe IDs
                    if hasattr(ingredient, 'recipe_ids'):
                        for rid in ingredient.recipe_ids:
                            if rid not in existing.recipe_ids:
                                existing.recipe_ids.append(rid)
                else:
                    # Keep both if units are incompatible
                    consolidated[f"{key}_alt"] = ingredient
            else:
                consolidated[key] = ingredient
        
        return list(consolidated.values())
    
    
    
    def _optimize_item_order(self, items: List[IngredientItem]) -> List[IngredientItem]:
        """Optimize the order of items based on typical store layout."""
        return sorted(items, key=lambda item: self.store_layout.get(item.category, 99))
    
    async def _generate_optimization(self, shopping_list: ShoppingList, request: ShoppingListOptimizationRequest) -> ShoppingOptimization:
        """Generate optimization recommendations."""
        recommendations = {}
        
        # Budget optimization
        if request.budget_priority and shopping_list.budget_limit:
            recommendations['budget'] = await self._optimize_for_budget(shopping_list)
        
        # Time optimization
        if request.time_priority:
            recommendations['time'] = await self._optimize_for_time(shopping_list)
        
        # Bulk buying recommendations
        if request.include_bulk_recommendations:
            recommendations['bulk'] = await self._generate_bulk_recommendations(shopping_list)
        
        return ShoppingOptimization(
            user_id=shopping_list.user_id,
            recommendations=recommendations,
            store_route=self._generate_store_route(shopping_list.items),
            estimated_time=self._estimate_shopping_time(shopping_list.items),
            cost_savings=self._calculate_potential_savings(shopping_list),
            bulk_opportunities=recommendations.get('bulk', []),
            seasonal_suggestions=await self._get_seasonal_suggestions(shopping_list.items)
        )
    
    async def _optimize_for_budget(self, shopping_list: ShoppingList) -> Dict[str, Any]:
        """Generate budget optimization recommendations."""
        return {
            'total_budget': shopping_list.budget_limit,
            'estimated_total': shopping_list.estimated_total,
            'over_budget': shopping_list.estimated_total > (shopping_list.budget_limit or float('inf')),
            'cost_reduction_suggestions': [],  # Implement specific suggestions
            'generic_alternatives': []  # Implement generic brand alternatives
        }
    
    async def _optimize_for_time(self, shopping_list: ShoppingList) -> Dict[str, Any]:
        """Generate time optimization recommendations."""
        return {
            'estimated_time_minutes': self._estimate_shopping_time(shopping_list.items),
            'time_saving_tips': [
                "Group items by store section",
                "Shop during off-peak hours",
                "Use store's mobile app for faster checkout"
            ],
            'optimal_shopping_hours': ['8-10 AM', '2-4 PM', '7-9 PM']
        }
    
    async def _generate_bulk_recommendations(self, shopping_list: ShoppingList) -> List[Dict[str, Any]]:
        """Generate bulk buying recommendations."""
        bulk_recommendations = []
        
        for item in shopping_list.items:
            if item.category in [ItemCategory.PANTRY, ItemCategory.HOUSEHOLD]:
                # Suggest bulk buying for non-perishables
                bulk_recommendations.append({
                    'item': item.name,
                    'current_quantity': item.quantity,
                    'bulk_quantity': item.quantity * 3,  # Suggest 3x quantity
                    'current_price': item.estimated_price,
                    'bulk_price': item.estimated_price * 2.5,  # 15% savings
                    'savings': item.estimated_price * 0.5,
                    'recommendation': f"Buy in bulk to save ${item.estimated_price * 0.5:.2f}"
                })
        
        return bulk_recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_store_route(self, items: List[IngredientItem]) -> List[str]:
        """Generate optimal route through store."""
        categories = []
        for item in items:
            if item.category not in categories:
                categories.append(item.category)
        
        # Sort by store layout
        sorted_categories = sorted(categories, key=lambda cat: self.store_layout.get(cat, 99))
        
        return [cat.value for cat in sorted_categories]
    
    def _estimate_shopping_time(self, items: List[IngredientItem]) -> int:
        """Estimate shopping time in minutes."""
        base_time = 15  # Base time for any shopping trip
        item_time = len(items) * 2  # 2 minutes per item
        category_time = len(set(item.category for item in items)) * 3  # 3 minutes per category
        
        return base_time + item_time + category_time
    
    def _calculate_potential_savings(self, shopping_list: ShoppingList) -> float:
        """Calculate potential savings from optimization."""
        # Simplified calculation - in real implementation, compare with historical data
        total = shopping_list.estimated_total or 0
        return total * 0.15  # Assume 15% potential savings
    
    async def _get_seasonal_suggestions(self, items: List[IngredientItem]) -> List[Dict[str, Any]]:
        """Get seasonal ingredient suggestions."""
        current_month = datetime.now().month
        seasonal_items = []
        
        # Simplified seasonal data
        seasonal_map = {
            'spring': ['asparagus', 'peas', 'strawberries', 'artichokes'],
            'summer': ['tomatoes', 'corn', 'berries', 'zucchini'],
            'fall': ['apples', 'pumpkin', 'squash', 'cranberries'],
            'winter': ['citrus', 'root vegetables', 'brussels sprouts', 'cabbage']
        }
        
        season = 'spring' if 3 <= current_month <= 5 else \
                'summer' if 6 <= current_month <= 8 else \
                'fall' if 9 <= current_month <= 11 else 'winter'
        
        seasonal_ingredients = seasonal_map.get(season, [])
        
        for item in items:
            for seasonal_item in seasonal_ingredients:
                if seasonal_item in item.name.lower():
                    seasonal_items.append({
                        'item': item.name,
                        'season': season,
                        'suggestion': f"{item.name} is in season - great time to buy!",
                        'expected_savings': '10-30%'
                    })
        
        return seasonal_items[:3]  # Limit to top 3
    
    def _units_compatible(self, unit1: Optional[Unit], unit2: Optional[Unit]) -> bool:
        """Check if two units are compatible for conversion."""
        if not unit1 or not unit2:
            return False
        
        volume_units = {Unit.CUP, Unit.CUPS, Unit.TABLESPOON, Unit.TABLESPOONS, 
                       Unit.TEASPOON, Unit.TEASPOONS, Unit.FLUID_OUNCE, Unit.FLUID_OUNCES,
                       Unit.LITER, Unit.LITERS, Unit.MILLILITER, Unit.MILLILITERS}
        
        weight_units = {Unit.POUND, Unit.POUNDS, Unit.OUNCE, Unit.OUNCES,
                       Unit.GRAM, Unit.GRAMS, Unit.KILOGRAM, Unit.KILOGRAMS}
        
        return (unit1 in volume_units and unit2 in volume_units) or \
               (unit1 in weight_units and unit2 in weight_units)
    
    def _convert_to_base_unit(self, quantity: float, unit: Optional[Unit]) -> float:
        """Convert quantity to base unit (cups for volume, pounds for weight)."""
        if not unit:
            return quantity
        
        if unit in self.unit_conversions['volume']:
            return quantity * self.unit_conversions['volume'][unit]
        elif unit in self.unit_conversions['weight']:
            return quantity * self.unit_conversions['weight'][unit]
        
        return quantity
    
    def _convert_from_base_unit(self, quantity: float, unit: Unit) -> float:
        """Convert from base unit to target unit."""
        if unit in self.unit_conversions['volume']:
            return quantity / self.unit_conversions['volume'][unit]
        elif unit in self.unit_conversions['weight']:
            return quantity / self.unit_conversions['weight'][unit]
        
        return quantity
    
    def _choose_better_unit(self, unit1: Optional[Unit], unit2: Optional[Unit], total_qty: float) -> Unit:
        """Choose the better unit for the total quantity."""
        if not unit1:
            return unit2 or Unit.ITEM
        if not unit2:
            return unit1
        
        # Prefer larger units for larger quantities
        if total_qty > 4:
            return unit1 if unit1 in [Unit.CUPS, Unit.POUNDS] else unit2
        
        return unit1  # Default to first unit
    
    async def _save_shopping_list(self, shopping_list: ShoppingList) -> str:
        """Save shopping list to database."""
        try:
            db = self._get_db()
            if not db:
                logger.error("❌ Database connection not available")
                raise RuntimeError("Database service is not available")
            
            doc_ref = db.collection('shopping_lists').document()
            shopping_list_dict = shopping_list.dict(exclude={'id'})
            doc_ref.set(shopping_list_dict)
            logger.info(f"✅ Shopping list saved with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"❌ Error saving shopping list: {e}")
            raise
    
    async def _get_shopping_list(self, user_id: str, list_id: str) -> Optional[ShoppingList]:
        """Get shopping list from database."""
        try:
            db = self._get_db()
            if not db:
                logger.error("❌ Database connection not available")
                raise RuntimeError("Database service is not available")
            
            doc = db.collection('shopping_lists').document(list_id).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get('user_id') == user_id:
                    data['id'] = doc.id
                    logger.info(f"✅ Found shopping list: {data.get('name', list_id)}")
                    return ShoppingList(**data)
                else:
                    logger.warning(f"⚠️ Shopping list {list_id} belongs to different user")
                    return None
            else:
                logger.warning(f"⚠️ Shopping list {list_id} not found")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting shopping list: {e}")
            raise
    
    async def _update_shopping_list(self, shopping_list: ShoppingList) -> None:
        """Update shopping list in database."""
        try:
            db = self._get_db()
            if not db:
                logger.error("❌ Database connection not available")
                raise RuntimeError("Database service is not available")
            
            doc_ref = db.collection('shopping_lists').document(shopping_list.id)
            shopping_list_dict = shopping_list.dict(exclude={'id'})
            doc_ref.update(shopping_list_dict)
            logger.info(f"✅ Shopping list updated: {shopping_list.id}")
        except Exception as e:
            logger.error(f"❌ Error updating shopping list: {e}")
            raise
    
    async def get_user_shopping_lists(self, user_id: str, page: int = 1, limit: int = 12, status_filter: Optional[str] = None):
        """Get user's shopping lists with pagination."""
        try:
            db = self._get_db()
            if not db:
                logger.error("❌ Database connection not available")
                raise RuntimeError("Database service is not available")
            
            # Query shopping lists for the user
            try:
                # Use the new filter() method to avoid deprecation warning
                query = db.collection('shopping_lists').where(filter=firestore.FieldFilter('user_id', '==', user_id))
                
                # Apply status filter if provided
                if status_filter:
                    query = query.where(filter=firestore.FieldFilter('status', '==', status_filter))
                
                # Order by creation date (newest first)
                # This requires a composite index in Firestore
                query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
                
                # Get total count
                total_docs = query.get()
                total = len(total_docs)
                logger.info(f"📊 Found {total} shopping lists for user {user_id}")
                
                # Apply pagination
                offset = (page - 1) * limit
                paginated_docs = query.offset(offset).limit(limit).get()
                
            except Exception as firestore_error:
                error_msg = str(firestore_error)
                if "requires an index" in error_msg and "create it here:" in error_msg:
                    # Extract the URL from the error message
                    import re
                    url_match = re.search(r'https://console\.firebase\.google\.com[^\s]+', error_msg)
                    index_url = url_match.group(0) if url_match else "Firebase Console"
                    
                    logger.error(f"🔍 Firestore index required for shopping lists query")
                    logger.error(f"📋 Please create the index at: {index_url}")
                    logger.error(f"💡 This is a one-time setup for your Firebase project")
                    
                    # For now, fall back to simple query without ordering
                    logger.info("🔄 Falling back to unordered query...")
                    simple_query = db.collection('shopping_lists').where(filter=firestore.FieldFilter('user_id', '==', user_id))
                    if status_filter:
                        simple_query = simple_query.where(filter=firestore.FieldFilter('status', '==', status_filter))
                    
                    total_docs = simple_query.get()
                    total = len(total_docs)
                    
                    # Apply pagination manually
                    offset = (page - 1) * limit
                    paginated_docs = total_docs[offset:offset + limit]
                    
                    logger.warning(f"⚠️ Using unordered results due to missing index. Found {total} shopping lists.")
                else:
                    # Re-raise if it's a different error
                    raise
            
            # Convert to ShoppingList objects
            shopping_lists = []
            for doc in paginated_docs:
                if hasattr(doc, 'to_dict'):
                    data = doc.to_dict()
                    data['id'] = doc.id
                else:
                    # Handle case where doc is already a dict (from manual pagination)
                    data = doc
                
                # Convert to ShoppingList object to ensure proper structure
                shopping_list = ShoppingList(**data)
                shopping_lists.append(shopping_list)
                logger.info(f"✅ Loaded shopping list: {shopping_list.name}")
            
            # Calculate pagination info
            pages = (total + limit - 1) // limit if total > 0 else 1
            has_next = page < pages
            has_prev = page > 1
            
            result = {
                'items': shopping_lists,
                'total': total,
                'page': page,
                'limit': limit,
                'pages': pages,
                'hasNext': has_next,
                'hasPrev': has_prev
            }
            
            logger.info(f"📋 Returning {len(shopping_lists)} shopping lists (page {page}/{pages})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting user shopping lists: {e}")
            raise
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get real shopping list statistics for the user."""
        try:
            db = self._get_db()
            if not db:
                logger.error("❌ Database connection not available")
                raise RuntimeError("Database service is not available")
            
            # Get all shopping lists for the user
            query = db.collection('shopping_lists').where('user_id', '==', user_id)
            docs = query.get()
            
            total_lists = len(docs)
            active_lists = 0
            completed_lists = 0
            total_items = 0
            category_counts = {}
            ingredient_counts = {}
            
            for doc in docs:
                data = doc.to_dict()
                status = data.get('status', 'active')
                
                if status == 'active':
                    active_lists += 1
                elif status == 'completed':
                    completed_lists += 1
                
                # Count items and categories
                items = data.get('items', [])
                total_items += len(items)
                
                for item in items:
                    # Count categories
                    category = item.get('category', 'other')
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                    # Count ingredient names
                    name = item.get('name', '').lower()
                    if name:
                        ingredient_counts[name] = ingredient_counts.get(name, 0) + 1
            
            # Calculate average items per list
            average_items_per_list = total_items / total_lists if total_lists > 0 else 0.0
            
            # Get top categories
            top_categories = [
                {"category": cat, "count": count}
                for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Get top ingredients
            top_ingredients = [
                {"ingredient": ing, "count": count}
                for ing, count in sorted(ingredient_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Estimated savings (simplified calculation)
            estimated_savings = total_lists * 15.0  # Assume $15 savings per list
            
            from app.schemas.shopping_list import ShoppingListStatsResponse
            stats = ShoppingListStatsResponse(
                total_lists=total_lists,
                active_lists=active_lists,
                completed_lists=completed_lists,
                total_items=total_items,
                average_items_per_list=round(average_items_per_list, 2),
                top_categories=top_categories,
                top_ingredients=top_ingredients,
                estimated_savings=estimated_savings
            )
            
            logger.info(f"📊 Statistics calculated for user {user_id}: {total_lists} lists, {total_items} items")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting user statistics: {e}")
            raise


# Global instance
shopping_list_service = ShoppingListService()