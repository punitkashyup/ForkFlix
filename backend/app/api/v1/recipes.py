from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from app.core.security import get_current_user
from app.models.recipe import Recipe, RecipeCategory, RecipeDifficulty
from app.schemas.recipe import (
    RecipeCreate,
    RecipeUpdate, 
    RecipeResponse,
    RecipeListQuery,
    PaginatedRecipeResponse,
    RecipeAIReprocessRequest,
    AIExtractionResponse
)
from app.schemas.responses import (
    SuccessResponse,
    ErrorResponse,
    NotFoundResponse,
    ValidationErrorResponse
)
from app.services.firebase_service import firebase_service
from app.services.instagram_service import instagram_service
from app.services.ai_service import ai_service

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create recipe from Instagram URL",
    description="Create a new recipe by extracting data from Instagram URL using AI services",
    responses={
        201: {"model": SuccessResponse, "description": "Recipe created successfully"},
        400: {"model": ValidationErrorResponse, "description": "Invalid Instagram URL or request data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new recipe from Instagram URL with AI extraction"""
    try:
        logger.info(f"Creating recipe for user {current_user['uid']} with URL: {recipe_data.instagramUrl}")
        logger.info(f"📥 Received recipe data: {recipe_data.dict()}")
        
        # Step 1: Validate Instagram URL
        instagram_url = str(recipe_data.instagramUrl)
        validation_result = await instagram_service.validate_url(instagram_url)
        
        if not validation_result["isValid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Instagram URL: {validation_result['message']}"
            )
        
        # Step 2: Get Instagram metadata and embed code
        try:
            metadata = await instagram_service.get_metadata(instagram_url)
            embed_result = await instagram_service.get_embed_code(instagram_url)
        except Exception as e:
            logger.error(f"Instagram service error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch Instagram content. The post might be private or deleted."
            )
        
        # Step 3: Use provided recipe data or extract with AI as fallback
        ai_result = None
        
        # Check if frontend already provided extracted data
        has_frontend_data = (recipe_data.ingredients and len(recipe_data.ingredients) > 0) or recipe_data.instructions
        
        if not has_frontend_data:
            # Only run AI extraction if frontend didn't provide data
            try:
                ai_result = await ai_service.extract_from_instagram(
                    instagram_url=instagram_url,
                    thumbnail_url=metadata.get("thumbnailUrl"),
                    description=metadata.get("description", ""),
                    caption=metadata.get("title", "")
                )
                logger.info(f"AI extraction completed with confidence: {ai_result.get('confidence', 0)}")
            except Exception as e:
                logger.warning(f"AI extraction failed, using manual data: {e}")
                # Continue without AI data if extraction fails
        else:
            logger.info("Using frontend-provided extracted data, skipping backend AI extraction")
        
        # Step 4: Prepare recipe data (prioritize frontend data over AI extraction)
        recipe_dict = {
            "userId": current_user["uid"],
            "title": recipe_data.title or (ai_result.get("title") if ai_result else metadata.get("title", "Recipe from Instagram")),
            "instagramUrl": instagram_url,
            "embedCode": recipe_data.embedCode or embed_result["embedCode"],
            "category": recipe_data.category or (ai_result.get("category") if ai_result else "Main Course"),
            "cookingTime": recipe_data.cookingTime or (ai_result.get("cookingTime", 30) if ai_result else 30),
            "difficulty": recipe_data.difficulty or (ai_result.get("difficulty", "Medium") if ai_result else "Medium"),
            "ingredients": recipe_data.ingredients or (ai_result.get("ingredients", []) if ai_result else []),
            "instructions": recipe_data.instructions or (ai_result.get("instructions", "") if ai_result else ""),
            "aiExtracted": recipe_data.aiExtracted or (ai_result is not None),
            "tags": ai_result.get("tags", []) if ai_result else [],
            "dietaryInfo": ai_result.get("dietaryInfo", []) if ai_result else [],
            "isPublic": recipe_data.isPublic,
            "likes": 0,
            "thumbnailUrl": recipe_data.thumbnailUrl or metadata.get("thumbnailUrl")
        }
        
        # Add extraction metadata if provided
        if recipe_data.extractionMethod:
            recipe_dict["extractionMethod"] = recipe_data.extractionMethod
        if recipe_data.confidence is not None:
            recipe_dict["confidence"] = recipe_data.confidence
        
        # Step 5: Save to Firebase
        recipe_id = await firebase_service.create_recipe(recipe_dict)
        recipe_dict["id"] = recipe_id
        
        logger.info(f"Recipe created successfully with ID: {recipe_id}")
        
        return SuccessResponse(
            message="Recipe created successfully",
            data={
                "recipe": recipe_dict,
                "aiConfidence": recipe_data.confidence or (ai_result.get("confidence", 0) if ai_result else 0),
                "extractedByAI": recipe_data.aiExtracted or (ai_result is not None)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating recipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the recipe"
        )


@router.get(
    "/",
    response_model=PaginatedRecipeResponse,
    summary="List recipes with pagination and filtering",
    description="Get a paginated list of recipes with optional filtering by category, difficulty, tags, and search"
)
async def list_recipes(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    limit: int = Query(default=12, ge=1, le=50, description="Number of recipes per page"),
    category: Optional[RecipeCategory] = Query(default=None, description="Filter by category"),
    difficulty: Optional[RecipeDifficulty] = Query(default=None, description="Filter by difficulty"),
    tags: Optional[str] = Query(default=None, description="Comma-separated tags to filter by"),
    search: Optional[str] = Query(default=None, description="Search in recipe titles"),
    public_only: bool = Query(default=False, description="Show only public recipes"),
    current_user: dict = Depends(get_current_user)
):
    """List recipes with pagination and filtering"""
    try:
        # Parse tags if provided
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None
        
        # Create query parameters
        query_params = RecipeListQuery(
            page=page,
            limit=limit,
            category=category,
            difficulty=difficulty,
            tags=tag_list,
            search=search,
            public_only=public_only
        )
        
        # Get recipes from Firebase
        result = await firebase_service.list_recipes(
            query_params=query_params,
            user_id=current_user["uid"] if not public_only else None
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing recipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recipes"
        )


@router.get(
    "/{recipe_id}",
    response_model=SuccessResponse,
    summary="Get recipe by ID",
    description="Retrieve a single recipe by its ID",
    responses={
        200: {"model": SuccessResponse, "description": "Recipe retrieved successfully"},
        404: {"model": NotFoundResponse, "description": "Recipe not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
async def get_recipe(
    recipe_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single recipe by ID"""
    try:
        recipe = await firebase_service.get_recipe(recipe_id, current_user["uid"])
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or access denied"
            )
        
        return SuccessResponse(
            message="Recipe retrieved successfully",
            data=recipe
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recipe"
        )


@router.put(
    "/{recipe_id}",
    response_model=SuccessResponse,
    summary="Update recipe",
    description="Update an existing recipe (only by owner)",
    responses={
        200: {"model": SuccessResponse, "description": "Recipe updated successfully"},
        404: {"model": NotFoundResponse, "description": "Recipe not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
async def update_recipe(
    recipe_id: str,
    recipe_data: RecipeUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing recipe"""
    try:
        # Prepare update data (only include non-None fields)
        update_data = {}
        for field, value in recipe_data.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        # Update in Firebase
        success = await firebase_service.update_recipe(
            recipe_id=recipe_id,
            user_id=current_user["uid"],
            update_data=update_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or access denied"
            )
        
        # Get updated recipe
        updated_recipe = await firebase_service.get_recipe(recipe_id, current_user["uid"])
        
        return SuccessResponse(
            message="Recipe updated successfully",
            data=updated_recipe
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recipe"
        )


@router.delete(
    "/{recipe_id}",
    response_model=SuccessResponse,
    summary="Delete recipe",
    description="Delete a recipe (only by owner)",
    responses={
        200: {"model": SuccessResponse, "description": "Recipe deleted successfully"},
        404: {"model": NotFoundResponse, "description": "Recipe not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
async def delete_recipe(
    recipe_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a recipe"""
    try:
        success = await firebase_service.delete_recipe(
            recipe_id=recipe_id,
            user_id=current_user["uid"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or access denied"
            )
        
        return SuccessResponse(
            message="Recipe deleted successfully",
            data={"deleted_id": recipe_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recipe"
        )


@router.post(
    "/{recipe_id}/ai",
    response_model=SuccessResponse,
    summary="Re-run AI extraction on recipe",
    description="Re-process an existing recipe with AI to extract updated information",
    responses={
        200: {"model": SuccessResponse, "description": "AI re-processing completed"},
        404: {"model": NotFoundResponse, "description": "Recipe not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
async def reprocess_recipe_ai(
    recipe_id: str,
    reprocess_options: RecipeAIReprocessRequest,
    current_user: dict = Depends(get_current_user)
):
    """Re-run AI extraction on an existing recipe"""
    try:
        # Get existing recipe
        recipe = await firebase_service.get_recipe(recipe_id, current_user["uid"])
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or access denied"
            )
        
        if recipe["userId"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only reprocess your own recipes"
            )
        
        # Re-run AI extraction
        try:
            ai_result = await ai_service.extract_from_instagram(
                instagram_url=recipe["instagramUrl"],
                thumbnail_url=recipe.get("thumbnailUrl"),
                extract_ingredients=reprocess_options.extractIngredients,
                categorize=reprocess_options.categorize,
                extract_instructions=reprocess_options.extractInstructions
            )
        except Exception as e:
            logger.error(f"AI re-processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI processing failed. Please try again later."
            )
        
        # Prepare update data based on reprocessing options
        update_data = {"aiExtracted": True}
        
        if reprocess_options.extractIngredients and ai_result.get("ingredients"):
            update_data["ingredients"] = ai_result["ingredients"]
        
        if reprocess_options.categorize and ai_result.get("category"):
            update_data["category"] = ai_result["category"]
        
        if reprocess_options.extractInstructions and ai_result.get("instructions"):
            update_data["instructions"] = ai_result["instructions"]
        
        # Always update these if available
        if ai_result.get("cookingTime"):
            update_data["cookingTime"] = ai_result["cookingTime"]
        if ai_result.get("difficulty"):
            update_data["difficulty"] = ai_result["difficulty"]
        if ai_result.get("tags"):
            update_data["tags"] = ai_result["tags"]
        if ai_result.get("dietaryInfo"):
            update_data["dietaryInfo"] = ai_result["dietaryInfo"]
        
        # Update recipe in Firebase
        await firebase_service.update_recipe(
            recipe_id=recipe_id,
            user_id=current_user["uid"],
            update_data=update_data
        )
        
        # Get updated recipe
        updated_recipe = await firebase_service.get_recipe(recipe_id, current_user["uid"])
        
        return SuccessResponse(
            message="Recipe re-processed successfully with AI",
            data={
                "recipe": updated_recipe,
                "aiConfidence": ai_result.get("confidence", 0),
                "extractedFields": list(update_data.keys())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reprocess recipe with AI"
        )