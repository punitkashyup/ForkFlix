from typing import Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from app.models.user import UserPreferences


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")
    displayName: str = Field(..., min_length=1, max_length=100, description="Display name")


class SignupResponse(BaseModel):
    message: str = Field(..., description="Signup success message")
    user: dict = Field(..., description="Created user information")


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="User email for password reset")


class PasswordResetResponse(BaseModel):
    message: str = Field(..., description="Password reset success message")


class ProfileUpdateRequest(BaseModel):
    displayName: Optional[str] = Field(None, min_length=1, max_length=100)
    photoURL: Optional[HttpUrl] = None
    preferences: Optional[UserPreferences] = None


class ProfileResponse(BaseModel):
    uid: str
    email: EmailStr
    displayName: str
    photoURL: Optional[HttpUrl] = None
    recipeCount: int
    preferences: UserPreferences
    memberSince: str = Field(..., description="ISO formatted date string")


class UserStatsResponse(BaseModel):
    totalRecipes: int = Field(..., ge=0, description="Total recipes created")
    publicRecipes: int = Field(..., ge=0, description="Public recipes")
    totalLikes: int = Field(..., ge=0, description="Total likes received")
    averageCookingTime: float = Field(..., ge=0, description="Average cooking time")
    favoriteCategory: str = Field(..., description="Most used category")
    recipesThisMonth: int = Field(..., ge=0, description="Recipes created this month")