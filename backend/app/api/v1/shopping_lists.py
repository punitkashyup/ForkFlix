from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import logging
from app.schemas.shopping_list import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    PaginatedShoppingListResponse, GenerateShoppingListRequest,
    ShoppingListOptimizationRequest, ShoppingListOptimizationResponse,
    BulkProcessIngredientsRequest, BulkProcessIngredientsResponse,
    ShoppingListStatsResponse, IngredientItemCreate, IngredientItemUpdate
)
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.services.shopping_list_service import shopping_list_service
from app.services.ingredient_processor import ingredient_processor
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=SuccessResponse[ShoppingListResponse])
async def generate_shopping_list(
    request: GenerateShoppingListRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a smart shopping list from multiple recipes with AI optimization."""
    try:
        user_id = current_user["uid"]
        logger.info(f"Generating shopping list for user: {user_id}")
        
        shopping_list = await shopping_list_service.generate_shopping_list(
            user_id, request
        )
        
        return SuccessResponse(
            success=True,
            message="Shopping list generated successfully",
            data=shopping_list
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate shopping list"
        )


@router.get("/", response_model=SuccessResponse[PaginatedShoppingListResponse])
async def get_shopping_lists(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=50, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user)
):
    """Get user's shopping lists with pagination."""
    try:
        user_id = current_user["uid"]
        logger.info(f"Fetching shopping lists for user: {user_id}")
        
        # Get shopping lists from service
        shopping_lists = await shopping_list_service.get_user_shopping_lists(
            user_id=user_id,
            page=page,
            limit=limit,
            status_filter=status_filter
        )
        
        return SuccessResponse(
            success=True,
            message="Shopping lists retrieved successfully",
            data=shopping_lists
        )
        
    except Exception as e:
        logger.error(f"Error getting shopping lists: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shopping lists"
        )


@router.get("/{list_id}", response_model=SuccessResponse[ShoppingListResponse])
async def get_shopping_list(
    list_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific shopping list by ID."""
    try:
        shopping_list = await shopping_list_service._get_shopping_list(
            current_user["uid"], list_id
        )
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shopping list not found"
            )
        
        return SuccessResponse(
            success=True,
            message="Shopping list retrieved successfully",
            data=shopping_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shopping list"
        )


@router.put("/{list_id}", response_model=SuccessResponse[ShoppingListResponse])
async def update_shopping_list(
    list_id: str,
    update_data: ShoppingListUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a shopping list."""
    try:
        # Get existing list
        shopping_list = await shopping_list_service._get_shopping_list(
            current_user["uid"], list_id
        )
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shopping list not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(shopping_list, field, value)
        
        # Save updated list
        await shopping_list_service._update_shopping_list(shopping_list)
        
        return SuccessResponse(
            success=True,
            message="Shopping list updated successfully",
            data=shopping_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update shopping list"
        )


@router.delete("/{list_id}", response_model=SuccessResponse[dict])
async def delete_shopping_list(
    list_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a shopping list."""
    try:
        # Verify ownership and delete
        shopping_list = await shopping_list_service._get_shopping_list(
            current_user["uid"], list_id
        )
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shopping list not found"
            )
        
        # Delete from database
        db = shopping_list_service._get_db()
        if db:
            db.collection('shopping_lists').document(list_id).delete()
        else:
            logger.warning("Database not available - skipping delete operation")
        
        return SuccessResponse(
            success=True,
            message="Shopping list deleted successfully",
            data={"deleted_id": list_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete shopping list"
        )


@router.post("/{list_id}/optimize", response_model=SuccessResponse[ShoppingListOptimizationResponse])
async def optimize_shopping_list(
    list_id: str,
    optimization_request: ShoppingListOptimizationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Optimize a shopping list for cost, time, and efficiency."""
    try:
        optimization_request.shopping_list_id = list_id
        
        optimization_result = await shopping_list_service.optimize_shopping_list(
            current_user["uid"], optimization_request
        )
        
        return SuccessResponse(
            success=True,
            message="Shopping list optimized successfully",
            data=optimization_result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error optimizing shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize shopping list"
        )


@router.post("/{list_id}/items", response_model=SuccessResponse[dict])
async def add_item_to_list(
    list_id: str,
    item: IngredientItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add an item to a shopping list."""
    try:
        shopping_list = await shopping_list_service._get_shopping_list(
            current_user["uid"], list_id
        )
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shopping list not found"
            )
        
        # Process the ingredient if needed
        if not item.category:
            processed = ingredient_processor.process_ingredient(item.name)
            item.category = processed.category
        
        # Add item to list
        from app.models.shopping_list import IngredientItem
        new_item = IngredientItem(**item.dict())
        shopping_list.items.append(new_item)
        shopping_list.total_items = len(shopping_list.items)
        
        # Update estimated total
        if new_item.estimated_price:
            shopping_list.estimated_total = (shopping_list.estimated_total or 0) + new_item.estimated_price
        
        await shopping_list_service._update_shopping_list(shopping_list)
        
        return SuccessResponse(
            success=True,
            message="Item added to shopping list successfully",
            data={"item_added": item.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to shopping list"
        )


@router.put("/{list_id}/items/{item_index}", response_model=SuccessResponse[dict])
async def update_list_item(
    list_id: str,
    item_index: int,
    item_update: IngredientItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an item in a shopping list."""
    try:
        shopping_list = await shopping_list_service._get_shopping_list(
            current_user["uid"], list_id
        )
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shopping list not found"
            )
        
        if item_index >= len(shopping_list.items):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Update item
        item = shopping_list.items[item_index]
        update_dict = item_update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(item, field, value)
        
        # Update checked items count
        shopping_list.checked_items = sum(1 for item in shopping_list.items if item.is_checked)
        
        await shopping_list_service._update_shopping_list(shopping_list)
        
        return SuccessResponse(
            success=True,
            message="Item updated successfully",
            data={"updated_item": item.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating list item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update list item"
        )


@router.delete("/{list_id}/items/{item_index}", response_model=SuccessResponse[dict])
async def remove_item_from_list(
    list_id: str,
    item_index: int,
    current_user: dict = Depends(get_current_user)
):
    """Remove an item from a shopping list."""
    try:
        shopping_list = await shopping_list_service._get_shopping_list(
            current_user["uid"], list_id
        )
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shopping list not found"
            )
        
        if item_index >= len(shopping_list.items):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Remove item
        removed_item = shopping_list.items.pop(item_index)
        shopping_list.total_items = len(shopping_list.items)
        shopping_list.checked_items = sum(1 for item in shopping_list.items if item.is_checked)
        
        # Update estimated total
        if removed_item.estimated_price:
            shopping_list.estimated_total = max(0, (shopping_list.estimated_total or 0) - removed_item.estimated_price)
        
        await shopping_list_service._update_shopping_list(shopping_list)
        
        return SuccessResponse(
            success=True,
            message="Item removed from shopping list successfully",
            data={"removed_item": removed_item.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item from shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from shopping list"
        )


# Ingredient Processing Endpoints
@router.post("/ingredients/process", response_model=SuccessResponse[BulkProcessIngredientsResponse])
async def process_ingredients_bulk(
    request: BulkProcessIngredientsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process multiple ingredient strings with NLP for smart extraction."""
    try:
        processed_ingredients = ingredient_processor.process_ingredients_bulk(
            request.ingredients, 
            request.recipe_id, 
            request.dietary_restrictions
        )
        
        successful = sum(1 for ing in processed_ingredients if ing.confidence > 0.5)
        failed = len(processed_ingredients) - successful
        avg_confidence = sum(ing.confidence for ing in processed_ingredients) / len(processed_ingredients)
        
        response = BulkProcessIngredientsResponse(
            processed_ingredients=processed_ingredients,
            total_processed=len(processed_ingredients),
            successful_extractions=successful,
            failed_extractions=failed,
            confidence_average=avg_confidence
        )
        
        return SuccessResponse(
            success=True,
            message=f"Processed {len(processed_ingredients)} ingredients successfully",
            data=response
        )
        
    except Exception as e:
        logger.error(f"Error processing ingredients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process ingredients"
        )




# Statistics Endpoint
@router.get("/stats", response_model=SuccessResponse[ShoppingListStatsResponse])
async def get_shopping_list_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get shopping list statistics for the user."""
    try:
        user_id = current_user["uid"]
        logger.info(f"Getting shopping list statistics for user: {user_id}")
        
        # Get real statistics from the shopping list service
        stats = await shopping_list_service.get_user_statistics(user_id)
        
        return SuccessResponse(
            success=True,
            message="Shopping list statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting shopping list stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shopping list statistics"
        )