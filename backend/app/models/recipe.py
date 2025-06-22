from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class RecipeCategory(str, Enum):
    STARTERS = "Starters"
    MAIN_COURSE = "Main Course"
    DESSERTS = "Desserts"
    BEVERAGES = "Beverages"
    SNACKS = "Snacks"


class RecipeDifficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class DietaryInfo(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten-free"
    DAIRY_FREE = "dairy-free"
    NUT_FREE = "nut-free"
    KETO = "keto"
    PALEO = "paleo"


class Recipe(BaseModel):
    id: Optional[str] = None
    userId: str = Field(..., description="Firebase Auth UID of the recipe owner")
    title: str = Field(..., min_length=3, max_length=100, description="Recipe title")
    instagramUrl: HttpUrl = Field(..., description="Instagram reel/post URL")
    embedCode: str = Field(..., description="Instagram oEmbed HTML code")
    category: RecipeCategory = Field(..., description="Recipe category")
    cookingTime: int = Field(..., ge=1, le=1440, description="Cooking time in minutes")
    difficulty: RecipeDifficulty = Field(..., description="Recipe difficulty level")
    ingredients: List[str] = Field(default_factory=list, max_items=50, description="List of ingredients")
    instructions: str = Field(default="", description="Step-by-step instructions")
    aiExtracted: bool = Field(default=False, description="Whether data was AI extracted")
    tags: List[str] = Field(default_factory=list, max_items=20, description="Recipe tags")
    dietaryInfo: List[DietaryInfo] = Field(default_factory=list, description="Dietary information")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    isPublic: bool = Field(default=False, description="Whether recipe is publicly visible")
    likes: int = Field(default=0, ge=0, description="Number of likes")
    thumbnailUrl: Optional[HttpUrl] = Field(None, description="Thumbnail image URL")

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "firebase-auth-uid-123",
                "title": "Delicious Pasta Recipe",
                "instagramUrl": "https://www.instagram.com/reel/ABC123/",
                "embedCode": "<blockquote class=\"instagram-media\">...</blockquote>",
                "category": "Main Course",
                "cookingTime": 30,
                "difficulty": "Easy",
                "ingredients": ["pasta", "tomato sauce", "cheese"],
                "instructions": "1. Boil pasta\n2. Heat sauce\n3. Combine and serve",
                "aiExtracted": True,
                "tags": ["quick", "italian"],
                "dietaryInfo": ["vegetarian"],
                "isPublic": False,
                "likes": 0
            }
        }


class RecipeCreate(BaseModel):
    instagramUrl: HttpUrl = Field(..., description="Instagram reel/post URL")
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Recipe title")
    category: Optional[RecipeCategory] = Field(None, description="Recipe category")
    isPublic: bool = Field(default=False, description="Whether recipe is publicly visible")


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    category: Optional[RecipeCategory] = None
    cookingTime: Optional[int] = Field(None, ge=1, le=1440)
    difficulty: Optional[RecipeDifficulty] = None
    ingredients: Optional[List[str]] = Field(None, max_items=50)
    instructions: Optional[str] = None
    tags: Optional[List[str]] = Field(None, max_items=20)
    dietaryInfo: Optional[List[DietaryInfo]] = None
    isPublic: Optional[bool] = None


class RecipeResponse(Recipe):
    id: str
    
    class Config:
        from_attributes = True