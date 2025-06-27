from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ShoppingListStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ItemCategory(str, Enum):
    PRODUCE = "produce"
    MEAT_SEAFOOD = "meat_seafood"
    DAIRY_EGGS = "dairy_eggs"
    PANTRY = "pantry"
    FROZEN = "frozen"
    BAKERY = "bakery"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    HOUSEHOLD = "household"
    OTHER = "other"


class Unit(str, Enum):
    # Volume
    CUP = "cup"
    CUPS = "cups"
    TABLESPOON = "tablespoon"
    TABLESPOONS = "tablespoons"
    TEASPOON = "teaspoon"
    TEASPOONS = "teaspoons"
    LITER = "liter"
    LITERS = "liters"
    MILLILITER = "milliliter"
    MILLILITERS = "milliliters"
    FLUID_OUNCE = "fluid_ounce"
    FLUID_OUNCES = "fluid_ounces"
    
    # Weight
    POUND = "pound"
    POUNDS = "pounds"
    OUNCE = "ounce"
    OUNCES = "ounces"
    GRAM = "gram"
    GRAMS = "grams"
    KILOGRAM = "kilogram"
    KILOGRAMS = "kilograms"
    
    # Count
    PIECE = "piece"
    PIECES = "pieces"
    ITEM = "item"
    ITEMS = "items"
    CLOVE = "clove"
    CLOVES = "cloves"
    
    # Other
    PINCH = "pinch"
    DASH = "dash"
    TO_TASTE = "to_taste"
    PACKAGE = "package"
    PACKAGES = "packages"
    CAN = "can"
    CANS = "cans"
    BOTTLE = "bottle"
    BOTTLES = "bottles"


class IngredientItem(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200, description="Ingredient name")
    quantity: Optional[float] = Field(None, ge=0, description="Quantity needed")
    unit: Optional[Unit] = Field(None, description="Unit of measurement")
    category: Optional[ItemCategory] = Field(None, description="Grocery store category")
    is_checked: bool = Field(default=False, description="Whether item is checked off")
    recipe_ids: List[str] = Field(default_factory=list, description="Recipe IDs that need this ingredient")
    alternatives: List[str] = Field(default_factory=list, description="Alternative ingredient suggestions")
    estimated_price: Optional[float] = Field(None, ge=0, description="Estimated item price")


class ShoppingList(BaseModel):
    id: Optional[str] = None
    user_id: str = Field(..., description="Firebase Auth UID of the list owner")
    name: str = Field(..., min_length=1, max_length=100, description="Shopping list name")
    description: Optional[str] = Field(None, description="List description")
    status: ShoppingListStatus = Field(default=ShoppingListStatus.ACTIVE, description="List status")
    items: List[IngredientItem] = Field(default_factory=list, description="Shopping list items")
    recipe_ids: List[str] = Field(default_factory=list, description="Recipe IDs included in this list")
    
    # Simplified model - removed store preferences, dietary restrictions, budget limit, and pricing
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="When list was completed")
    
    # Analytics
    total_items: int = Field(default=0, description="Total number of items")
    checked_items: int = Field(default=0, description="Number of checked items")
    estimated_total: Optional[float] = Field(None, ge=0, description="Estimated total cost")
    budget_limit: Optional[float] = Field(None, ge=0, description="Budget limit for this list")
    
    # Additional fields for response compatibility
    optimization: Optional['ShoppingOptimization'] = Field(None, description="Optimization data")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "firebase-auth-uid-123",
                "name": "Weekend Meal Prep",
                "description": "Shopping list for this weekend's meal prep recipes",
                "status": "active",
                "recipe_ids": ["recipe-1", "recipe-2"],
                "store_preferences": ["Whole Foods", "Trader Joe's"],
                "dietary_restrictions": ["gluten-free"],
                "budget_limit": 75.00,
                "items": [
                    {
                        "name": "Chicken Breast",
                        "quantity": 2.0,
                        "unit": "pounds",
                        "category": "meat_seafood",
                        "estimated_price": 12.99,
                        "recipe_ids": ["recipe-1"]
                    }
                ]
            }
        }


class PantryItem(BaseModel):
    id: Optional[str] = None
    user_id: str = Field(..., description="Firebase Auth UID of the owner")
    name: str = Field(..., min_length=1, max_length=200, description="Item name")
    quantity: float = Field(..., gt=0, description="Current quantity")
    unit: Unit = Field(..., description="Unit of measurement")
    category: ItemCategory = Field(..., description="Item category")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date")
    location: Optional[str] = Field(None, description="Storage location (fridge, pantry, etc.)")
    minimum_stock: Optional[float] = Field(None, ge=0, description="Minimum stock level")
    auto_replenish: bool = Field(default=False, description="Auto-add to shopping list when low")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ShoppingOptimization(BaseModel):
    """Model for shopping optimization recommendations"""
    user_id: str = Field(..., description="Firebase Auth UID")
    recommendations: Dict[str, Any] = Field(..., description="Optimization recommendations")
    store_route: Optional[List[str]] = Field(None, description="Optimized store route")
    estimated_time: Optional[int] = Field(None, description="Estimated shopping time in minutes")
    cost_savings: Optional[float] = Field(None, description="Potential cost savings")
    bulk_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Bulk buying opportunities")
    seasonal_suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Seasonal alternatives")
    created_at: datetime = Field(default_factory=datetime.utcnow)