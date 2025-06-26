from typing import List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from app.models.recipe import Recipe, RecipeCategory, RecipeDifficulty, DietaryInfo


class RecipeCreate(BaseModel):
    instagramUrl: HttpUrl = Field(..., description="Instagram reel/post URL")
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Recipe title")
    category: Optional[RecipeCategory] = Field(None, description="Recipe category")
    cookingTime: Optional[int] = Field(None, ge=1, le=1440, description="Cooking time in minutes")
    difficulty: Optional[RecipeDifficulty] = Field(None, description="Recipe difficulty")
    ingredients: Optional[List[str]] = Field(None, max_items=50, description="Recipe ingredients")
    instructions: Optional[str] = Field(None, description="Cooking instructions")
    embedCode: Optional[str] = Field(None, description="Instagram embed code")
    thumbnailUrl: Optional[str] = Field(None, description="Recipe thumbnail URL")
    aiExtracted: Optional[bool] = Field(default=False, description="Whether data was AI extracted")
    extractionMethod: Optional[str] = Field(None, description="AI extraction method used")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="AI extraction confidence")
    isPublic: bool = Field(default=False, description="Whether recipe is publicly visible")

    @validator('thumbnailUrl', pre=True)
    def validate_thumbnail_url(cls, v):
        if v == "" or v is None:
            return None
        return v

    @validator('embedCode', pre=True)
    def validate_embed_code(cls, v):
        if v == "" or v is None:
            return None
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "instagramUrl": "https://www.instagram.com/reel/ABC123/",
                "title": "Delicious Pasta Recipe",
                "category": "Main Course",
                "cookingTime": 30,
                "difficulty": "Medium",
                "ingredients": ["pasta", "tomatoes", "garlic"],
                "instructions": "Cook pasta, add sauce, serve hot",
                "aiExtracted": True,
                "isPublic": False
            }
        }


class RecipeUpdate(BaseModel):
    instagramUrl: Optional[HttpUrl] = Field(None, description="Instagram reel/post URL")
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    category: Optional[RecipeCategory] = None
    cookingTime: Optional[int] = Field(None, ge=1, le=1440)
    difficulty: Optional[RecipeDifficulty] = None
    ingredients: Optional[List[str]] = Field(None, max_items=50)
    instructions: Optional[str] = None
    embedCode: Optional[str] = Field(None, description="Instagram embed code")
    thumbnailUrl: Optional[str] = Field(None, description="Recipe thumbnail URL")
    aiExtracted: Optional[bool] = Field(None, description="Whether data was AI extracted")
    extractionMethod: Optional[str] = Field(None, description="AI extraction method used")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="AI extraction confidence")
    tags: Optional[List[str]] = Field(None, max_items=20)
    dietaryInfo: Optional[List[DietaryInfo]] = None
    isPublic: Optional[bool] = None

    @validator('thumbnailUrl', pre=True)
    def validate_thumbnail_url(cls, v):
        if v == "" or v is None:
            return None
        return v

    @validator('embedCode', pre=True)
    def validate_embed_code(cls, v):
        if v == "" or v is None:
            return None
        return v


class RecipeResponse(Recipe):
    id: str
    
    class Config:
        from_attributes = True


class RecipeListQuery(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=12, ge=1, le=50, description="Items per page")
    category: Optional[RecipeCategory] = Field(None, description="Filter by category")
    difficulty: Optional[RecipeDifficulty] = Field(None, description="Filter by difficulty")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search query")
    public_only: bool = Field(default=False, description="Show only public recipes")


class PaginatedRecipeResponse(BaseModel):
    items: List[Recipe]
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=1, description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there are more pages")
    hasPrev: bool = Field(..., description="Whether there are previous pages")


class InstagramValidationRequest(BaseModel):
    url: HttpUrl = Field(..., description="Instagram URL to validate")


class InstagramValidationResponse(BaseModel):
    isValid: bool = Field(..., description="Whether the URL is valid")
    message: str = Field(..., description="Validation message")
    postType: Optional[str] = Field(None, description="Type of Instagram post")


class InstagramEmbedRequest(BaseModel):
    url: HttpUrl = Field(..., description="Instagram URL to embed")
    maxWidth: Optional[int] = Field(None, ge=320, le=658, description="Maximum width for embed")


class InstagramEmbedResponse(BaseModel):
    embedCode: str = Field(..., description="Instagram oEmbed HTML code")
    width: int = Field(..., description="Embed width")
    height: int = Field(..., description="Embed height")
    thumbnailUrl: Optional[HttpUrl] = Field(None, description="Thumbnail URL")


class InstagramMetadataResponse(BaseModel):
    url: HttpUrl
    title: str
    description: str
    thumbnailUrl: Optional[HttpUrl] = None
    authorName: str
    authorUrl: HttpUrl
    embedCode: str
    width: int
    height: int


class AIExtractionRequest(BaseModel):
    instagramUrl: HttpUrl = Field(..., description="Instagram URL to analyze")
    extractIngredients: bool = Field(default=True, description="Extract ingredients")
    categorize: bool = Field(default=True, description="Auto-categorize recipe")
    extractInstructions: bool = Field(default=True, description="Extract cooking instructions")


class AIExtractionResponse(BaseModel):
    ingredients: List[str] = Field(default_factory=list, description="Extracted ingredients")
    category: Optional[RecipeCategory] = Field(None, description="Predicted category")
    cookingTime: Optional[int] = Field(None, description="Estimated cooking time in minutes")
    difficulty: Optional[RecipeDifficulty] = Field(None, description="Predicted difficulty")
    dietaryInfo: List[DietaryInfo] = Field(default_factory=list, description="Detected dietary info")
    tags: List[str] = Field(default_factory=list, description="Generated tags")
    instructions: Optional[str] = Field(None, description="Extracted instructions")
    confidence: float = Field(..., ge=0, le=1, description="AI confidence score")


class RecipeAIReprocessRequest(BaseModel):
    extractIngredients: bool = Field(default=True)
    categorize: bool = Field(default=True)
    extractInstructions: bool = Field(default=True)


class RecipeStatsResponse(BaseModel):
    totalRecipes: int = Field(..., ge=0)
    publicRecipes: int = Field(..., ge=0)
    categoriesCount: dict = Field(..., description="Count by category")
    averageCookingTime: float = Field(..., ge=0)
    topTags: List[dict] = Field(..., description="Most used tags with counts")