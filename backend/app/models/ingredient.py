from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100, description="Ingredient name")
    category: Optional[str] = Field(None, max_length=50, description="Ingredient category")
    isCommon: bool = Field(default=False, description="Whether this is a common ingredient")
    alternatives: List[str] = Field(default_factory=list, max_items=10, description="Alternative ingredients")
    nutritionInfo: Optional[dict] = Field(None, description="Nutrition information per 100g")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tomato",
                "category": "Vegetable",
                "isCommon": True,
                "alternatives": ["Cherry tomatoes", "Canned tomatoes"],
                "nutritionInfo": {
                    "calories": 18,
                    "protein": 0.9,
                    "carbs": 3.9,
                    "fat": 0.2
                }
            }
        }


class IngredientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    isCommon: bool = Field(default=False)
    alternatives: List[str] = Field(default_factory=list, max_items=10)
    nutritionInfo: Optional[dict] = None


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    isCommon: Optional[bool] = None
    alternatives: Optional[List[str]] = Field(None, max_items=10)
    nutritionInfo: Optional[dict] = None


class IngredientResponse(Ingredient):
    id: str
    
    class Config:
        from_attributes = True