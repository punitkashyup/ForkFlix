from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from app.core.security import get_current_user
from app.schemas.recipe import (
    InstagramValidationRequest,
    InstagramValidationResponse,
    InstagramEmbedRequest,
    InstagramEmbedResponse,
    InstagramMetadataResponse
)
from app.services.instagram_service import (
    instagram_service,
    InstagramServiceError,
    InvalidUrlError,
    PrivateContentError,
    ContentNotFoundError,
    RateLimitError
)
import logging
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/validate", response_model=InstagramValidationResponse)
async def validate_instagram_url(
    request: InstagramValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate Instagram URL format and accessibility
    
    This endpoint checks if an Instagram URL is:
    - Properly formatted
    - Accessible (not private/deleted)
    - Contains supported content type (post/reel/tv)
    
    Returns detailed validation information including post type.
    """
    try:
        logger.info(f"Validating Instagram URL: {request.url}")
        
        # Use the Instagram service to validate the URL
        validation_result = await instagram_service.validate_url(str(request.url))
        
        return validation_result
        
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for URL validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except (InvalidUrlError, PrivateContentError, ContentNotFoundError) as e:
        logger.info(f"URL validation failed: {str(e)}")
        # Return validation response with error details
        return InstagramValidationResponse(
            isValid=False,
            message=str(e),
            postType=None
        )
    except InstagramServiceError as e:
        logger.error(f"Instagram service error during validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Instagram service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error validating Instagram URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate Instagram URL"
        )


@router.post("/embed", response_model=InstagramEmbedResponse)
async def get_instagram_embed(
    request: InstagramEmbedRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get Instagram embed code using oEmbed API
    
    This endpoint fetches the official Instagram embed code using
    Instagram's oEmbed API. The embed code can be directly used
    in web pages to display the Instagram content.
    
    Supports optional maxWidth parameter to control embed size.
    """
    try:
        logger.info(f"Getting Instagram embed for URL: {request.url}")
        
        # Get embed code using Instagram service
        embed_response = await instagram_service.get_embed_code(
            url=str(request.url),
            max_width=request.maxWidth
        )
        
        logger.info(f"Successfully retrieved embed code for URL: {request.url}")
        return embed_response
        
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for embed request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except InvalidUrlError as e:
        logger.info(f"Invalid URL for embed request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PrivateContentError as e:
        logger.info(f"Private content for embed request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ContentNotFoundError as e:
        logger.info(f"Content not found for embed request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InstagramServiceError as e:
        logger.error(f"Instagram service error during embed request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Instagram service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting Instagram embed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Instagram embed code"
        )


@router.get("/metadata/{url:path}", response_model=InstagramMetadataResponse)
async def get_instagram_metadata(
    url: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive Instagram metadata
    
    This endpoint retrieves detailed metadata for an Instagram post including:
    - Title and description
    - Author information
    - Thumbnail URL
    - Embed code
    - Dimensions
    
    The metadata is fetched using Instagram's oEmbed API and processed
    to provide structured information useful for recipe creation.
    """
    try:
        logger.info(f"Getting Instagram metadata for URL: {url}")
        
        # Ensure URL is properly formatted
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Get metadata using Instagram service
        metadata_response = await instagram_service.get_metadata(url)
        
        logger.info(f"Successfully retrieved metadata for URL: {url}")
        return metadata_response
        
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for metadata request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except InvalidUrlError as e:
        logger.info(f"Invalid URL for metadata request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PrivateContentError as e:
        logger.info(f"Private content for metadata request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ContentNotFoundError as e:
        logger.info(f"Content not found for metadata request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InstagramServiceError as e:
        logger.error(f"Instagram service error during metadata request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Instagram service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting Instagram metadata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Instagram metadata"
        )


@router.get("/health")
async def instagram_service_health():
    """
    Check Instagram service health
    
    This endpoint provides a simple health check for the Instagram
    integration service. It can be used to monitor service availability
    and diagnose potential issues.
    """
    try:
        # Simple health check - just return service status
        return {
            "service": "Instagram API Integration",
            "status": "healthy",
            "features": [
                "URL validation",
                "oEmbed integration", 
                "Metadata extraction",
                "Rate limiting",
                "Error handling"
            ],
            "supported_content_types": [
                "Instagram posts (/p/)",
                "Instagram reels (/reel/)",
                "Instagram TV (/tv/)"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Instagram service health check failed"
        )


@router.get("/url-info")
async def get_url_info(
    url: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get basic URL information without full metadata
    
    This endpoint provides quick URL analysis including:
    - URL format validation
    - Post type detection
    - Basic accessibility check
    
    Useful for preliminary URL validation before processing.
    """
    try:
        logger.info(f"Getting URL info for: {url}")
        
        # Validate and get basic info
        validation = await instagram_service.validate_url(url)
        
        return {
            "url": url,
            "isValid": validation["isValid"],
            "postType": validation["postType"],
            "message": validation["message"],
            "canProcess": validation["isValid"] and validation["postType"] in ['post', 'reel', 'tv']
        }
        
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for URL info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting URL info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get URL information"
        )


@router.post("/bulk-validate")
async def bulk_validate_urls(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate multiple Instagram URLs in bulk
    
    This endpoint allows validation of multiple URLs at once,
    useful for batch processing or import functionality.
    
    Request format:
    {
        "urls": ["url1", "url2", "url3", ...]
    }
    
    Returns validation results for each URL.
    """
    try:
        urls = request.get("urls", [])
        
        if not urls or len(urls) > 10:  # Limit to 10 URLs per request
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide 1-10 URLs for validation"
            )
        
        logger.info(f"Bulk validating {len(urls)} URLs")
        
        results = []
        
        for url in urls:
            try:
                validation = await instagram_service.validate_url(url)
                results.append({
                    "url": url,
                    "isValid": validation["isValid"],
                    "postType": validation["postType"],
                    "message": validation["message"],
                    "error": None
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "isValid": False,
                    "postType": None,
                    "message": f"Validation failed: {str(e)}",
                    "error": str(e)
                })
        
        # Count results
        valid_count = sum(1 for r in results if r["isValid"])
        
        return {
            "totalUrls": len(urls),
            "validUrls": valid_count,
            "invalidUrls": len(urls) - valid_count,
            "results": results
        }
        
    except HTTPException:
        raise
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for bulk validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in bulk URL validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate URLs"
        )


@router.get("/rate-limit-status")
async def get_rate_limit_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current rate limit status
    
    This endpoint provides information about the current
    rate limiting status for Instagram API calls.
    """
    try:
        # Access the rate limiting information from the service
        # This is a simplified implementation - you might want to
        # track more detailed rate limiting information
        
        return {
            "service": "Instagram API",
            "rateLimitInfo": {
                "requestsPerMinute": 30,  # Based on typical Instagram oEmbed limits
                "currentUsage": "Available",  # Simplified status
                "resetTime": None,
                "remainingRequests": None
            },
            "recommendations": [
                "Space out requests when processing multiple URLs",
                "Use bulk validation for multiple URLs",
                "Cache results when possible to reduce API calls"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit status"
        )


@router.post("/test-connection")
async def test_instagram_connection(
    current_user: dict = Depends(get_current_user)
):
    """
    Test Instagram API connection
    
    This endpoint tests the connection to Instagram's oEmbed API
    using a known public post. Useful for debugging connectivity issues.
    """
    try:
        logger.info("Testing Instagram API connection")
        
        # Use a known public Instagram post for testing
        # This should be a stable, public post that won't be deleted
        test_url = "https://www.instagram.com/p/CUdh8EyLLEt/"  # Example public post
        
        try:
            validation = await instagram_service.validate_url(test_url)
            
            connection_test = {
                "connectionStatus": "successful" if validation["isValid"] else "failed",
                "testUrl": test_url,
                "validationResult": {
                    "isValid": validation["isValid"],
                    "postType": validation["postType"],
                    "message": validation["message"]
                },
                "timestamp": logger.info(f"Instagram connection test completed"),
                "recommendations": []
            }
            
            if not validation["isValid"]:
                connection_test["recommendations"].append(
                    "Check internet connectivity and Instagram service status"
                )
            
            return connection_test
            
        except RateLimitError as e:
            return {
                "connectionStatus": "rate_limited",
                "testUrl": test_url,
                "error": str(e),
                "recommendations": [
                    "Wait before retrying",
                    "Check rate limiting configuration"
                ]
            }
        except Exception as e:
            return {
                "connectionStatus": "error",
                "testUrl": test_url,
                "error": str(e),
                "recommendations": [
                    "Check Instagram service status",
                    "Verify network connectivity",
                    "Check service configuration"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error testing Instagram connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test Instagram connection"
        )