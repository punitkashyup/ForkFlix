from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from app.models.recipe import RecipeCategory


class UserPreferences(BaseModel):
    defaultCategory: RecipeCategory = Field(default=RecipeCategory.MAIN_COURSE)
    aiAutoExtract: bool = Field(default=True, description="Auto-extract recipe info using AI")
    publicRecipes: bool = Field(default=False, description="Make recipes public by default")


class User(BaseModel):
    uid: str = Field(..., description="Firebase Auth UID")
    email: str = Field(..., description="User email address")
    displayName: str = Field(..., min_length=1, max_length=100, description="Display name")
    photoURL: Optional[HttpUrl] = Field(None, description="Profile picture URL")
    recipeCount: int = Field(default=0, ge=0, description="Number of recipes created")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    class Config:
        json_schema_extra = {
            "example": {
                "uid": "firebase-auth-uid-123",
                "email": "user@example.com",
                "displayName": "John Doe",
                "photoURL": "https://example.com/photo.jpg",
                "recipeCount": 5,
                "preferences": {
                    "defaultCategory": "Main Course",
                    "aiAutoExtract": True,
                    "publicRecipes": False
                }
            }
        }


class UserCreate(BaseModel):
    email: str
    displayName: str = Field(..., min_length=1, max_length=100)
    photoURL: Optional[HttpUrl] = None


class UserUpdate(BaseModel):
    displayName: Optional[str] = Field(None, min_length=1, max_length=100)
    photoURL: Optional[HttpUrl] = None
    preferences: Optional[UserPreferences] = None


class UserResponse(User):
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    uid: str
    email: str
    displayName: str
    photoURL: Optional[HttpUrl] = None
    recipeCount: int
    preferences: UserPreferences
    memberSince: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True