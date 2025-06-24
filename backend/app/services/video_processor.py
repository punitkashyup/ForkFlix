import asyncio
import cv2
import numpy as np
import tempfile
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import httpx
from urllib.parse import urlparse
import yt_dlp

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Advanced video processing for recipe extraction"""
    
    def __init__(self):
        self.client = None
    
    async def extract_frames_strategic(self, video_url: str, max_frames: int = 12) -> List[np.ndarray]:
        """
        Extract frames strategically based on cooking video patterns:
        - Ingredient preparation scenes (beginning 30% of video)  
        - Active cooking process (middle 50% of video)
        - Final dish presentation (final 20% of video)
        """
        try:
            # Download video temporarily
            video_path = await self._download_video_temp(video_url)
            if not video_path:
                return []
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error("Could not open video file")
                return []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video stats: {total_frames} frames, {fps} fps, {duration:.2f}s duration")
            
            # Calculate strategic frame positions
            frame_positions = self._calculate_strategic_positions(total_frames, max_frames)
            
            extracted_frames = []
            for frame_pos in frame_positions:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    extracted_frames.append(frame_rgb)
                    
                    logger.debug(f"Extracted frame at position {frame_pos}")
            
            cap.release()
            
            # Clean up temporary file
            try:
                os.unlink(video_path)
            except:
                pass
            
            logger.info(f"Successfully extracted {len(extracted_frames)} strategic frames")
            return extracted_frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []
    
    def _calculate_strategic_positions(self, total_frames: int, max_frames: int) -> List[int]:
        """Calculate frame positions based on cooking video structure"""
        if total_frames <= max_frames:
            return list(range(0, total_frames, max(1, total_frames // max_frames)))
        
        # Strategic sampling based on cooking video patterns
        positions = []
        
        # Ingredient prep phase (first 30% of video) - 30% of frames
        prep_frames = int(max_frames * 0.3)
        prep_end = int(total_frames * 0.3)
        prep_positions = np.linspace(0, prep_end, prep_frames, dtype=int)
        positions.extend(prep_positions)
        
        # Active cooking phase (middle 50% of video) - 50% of frames  
        cooking_frames = int(max_frames * 0.5)
        cooking_start = prep_end
        cooking_end = int(total_frames * 0.8)
        cooking_positions = np.linspace(cooking_start, cooking_end, cooking_frames, dtype=int)
        positions.extend(cooking_positions)
        
        # Final presentation phase (last 20% of video) - 20% of frames
        final_frames = max_frames - prep_frames - cooking_frames
        final_start = cooking_end
        final_positions = np.linspace(final_start, total_frames - 1, final_frames, dtype=int)
        positions.extend(final_positions)
        
        # Remove duplicates and sort
        positions = sorted(list(set(positions)))
        
        logger.info(f"Strategic frame positions: {positions[:5]}...{positions[-5:]} (showing first/last 5)")
        return positions
    
    def _extract_frames_from_file(self, video_path: str, max_frames: int = 12) -> List[np.ndarray]:
        """Extract frames directly from a video file"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video stats: {total_frames} frames, {fps} fps, {duration:.2f}s duration")
            
            # Calculate strategic frame positions
            frame_positions = self._calculate_strategic_positions(total_frames, max_frames)
            
            extracted_frames = []
            for frame_pos in frame_positions:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    extracted_frames.append(frame_rgb)
                    logger.debug(f"Extracted frame at position {frame_pos}")
            
            cap.release()
            logger.info(f"Successfully extracted {len(extracted_frames)} frames from file")
            return extracted_frames
            
        except Exception as e:
            logger.error(f"Frame extraction from file failed: {e}")
            return []
    
    async def _download_video_temp(self, video_url: str) -> Optional[str]:
        """Download video to temporary file using yt-dlp for Instagram support"""
        try:
            # Create unique temporary file for output
            import time
            timestamp = int(time.time() * 1000)
            output_path = f"/tmp/video_{timestamp}.mp4"
            
            logger.info(f"Attempting to download video from: {video_url}")
            
            # For Instagram URLs, use yt-dlp
            if 'instagram.com' in video_url:
                return await self._download_instagram_video_ytdlp(video_url, output_path)
            else:
                # For other URLs, use direct download
                return await self._download_video_direct(video_url, output_path)
                
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            return None
    
    async def _download_instagram_video_ytdlp(self, instagram_url: str, output_path: str) -> Optional[str]:
        """Download Instagram video using yt-dlp"""
        try:
            # Configure yt-dlp options for Instagram
            ydl_opts = {
                'outtmpl': output_path,
                'quiet': False,  # Enable output for debugging
                'no_warnings': False,
                'format': 'best[height<=720]/best',  # Get best quality up to 720p
                'noplaylist': True,
                'extract_flat': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'merge_output_format': 'mp4',  # Ensure mp4 output
                'overwrites': True,  # Overwrite existing files
                'force_overwrites': True,  # Force overwrite
            }
            
            logger.info(f"Starting yt-dlp download for Instagram URL: {instagram_url}")
            
            # Run yt-dlp in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            
            def download_sync():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([instagram_url])
            
            # Execute download in thread pool
            await loop.run_in_executor(None, download_sync)
            
            # Verify file exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Instagram video downloaded successfully: {output_path} ({file_size} bytes)")
                return output_path
            else:
                logger.error("❌ Downloaded file is empty or missing")
                # Clean up empty file
                if os.path.exists(output_path):
                    os.unlink(output_path)
                return None
                
        except Exception as e:
            logger.error(f"yt-dlp Instagram download failed: {e}")
            # Clean up failed download
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except:
                    pass
            return None
    
    async def _download_video_direct(self, video_url: str, output_path: str) -> Optional[str]:
        """Download video directly via HTTP for non-Instagram URLs"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=120.0)
            
            logger.info(f"Direct download from: {video_url}")
            
            response = await self.client.get(video_url)
            if response.status_code != 200:
                logger.error(f"Failed to download video: HTTP {response.status_code}")
                return None
            
            # Write content to file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Verify file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Direct video download successful: {output_path} ({file_size} bytes)")
                return output_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"Direct video download failed: {e}")
            return None
    
    async def detect_scene_changes(self, frames: List[np.ndarray], threshold: float = 0.3) -> List[int]:
        """Detect significant scene changes in video frames"""
        if len(frames) < 2:
            return []
        
        scene_changes = []
        prev_hist = self._calculate_histogram(frames[0])
        
        for i, frame in enumerate(frames[1:], 1):
            curr_hist = self._calculate_histogram(frame)
            
            # Calculate histogram correlation
            correlation = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)
            
            # If correlation is low, it's likely a scene change
            if correlation < (1 - threshold):
                scene_changes.append(i)
                logger.debug(f"Scene change detected at frame {i} (correlation: {correlation:.3f})")
            
            prev_hist = curr_hist
        
        return scene_changes
    
    def _calculate_histogram(self, frame: np.ndarray) -> np.ndarray:
        """Calculate color histogram for frame comparison"""
        # Convert to HSV for better color representation
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        # Calculate histogram
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
        
        # Normalize histogram
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        
        return hist
    
    async def extract_text_from_frames(self, frames: List[np.ndarray]) -> List[str]:
        """Extract text from video frames using OCR"""
        try:
            import easyocr
            
            reader = easyocr.Reader(['en'])
            extracted_texts = []
            
            for i, frame in enumerate(frames):
                try:
                    # Convert numpy array to format expected by easyocr
                    results = reader.readtext(frame)
                    
                    # Extract text with confidence > 0.5
                    frame_text = []
                    for (bbox, text, confidence) in results:
                        if confidence > 0.5:
                            frame_text.append(text.strip())
                    
                    if frame_text:
                        extracted_texts.append(' '.join(frame_text))
                        logger.debug(f"Frame {i} OCR: {frame_text}")
                
                except Exception as e:
                    logger.error(f"OCR failed for frame {i}: {e}")
                    continue
            
            return extracted_texts
            
        except ImportError:
            logger.warning("EasyOCR not available, skipping text extraction")
            return []
        except Exception as e:
            logger.error(f"Text extraction from frames failed: {e}")
            return []
    
    def analyze_frame_composition(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze frame composition for cooking-relevant features"""
        try:
            height, width = frame.shape[:2]
            
            # Detect dominant colors
            dominant_colors = self._get_dominant_colors(frame, k=3)
            
            # Analyze brightness and contrast
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Detect potential food regions (simplified)
            food_regions = self._detect_potential_food_regions(frame)
            
            return {
                'dimensions': (width, height),
                'dominant_colors': dominant_colors,
                'brightness': float(brightness),
                'contrast': float(contrast),
                'food_regions': len(food_regions),
                'aspect_ratio': width / height
            }
            
        except Exception as e:
            logger.error(f"Frame composition analysis failed: {e}")
            return {}
    
    def _get_dominant_colors(self, frame: np.ndarray, k: int = 3) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from frame"""
        try:
            # Reshape frame to be a list of pixels
            data = frame.reshape((-1, 3))
            data = np.float32(data)
            
            # Use k-means clustering to find dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to integers and return as tuples (JSON serializable)
            centers = np.uint8(centers)
            return [tuple(int(c) for c in color) for color in centers]
            
        except Exception as e:
            logger.error(f"Dominant color extraction failed: {e}")
            return []
    
    def _detect_potential_food_regions(self, frame: np.ndarray) -> List[Dict]:
        """Detect regions that might contain food (simplified implementation)"""
        try:
            # Convert to HSV for better color segmentation
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            
            # Define color ranges for common food colors
            food_color_ranges = [
                # Brown/beige (bread, meat)
                ([8, 50, 20], [25, 255, 200]),
                # Red/orange (tomatoes, peppers)
                ([0, 50, 50], [10, 255, 255]),
                # Green (vegetables)
                ([35, 50, 50], [85, 255, 255]),
                # Yellow (cheese, pasta)
                ([15, 50, 50], [35, 255, 255])
            ]
            
            food_regions = []
            
            for lower, upper in food_color_ranges:
                lower = np.array(lower)
                upper = np.array(upper)
                
                # Create mask for this color range
                mask = cv2.inRange(hsv, lower, upper)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Filter contours by area
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 1000:  # Minimum area threshold
                        x, y, w, h = cv2.boundingRect(contour)
                        food_regions.append({
                            'bbox': (int(x), int(y), int(w), int(h)),
                            'area': float(area),
                            'color_range': (lower.tolist(), upper.tolist())
                        })
            
            return food_regions
            
        except Exception as e:
            logger.error(f"Food region detection failed: {e}")
            return []
    
    async def process_instagram_video_for_recipe(self, instagram_url: str) -> Dict[str, Any]:
        """
        Complete video processing pipeline for Instagram recipe extraction
        
        Returns:
            Dict containing visual ingredients, OCR text, confidence, and metadata
        """
        try:
            logger.info(f"Starting complete Instagram video processing for: {instagram_url}")
            
            # Step 1: Download video using yt-dlp
            video_path = await self._download_video_temp(instagram_url)
            if not video_path:
                logger.error("Failed to download Instagram video")
                return self._create_empty_result("Video download failed")
            
            logger.info(f"Video downloaded successfully: {video_path}")
            
            # Step 2: Extract strategic frames directly from downloaded file
            frames = self._extract_frames_from_file(video_path, max_frames=12)
            if not frames:
                logger.error("Failed to extract frames from video")
                return self._create_empty_result("Frame extraction failed")
            
            logger.info(f"Extracted {len(frames)} frames for analysis")
            
            # Step 3: Analyze frames for ingredients using AI
            visual_ingredients = await self._detect_ingredients_in_frames(frames)
            
            # Step 4: Extract text from frames using OCR
            ocr_texts = await self.extract_text_from_frames(frames)
            combined_ocr_text = " ".join(ocr_texts) if ocr_texts else ""
            
            # Step 5: Analyze frame composition and cooking stages
            frame_analysis = []
            for i, frame in enumerate(frames):
                composition = self.analyze_frame_composition(frame)
                composition['frame_index'] = i
                frame_analysis.append(composition)
            
            # Step 6: Detect scene changes for cooking stages
            scene_changes = await self.detect_scene_changes(frames)
            
            # Step 7: Calculate confidence based on analysis results
            confidence = self._calculate_video_analysis_confidence(
                visual_ingredients, ocr_texts, frame_analysis, scene_changes
            )
            
            # Clean up temporary video file
            try:
                os.unlink(video_path)
                logger.info("Temporary video file cleaned up")
            except:
                pass
            
            result = {
                "visualIngredients": visual_ingredients,
                "ocrText": combined_ocr_text,
                "frameAnalysis": self._make_json_serializable(frame_analysis),
                "sceneChanges": scene_changes,
                "framesProcessed": len(frames),
                "confidence": float(confidence),
                "processingMethod": "yt-dlp + AI analysis",
                "success": True
            }
            
            logger.info(f"✅ Video processing completed successfully. Confidence: {confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Instagram video processing failed: {e}")
            return self._create_empty_result(f"Processing error: {str(e)}")
    
    async def _detect_ingredients_in_frames(self, frames: List[np.ndarray]) -> List[str]:
        """Detect ingredients in video frames using AI models"""
        try:
            import httpx
            from app.core.config import settings
            
            if not hasattr(settings, 'huggingface_api_key') or not settings.huggingface_api_key:
                logger.warning("Hugging Face API key not configured, using fallback ingredient detection")
                return self._fallback_ingredient_detection(frames)
            
            # Use object detection model for ingredient detection
            model_url = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"
            headers = {
                "Authorization": f"Bearer {settings.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            detected_ingredients = []
            
            # Process up to 3 key frames to avoid API limits
            key_frames = frames[::max(1, len(frames)//3)][:3]
            
            for i, frame in enumerate(key_frames):
                try:
                    # Convert frame to base64 for API
                    import cv2
                    import base64
                    
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send to object detection API
                    if not self.client:
                        self.client = httpx.AsyncClient(timeout=30.0)
                    
                    response = await self.client.post(
                        model_url,
                        headers=headers,
                        json={"inputs": frame_b64}
                    )
                    
                    if response.status_code == 200:
                        detections = response.json()
                        frame_ingredients = self._extract_food_items_from_detections(detections)
                        detected_ingredients.extend(frame_ingredients)
                        logger.info(f"Frame {i}: Detected {len(frame_ingredients)} potential ingredients")
                    
                except Exception as e:
                    logger.warning(f"AI detection failed for frame {i}: {e}")
                    continue
            
            # Remove duplicates and filter food items
            unique_ingredients = list(set(detected_ingredients))
            return unique_ingredients[:10]  # Limit to top 10
            
        except Exception as e:
            logger.error(f"AI ingredient detection failed: {e}")
            return self._fallback_ingredient_detection(frames)
    
    def _extract_food_items_from_detections(self, detections: List[Dict]) -> List[str]:
        """Extract food-related items from object detection results"""
        food_keywords = [
            'apple', 'banana', 'orange', 'carrot', 'broccoli', 'tomato', 'potato',
            'onion', 'garlic', 'pepper', 'mushroom', 'cheese', 'bread', 'egg',
            'chicken', 'beef', 'fish', 'pasta', 'rice', 'flour', 'milk', 'butter',
            'oil', 'salt', 'sugar', 'lemon', 'avocado', 'spinach', 'lettuce'
        ]
        
        food_items = []
        
        for detection in detections:
            if isinstance(detection, dict):
                label = detection.get('label', '').lower()
                score = detection.get('score', 0)
                
                # Only include high-confidence detections
                if score > 0.5:
                    # Check if label contains food keywords
                    for keyword in food_keywords:
                        if keyword in label and keyword not in food_items:
                            food_items.append(keyword)
        
        return food_items
    
    def _fallback_ingredient_detection(self, frames: List[np.ndarray]) -> List[str]:
        """Fallback ingredient detection using color and shape analysis"""
        try:
            # Simple color-based ingredient detection
            detected = []
            
            for frame in frames[:3]:  # Process first 3 frames
                # Detect common food colors
                hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
                
                # Red/orange foods (tomatoes, carrots, peppers)
                red_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
                orange_mask = cv2.inRange(hsv, np.array([10, 50, 50]), np.array([25, 255, 255]))
                
                # Green foods (vegetables, herbs)
                green_mask = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
                
                # Yellow foods (cheese, pasta, corn)
                yellow_mask = cv2.inRange(hsv, np.array([15, 50, 50]), np.array([35, 255, 255]))
                
                # Count pixels for each color category
                red_pixels = cv2.countNonZero(red_mask)
                orange_pixels = cv2.countNonZero(orange_mask)
                green_pixels = cv2.countNonZero(green_mask)
                yellow_pixels = cv2.countNonZero(yellow_mask)
                
                total_pixels = frame.shape[0] * frame.shape[1]
                
                # Add ingredients based on color presence (threshold: 5% of image)
                threshold = total_pixels * 0.05
                
                if red_pixels > threshold and 'tomato' not in detected:
                    detected.append('tomato')
                if orange_pixels > threshold and 'carrot' not in detected:
                    detected.append('carrot')
                if green_pixels > threshold and 'vegetables' not in detected:
                    detected.append('vegetables')
                if yellow_pixels > threshold and 'cheese' not in detected:
                    detected.append('cheese')
            
            return detected
            
        except Exception as e:
            logger.error(f"Fallback ingredient detection failed: {e}")
            return []
    
    def _calculate_video_analysis_confidence(
        self, 
        visual_ingredients: List[str], 
        ocr_texts: List[str], 
        frame_analysis: List[Dict], 
        scene_changes: List[int]
    ) -> float:
        """Calculate confidence score for video analysis results"""
        confidence = 0.3  # Base confidence for video processing
        
        # Boost for detected ingredients
        if visual_ingredients:
            confidence += min(len(visual_ingredients) * 0.05, 0.2)
        
        # Boost for OCR text extraction
        if ocr_texts and any(len(text) > 10 for text in ocr_texts):
            confidence += 0.15
        
        # Boost for frame analysis completeness
        if frame_analysis and len(frame_analysis) >= 3:
            confidence += 0.1
        
        # Boost for scene change detection (indicates cooking progression)
        if scene_changes and len(scene_changes) >= 2:
            confidence += 0.1
        
        # Boost for food-related colors detected
        food_color_frames = sum(1 for analysis in frame_analysis 
                               if analysis.get('food_regions', 0) > 0)
        if food_color_frames > 0:
            confidence += min(food_color_frames * 0.05, 0.15)
        
        return min(confidence, 0.85)  # Cap at 85% for video analysis
    
    def _make_json_serializable(self, obj):
        """Convert numpy types to JSON-serializable Python types"""
        import numpy as np
        
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
    
    def _create_empty_result(self, error_message: str) -> Dict[str, Any]:
        """Create empty result for failed processing"""
        return {
            "visualIngredients": [],
            "ocrText": "",
            "frameAnalysis": [],
            "sceneChanges": [],
            "framesProcessed": 0,
            "confidence": 0.1,
            "processingMethod": "failed",
            "success": False,
            "error": error_message
        }
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()


# Global instance
video_processor = VideoProcessor()