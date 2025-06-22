from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Operation success status")
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ValidationErrorResponse(BaseModel):
    success: bool = Field(default=False)
    error: str = Field(default="Validation Error")
    details: List[Dict[str, Any]] = Field(..., description="Validation error details")


class NotFoundResponse(BaseModel):
    success: bool = Field(default=False)
    error: str = Field(default="Resource not found")
    message: str = Field(..., description="Not found message")


class UnauthorizedResponse(BaseModel):
    success: bool = Field(default=False)
    error: str = Field(default="Unauthorized")
    message: str = Field(default="Authentication required")


class ForbiddenResponse(BaseModel):
    success: bool = Field(default=False)
    error: str = Field(default="Forbidden")
    message: str = Field(default="Insufficient permissions")


class RateLimitResponse(BaseModel):
    success: bool = Field(default=False)
    error: str = Field(default="Rate Limit Exceeded")
    message: str = Field(default="Too many requests")
    retryAfter: Optional[int] = Field(None, description="Seconds to wait before retry")


class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy", description="Service health status")
    timestamp: str = Field(..., description="ISO timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (dev/prod)")
    services: Dict[str, str] = Field(..., description="External service status")


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=1, description="Total number of pages")
    hasNext: bool = Field(..., description="Has next page")
    hasPrev: bool = Field(..., description="Has previous page")


class PaginatedResponse(BaseModel):
    items: List[Any] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class BulkOperationResponse(BaseModel):
    success: bool = Field(default=True)
    processed: int = Field(..., ge=0, description="Number of items processed")
    successful: int = Field(..., ge=0, description="Number of successful operations")
    failed: int = Field(..., ge=0, description="Number of failed operations")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of errors")


class UploadResponse(BaseModel):
    success: bool = Field(default=True)
    url: str = Field(..., description="Uploaded file URL")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., ge=0, description="File size in bytes")
    contentType: str = Field(..., description="MIME content type")