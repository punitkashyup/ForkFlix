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
        """Get Instagram embed code by scraping page metadata"""
        try:
            # Get metadata first to extract thumbnail
            metadata = await self._extract_metadata_from_page(url)
            
            # Generate embed code
            embed_html = f'''<blockquote class="instagram-media" data-instgrm-captioned data-instgrm-permalink="{url}" data-instgrm-version="14">
    <div style="padding:16px;">
        <a href="{url}" style="background:#FFFFFF; line-height:0; padding:0 0; text-align:center; text-decoration:none; width:100%;" target="_blank">
            <div style="display: flex; flex-direction: row; align-items: center;">
                <div style="background-color: #F4F4F4; border-radius: 50%; flex-grow: 0; height: 40px; margin-right: 14px; width: 40px;"></div>
                <div style="display: flex; flex-direction: column; flex-grow: 1; justify-content: center;">
                    <div style="background-color: #F4F4F4; border-radius: 4px; flex-grow: 0; height: 14px; margin-bottom: 6px; width: 100px;"></div>
                    <div style="background-color: #F4F4F4; border-radius: 4px; flex-grow: 0; height: 14px; width: 60px;"></div>
                </div>
            </div>
            <div style="padding: 19% 0;"></div>
            <div style="display:block; height:50px; margin:0 auto 12px; width:50px;">
                <svg width="50px" height="50px" viewBox="0 0 60 60" version="1.1" xmlns="https://www.w3.org/2000/svg">
                    <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                        <g transform="translate(-511.000000, -20.000000)" fill="#000000">
                            <g>
                                <path d="M556.869,30.41 C554.814,30.41 553.148,32.076 553.148,34.131 C553.148,36.186 554.814,37.852 556.869,37.852 C558.924,37.852 560.59,36.186 560.59,34.131 C560.59,32.076 558.924,30.41 556.869,30.41 M541,60.657 C535.114,60.657 530.342,55.887 530.342,50 C530.342,44.114 535.114,39.342 541,39.342 C546.887,39.342 551.658,44.114 551.658,50 C551.658,55.887 546.887,60.657 541,60.657 M541,33.886 C532.1,33.886 524.886,41.1 524.886,50 C524.886,58.899 532.1,66.113 541,66.113 C549.9,66.113 557.115,58.899 557.115,50 C557.115,41.1 549.9,33.886 541,33.886 M565.378,62.101 C565.244,65.022 564.756,66.606 564.346,67.663 C563.803,69.06 563.154,70.057 562.106,71.106 C561.058,72.155 560.06,72.803 558.662,73.347 C557.607,73.757 556.021,74.244 553.102,74.378 C549.944,74.521 548.997,74.552 541,74.552 C533.003,74.552 532.056,74.521 528.898,74.378 C525.979,74.244 524.393,73.757 523.338,73.347 C521.94,72.803 520.942,72.155 519.894,71.106 C518.846,70.057 518.197,69.06 517.654,67.663 C517.244,66.606 516.755,65.022 516.623,62.101 C516.479,58.943 516.448,57.996 516.448,50 C516.448,42.003 516.479,41.056 516.623,37.899 C516.755,34.978 517.244,33.391 517.654,32.338 C518.197,30.938 518.846,29.942 519.894,28.894 C520.942,27.846 521.94,27.196 523.338,26.654 C524.393,26.244 525.979,25.756 528.898,25.623 C532.057,25.479 533.004,25.448 541,25.448 C548.997,25.448 549.943,25.479 553.102,25.623 C556.021,25.756 557.607,26.244 558.662,26.654 C560.06,27.196 561.058,27.846 562.106,28.894 C563.154,29.942 563.803,30.938 564.346,32.338 C564.756,33.391 565.244,34.978 565.378,37.899 C565.522,41.056 565.552,42.003 565.552,50 C565.552,57.996 565.522,58.943 565.378,62.101 M570.82,37.631 C570.674,34.438 570.167,32.258 569.425,30.349 C568.659,28.377 567.633,26.702 565.965,25.035 C564.297,23.368 562.623,22.342 560.652,21.575 C558.743,20.834 556.562,20.326 553.369,20.18 C550.169,20.033 549.148,20 541,20 C532.853,20 531.831,20.033 528.631,20.18 C525.438,20.326 523.257,20.834 521.349,21.575 C519.376,22.342 517.703,23.368 516.035,25.035 C514.368,26.702 513.342,28.377 512.574,30.349 C511.834,32.258 511.326,34.438 511.181,37.631 C511.035,40.831 511,41.851 511,50 C511,58.147 511.035,59.17 511.181,62.369 C511.326,65.562 511.834,67.743 512.574,69.651 C513.342,71.625 514.368,73.296 516.035,74.965 C517.703,76.634 519.376,77.658 521.349,78.425 C523.257,79.167 525.438,79.673 528.631,79.82 C531.831,79.965 532.853,80.001 541,80.001 C549.148,80.001 550.169,79.965 553.369,79.82 C556.562,79.673 558.743,79.167 560.652,78.425 C562.623,77.658 564.297,76.634 565.965,74.965 C567.633,73.296 568.659,71.625 569.425,69.651 C570.167,67.743 570.674,65.562 570.82,62.369 C570.966,59.17 571,58.147 571,50 C571,41.851 570.966,40.831 570.82,37.631"></path>
                            </g>
                        </g>
                    </g>
                </svg>
            </div>
            <div style="padding-top: 8px;">
                <div style="color:#3897f0; font-family:Arial,sans-serif; font-size:14px; font-style:normal; font-weight:550; line-height:18px;">View this post on Instagram</div>
            </div>
        </a>
    </div>
</blockquote>
<script async src="//www.instagram.com/embed.js"></script>'''
            
            return {
                "embedCode": embed_html,
                "width": max_width or 540,
                "height": 540,
                "thumbnailUrl": metadata.get("thumbnailUrl")
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
            
            response = await self.client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Failed to load Instagram page: {response.status_code}")
                return {}
            
            # Parse HTML content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Open Graph metadata
            thumbnail_tag = soup.find('meta', property='og:image')
            title_tag = soup.find('meta', property='og:title')
            description_tag = soup.find('meta', property='og:description')
            
            # Also try Twitter card metadata as fallback
            if not thumbnail_tag:
                thumbnail_tag = soup.find('meta', {'name': 'twitter:image'})
            if not title_tag:
                title_tag = soup.find('meta', {'name': 'twitter:title'})
            if not description_tag:
                description_tag = soup.find('meta', {'name': 'twitter:description'})
            
            return {
                'thumbnailUrl': thumbnail_tag.get('content') if thumbnail_tag else None,
                'title': title_tag.get('content') if title_tag else None,
                'description': description_tag.get('content') if description_tag else None
            }
            
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