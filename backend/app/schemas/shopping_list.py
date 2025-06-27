from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.shopping_list import (
    ShoppingListStatus, ItemCategory, Unit, IngredientItem, 
    PantryItem, ShoppingOptimization
)


class ShoppingListCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    recipe_ids: List[str] = Field(..., min_items=1)
    consolidate_duplicates: bool = Field(default=True)
    check_pantry: bool = Field(default=True)
    optimize_categories: bool = Field(default=True)
    include_alternatives: bool = Field(default=True)
    store_preferences: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    budget_limit: Optional[float] = Field(None, ge=0)


class ShoppingListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[ShoppingListStatus] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class ShoppingListResponse(BaseModel):
    id: str
    user_id: str
    name: str
    recipe_ids: List[str]
    items: List[IngredientItem]
    status: ShoppingListStatus
    total_items: int
    checked_items: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    optimization: Optional[ShoppingOptimization]
    notes: Optional[str]

    class Config:
        from_attributes = True


class PaginatedShoppingListResponse(BaseModel):
    items: List[ShoppingListResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1)
    pages: int = Field(..., ge=1)  # Minimum 1 page
    hasNext: bool
    hasPrev: bool


class GenerateShoppingListRequest(BaseModel):
    recipe_ids: List[str] = Field(..., min_items=1, description="Recipe IDs to include")
    list_name: str = Field(..., min_length=1, max_length=200, description="Shopping list name")
    consolidate_duplicates: bool = Field(default=True, description="Merge duplicate ingredients")


class ShoppingListOptimizationRequest(BaseModel):
    shopping_list_id: Optional[str] = None
    budget_priority: bool = Field(default=False, description="Prioritize cost optimization")
    time_priority: bool = Field(default=True, description="Prioritize time efficiency")
    include_bulk_recommendations: bool = Field(default=True, description="Include bulk buying suggestions")
    store_layout: Optional[Dict[str, int]] = Field(None, description="Store section order")


class ShoppingListOptimizationResponse(BaseModel):
    optimized_list: ShoppingListResponse
    optimization_data: Dict[str, Any]
    savings_summary: Dict[str, float]
    shopping_route: List[str]
    bulk_recommendations: List[Dict[str, Any]]
    estimated_time: int
    confidence_score: float


# Pantry Item Schemas
class PantryItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: ItemCategory
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[Unit] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None


class PantryItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[ItemCategory] = None
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[Unit] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None


class PantryItemResponse(BaseModel):
    id: str
    user_id: str
    name: str
    category: ItemCategory
    quantity: Optional[float]
    unit: Optional[Unit]
    expiry_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Ingredient Processing Schemas
class BulkProcessIngredientsRequest(BaseModel):
    ingredients: List[str] = Field(..., min_items=1, description="Raw ingredient strings")
    recipe_id: Optional[str] = Field(None, description="Associated recipe ID")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions")


class ProcessedIngredient(BaseModel):
    original_text: str
    name: str
    quantity: Optional[float]
    unit: Optional[Unit]
    category: ItemCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    alternatives: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class BulkProcessIngredientsResponse(BaseModel):
    processed_ingredients: List[ProcessedIngredient]
    total_processed: int = Field(..., ge=0)
    successful_extractions: int = Field(..., ge=0)
    failed_extractions: int = Field(..., ge=0)
    confidence_average: float = Field(..., ge=0.0, le=1.0)


# Item Management Schemas
class IngredientItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[Unit] = None
    category: Optional[ItemCategory] = None
    notes: Optional[str] = None
    recipe_source: Optional[str] = None


class IngredientItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[Unit] = None
    category: Optional[ItemCategory] = None
    is_checked: Optional[bool] = None
    notes: Optional[str] = None
    estimated_price: Optional[float] = Field(None, ge=0)


# Statistics Schema
class ShoppingListStatsResponse(BaseModel):
    total_lists: int = Field(..., ge=0)
    active_lists: int = Field(..., ge=0)
    completed_lists: int = Field(..., ge=0)
    total_items: int = Field(..., ge=0)
    average_items_per_list: float = Field(..., ge=0.0)
    top_categories: List[Dict[str, Any]] = Field(default_factory=list)
    top_ingredients: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_savings: float = Field(..., ge=0.0)