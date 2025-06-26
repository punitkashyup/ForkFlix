import asyncio
import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class InstagramServiceError(Exception):
    """Base exception for Instagram service errors"""
    pass


class InvalidUrlError(InstagramServiceError):
    """Raised when Instagram URL is invalid"""
    pass


class PrivateContentError(InstagramServiceError):
    """Raised when Instagram content is private"""
    pass


class ContentNotFoundError(InstagramServiceError):
    """Raised when Instagram content is not found"""
    pass


class RateLimitError(InstagramServiceError):
    """Raised when Instagram API rate limit is exceeded"""
    pass


class InstagramService:
    def __init__(self):
        self.client = None
    
    async def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate Instagram URL"""
        try:
            # Basic URL validation
            parsed = urlparse(url)
            
            # Check if it's an Instagram URL
            if 'instagram.com' not in parsed.netloc:
                return {
                    "isValid": False,
                    "message": "URL is not from Instagram",
                    "postType": None
                }
            
            # Check if it's a supported post type
            if '/p/' in parsed.path:
                post_type = "post"
            elif '/reel/' in parsed.path:
                post_type = "reel"
            elif '/tv/' in parsed.path:
                post_type = "tv"
            else:
                return {
                    "isValid": False,
                    "message": "URL is not a supported Instagram post type",
                    "postType": None
                }
            
            return {
                "isValid": True,
                "message": "Valid Instagram URL",
                "postType": post_type
            }
            
        except Exception as e:
            logger.error(f"Error validating Instagram URL: {e}")
            return {
                "isValid": False,
                "message": f"Error validating URL: {str(e)}",
                "postType": None
            }
    
    async def get_embed_code(self, url: str, max_width: Optional[int] = None) -> Dict[str, Any]:
        """Get Instagram embed code with thumbnail preview"""
        try:
            # Get metadata first to extract thumbnail
            metadata = await self._extract_metadata_from_page(url)
            thumbnail_url = metadata.get("thumbnailUrl")
            
            # Create a preview card with thumbnail and link to Instagram
            # Use proxy for Instagram images to avoid CORS issues
            from urllib.parse import quote
            from app.core.config import settings
            proxied_thumbnail = f"{settings.backend_url}/api/v1/proxy/instagram-image?url={quote(thumbnail_url)}" if thumbnail_url else None
            
            thumbnail_section = f'''<div style="position: relative; overflow: hidden; border-radius: 8px 8px 0 0;">
        <img src="{proxied_thumbnail}" alt="Instagram post preview" style="width: 100%; height: auto; display: block;" onerror="this.style.display='none'">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 60px; height: 60px; background: rgba(0, 0, 0, 0.7); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer;" onclick="window.open('{url}', '_blank')">
            <svg width="24" height="24" fill="white" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
            </svg>
        </div>
        <div style="position: absolute; top: 12px; right: 12px; background: rgba(0, 0, 0, 0.8); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">
            {"REEL" if "/reel/" in url else "VIDEO"}
        </div>
    </div>''' if proxied_thumbnail else ''
            
            embed_html = f'''<div class="instagram-preview-card" style="border: 1px solid #dbdbdb; border-radius: 8px; overflow: hidden; max-width: {max_width or 540}px; margin: 0 auto; background: white; position: relative;">
    {thumbnail_section}
    <div style="padding: 16px;">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <div style="width: 32px; height: 32px; background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                <svg width="18" height="18" fill="white" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
            </div>
            <div>
                <div style="font-weight: 600; font-size: 14px; color: #262626;">Instagram {("Reel" if "/reel/" in url else "Video")}</div>
                <div style="font-size: 12px; color: #8e8e8e;">{metadata.get('title', 'Instagram Post')[:50]}...</div>
            </div>
        </div>
        <a href="{url}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background: #0095f6; color: white; padding: 10px 16px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px; width: 100%; text-align: center; box-sizing: border-box; transition: background-color 0.2s;">
            ▶ Watch Full Video on Instagram
        </a>
    </div>
</div>'''
            
            return {
                "embedCode": embed_html,
                "width": max_width or 540,
                "height": 540,
                "thumbnailUrl": thumbnail_url
            }
            
        except Exception as e:
            logger.error(f"Error getting Instagram embed: {e}")
            raise InstagramServiceError(f"Failed to get embed code: {str(e)}")
    
    
    async def _extract_metadata_from_page(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Instagram page using BeautifulSoup approach"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=30.0)
            
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }
            
            # Ensure URL ends with / like in your working script
            if not url.endswith('/'):
                url = url + '/'
            
            response = await self.client.get(url, headers=headers, follow_redirects=True)
            if response.status_code != 200:
                logger.warning(f"Failed to load Instagram page: {response.status_code}")
                return {}
            
            # Parse HTML content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Open Graph metadata exactly like your working script
            thumbnail_tag = soup.find('meta', property='og:image')
            title_tag = soup.find('meta', property='og:title')
            description_tag = soup.find('meta', property='og:description')
            
            # Handle missing tags gracefully
            try:
                thumbnail_url = thumbnail_tag['content'] if thumbnail_tag else None
                title = title_tag['content'] if title_tag else None
                description = description_tag['content'] if description_tag else None
                
                # Log results for debugging
                if title and description:
                    logger.info(f"✅ Successfully extracted Instagram metadata")
                    logger.info(f"🔍 Recipe found in title: {'Golbari' in title}")
                else:
                    logger.warning(f"❌ Failed to extract complete Instagram metadata")
                    # Try fallback Twitter meta tags
                    if not thumbnail_tag:
                        thumbnail_tag = soup.find('meta', {'name': 'twitter:image'})
                        thumbnail_url = thumbnail_tag['content'] if thumbnail_tag else None
                    if not title_tag:
                        title_tag = soup.find('meta', {'name': 'twitter:title'})
                        title = title_tag['content'] if title_tag else None
                    if not description_tag:
                        description_tag = soup.find('meta', {'name': 'twitter:description'})
                        description = description_tag['content'] if description_tag else None
                
                return {
                    'thumbnailUrl': thumbnail_url,
                    'title': title,
                    'description': description
                }
            except (KeyError, TypeError) as e:
                logger.error(f"Error parsing meta tags: {e}")
                return {}
            
        except Exception as e:
            logger.error(f"Error extracting metadata from Instagram page: {e}")
            return {}
    
    async def _try_get_thumbnail(self, url: str) -> Optional[str]:
        """Try to get thumbnail URL from Instagram post"""
        try:
            metadata = await self._extract_metadata_from_page(url)
            return metadata.get('thumbnailUrl')
        except Exception as e:
            logger.debug(f"Could not extract thumbnail from {url}: {e}")
            return None
    
    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """Get Instagram post metadata using page scraping"""
        try:
            # Extract metadata from the page
            page_metadata = await self._extract_metadata_from_page(url)
            
            # Extract username from URL
            author_name = self._extract_username_from_url(url)
            
            # Get embed code
            embed_data = await self.get_embed_code(url)
            
            # Use extracted title and description if available, otherwise use defaults
            title = page_metadata.get('title') or f"Instagram Recipe from @{author_name}"
            description = page_metadata.get('description') or "A recipe shared on Instagram. Perfect for food lovers!"
            
            return {
                "url": url,
                "title": title,
                "description": description,
                "thumbnailUrl": page_metadata.get('thumbnailUrl'),
                "authorName": author_name,
                "authorUrl": f"https://www.instagram.com/{author_name}/",
                "embedCode": embed_data["embedCode"],
                "width": embed_data["width"],
                "height": embed_data["height"]
            }
            
        except Exception as e:
            logger.error(f"Error getting Instagram metadata: {e}")
            raise InstagramServiceError(f"Failed to get metadata: {str(e)}")
    
    def _extract_username_from_url(self, url: str) -> str:
        """Extract username from Instagram URL"""
        try:
            # Try to extract username from URL patterns
            import re
            # Pattern for URLs like https://www.instagram.com/username/p/postid/
            pattern = r'instagram\.com/([^/]+)/'
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            return "instagram_user"
        except:
            return "instagram_user"
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()


# Global instance
instagram_service = InstagramService()