from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/instagram-image")
async def proxy_instagram_image(url: str = Query(..., description="Instagram image URL to proxy")):
    """Proxy Instagram images to avoid CORS issues"""
    try:
        # Validate that this is an Instagram CDN URL
        if "scontent.cdninstagram.com" not in url:
            raise HTTPException(status_code=400, detail="Invalid Instagram image URL")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://www.instagram.com/'
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Image not found")
            
            # Return the image with proper headers
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg"),
                headers={
                    "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                    "Access-Control-Allow-Origin": "*"
                }
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error proxying Instagram image: {e}")
        raise HTTPException(status_code=500, detail="Failed to load image")