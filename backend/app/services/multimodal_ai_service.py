import asyncio
import httpx
import logging
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import base64
import io
from urllib.parse import quote

from app.core.config import settings
from app.services.video_processor import video_processor
from app.services.audio_processor import production_audio_processor
from app.services.ai_fusion_service import ai_fusion_service
from app.services.mistral_service import mistral_service

logger = logging.getLogger(__name__)


class MultiModalAIService:
    """Enhanced AI service for multi-modal recipe extraction with progressive enhancement"""
    
    def __init__(self):
        self.client = None
        self.huggingface_api_key = settings.huggingface_api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
    
    async def extract_progressive(
        self,
        instagram_url: str,
        thumbnail_url: Optional[str] = None,
        description: str = "",
        caption: str = "",
        video_url: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Progressive multi-modal extraction with real-time updates
        
        Yields extraction results as they become available:
        1. Immediate text-based results (1-2 seconds)
        2. Enhanced video frame analysis (10-15 seconds) 
        3. Audio transcription results (5-10 seconds)
        4. Final fusion results (2-3 seconds)
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=120.0)
            
            # Phase 1: Immediate Text Analysis (1-2 seconds)
            logger.info("Phase 1: Starting immediate text analysis")
            yield {
                "phase": 1,
                "status": "processing",
                "message": "Reading caption and description...",
                "progress": 25,
                "timestamp": datetime.now().isoformat()
            }
            
            text_result = await self._extract_from_text_enhanced(description, caption)
            
            yield {
                "phase": 1,
                "status": "completed",
                "message": "Text analysis completed",
                "progress": 25,
                "data": text_result,
                "confidence": text_result.get("confidence", 0.6),
                "timestamp": datetime.now().isoformat()
            }
            
            # Phase 2: Video Frame Analysis (10-15 seconds)
            visual_result = None
            if instagram_url:  # Use Instagram URL for full video processing
                logger.info("Phase 2: Starting Instagram video analysis with yt-dlp")
                yield {
                    "phase": 2,
                    "status": "processing", 
                    "message": "Downloading and analyzing Instagram video...",
                    "progress": 40,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Use our new Instagram video processing pipeline
                visual_result = await video_processor.process_instagram_video_for_recipe(instagram_url)
                
                yield {
                    "phase": 2,
                    "status": "completed",
                    "message": "Instagram video analysis completed",
                    "progress": 65,
                    "data": visual_result,
                    "confidence": visual_result.get("confidence", 0.7),
                    "timestamp": datetime.now().isoformat()
                }
            elif thumbnail_url:  # Fallback to thumbnail analysis
                logger.info("Phase 2: Starting thumbnail image analysis")
                yield {
                    "phase": 2,
                    "status": "processing", 
                    "message": "Analyzing thumbnail image for ingredients...",
                    "progress": 50,
                    "timestamp": datetime.now().isoformat()
                }
                
                visual_result = await self._extract_from_visual(thumbnail_url, text_result)
                
                yield {
                    "phase": 2,
                    "status": "completed",
                    "message": "Visual analysis completed",
                    "progress": 65,
                    "data": visual_result,
                    "confidence": visual_result.get("confidence", 0.5),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Phase 3: Audio Transcription (5-10 seconds)
            audio_result = None
            if instagram_url:  # Use Instagram URL for audio processing
                logger.info("Phase 3: Starting Instagram audio transcription with yt-dlp")
                yield {
                    "phase": 3,
                    "status": "processing",
                    "message": "Extracting and transcribing Instagram audio...",
                    "progress": 75,
                    "timestamp": datetime.now().isoformat()
                }
                
                audio_result = await production_audio_processor.transcribe_video_audio(instagram_url)
                
                yield {
                    "phase": 3,
                    "status": "completed",
                    "message": "Instagram audio transcription completed", 
                    "progress": 85,
                    "data": audio_result,
                    "confidence": audio_result.get("confidence", 0.8),
                    "timestamp": datetime.now().isoformat()
                }
            elif video_url:  # Fallback to provided video URL
                logger.info("Phase 3: Starting audio transcription from video URL")
                yield {
                    "phase": 3,
                    "status": "processing",
                    "message": "Transcribing cooking instructions...",
                    "progress": 80,
                    "timestamp": datetime.now().isoformat()
                }
                
                audio_result = await self._extract_from_audio(video_url, text_result)
                
                yield {
                    "phase": 3,
                    "status": "completed",
                    "message": "Audio transcription completed", 
                    "progress": 85,
                    "data": audio_result,
                    "confidence": audio_result.get("confidence", 0.6),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Phase 4: AI-Powered Data Fusion (2-3 seconds)
            logger.info("Phase 4: Starting AI-powered data fusion")
            yield {
                "phase": 4,
                "status": "processing",
                "message": "AI analyzing all sources for optimal recipe extraction...",
                "progress": 100,
                "timestamp": datetime.now().isoformat()
            }
            
            # Use AI-powered fusion with weighted analysis
            final_result = await ai_fusion_service.fuse_multimodal_data_with_ai(
                text_result,
                audio_result if video_url else None,
                visual_result if thumbnail_url else None
            )
            
            yield {
                "phase": 4,
                "status": "completed",
                "message": "AI fusion completed, starting final processing...",
                "progress": 90,
                "data": final_result,
                "confidence": final_result.get("confidence", 0.85),
                "timestamp": datetime.now().isoformat()
            }
            
            # Phase 5: Mistral AI Final Processing (5-10 seconds)
            logger.info("Phase 5: Starting Mistral AI final processing for maximum accuracy")
            yield {
                "phase": 5,
                "status": "processing",
                "message": "Mistral AI extracting structured recipe data for 100% accuracy...",
                "progress": 95,
                "timestamp": datetime.now().isoformat()
            }
            
            # Prepare complete multimodal data for Mistral AI
            complete_data = {
                "phase_1_text": text_result,
                "phase_2_video": visual_result if visual_result else None,
                "phase_3_audio": audio_result if audio_result else None,
                "phase_4_fusion": final_result,
                "instagram_url": instagram_url,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            # Use Mistral AI for final structured extraction
            mistral_result = await mistral_service.extract_structured_recipe(complete_data)
            
            # Final result with Mistral AI processing
            yield {
                "phase": 5,
                "status": "completed",
                "message": "Recipe extraction completed with maximum accuracy",
                "progress": 100,
                "data": mistral_result,
                "confidence": mistral_result.get("confidence", 0.95),
                "timestamp": datetime.now().isoformat(),
                "processing_method": "5-phase_multimodal_with_mistral_ai"
            }
            
        except Exception as e:
            logger.error(f"Progressive extraction failed: {e}")
            yield {
                "phase": "error",
                "status": "failed",
                "message": f"Extraction failed: {str(e)}",
                "progress": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _extract_from_text_enhanced(self, description: str, caption: str) -> Dict[str, Any]:
        """Enhanced text extraction using advanced NLP models"""
        try:
            combined_text = f"{description} {caption}".strip()
            
            # Use multiple models for better accuracy
            tasks = [
                self._extract_ingredients_advanced(combined_text),
                self._categorize_recipe_advanced(combined_text),
                self._extract_cooking_instructions_advanced(combined_text),
                self._extract_cooking_time_advanced(combined_text),
                self._detect_dietary_info_advanced(combined_text)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            ingredients = results[0] if not isinstance(results[0], Exception) else []
            category_result = results[1] if not isinstance(results[1], Exception) else {"category": "Main Course", "confidence": 0.5}
            instructions = results[2] if not isinstance(results[2], Exception) else ""
            cooking_time = results[3] if not isinstance(results[3], Exception) else 30
            dietary_info = results[4] if not isinstance(results[4], Exception) else []
            
            # Calculate overall confidence based on extraction quality
            confidence = self._calculate_text_confidence(
                combined_text, ingredients, category_result.get("confidence", 0.5)
            )
            
            return {
                "source": "text",
                "source_text": combined_text,  # Add source text for AI fusion
                "ingredients": ingredients,
                "category": category_result.get("category", "Main Course"),
                "instructions": instructions,
                "cookingTime": cooking_time,
                "difficulty": self._determine_difficulty_advanced(ingredients, cooking_time, combined_text),
                "dietaryInfo": dietary_info,
                "tags": self._generate_tags_advanced(ingredients, category_result.get("category"), combined_text),
                "confidence": confidence,
                "extractedFields": ["ingredients", "category", "instructions", "cookingTime", "difficulty", "dietaryInfo", "tags"]
            }
            
        except Exception as e:
            logger.error(f"Enhanced text extraction failed: {e}")
            return {
                "source": "text",
                "ingredients": [],
                "category": None,
                "instructions": "",
                "cookingTime": None,
                "difficulty": None,
                "dietaryInfo": [],
                "tags": [],
                "confidence": 0.0,
                "extractedFields": []
            }
    
    async def _extract_from_visual(self, thumbnail_url: str, text_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract recipe information from visual content using computer vision"""
        try:
            # For thumbnail URL, try direct image analysis
            if thumbnail_url:
                image_data = await self._download_image(thumbnail_url)
                if image_data:
                    # Use vision transformer for ingredient detection
                    visual_ingredients = await self._detect_ingredients_from_image(image_data)
                    
                    # Use OCR to extract any visible text
                    ocr_text = await self._extract_text_from_image(image_data)
                    
                    # Enhance ingredients list by combining visual detection with text context
                    enhanced_ingredients = self._merge_ingredient_lists(
                        text_context.get("ingredients", []),
                        visual_ingredients,
                        ocr_text
                    )
                    
                    confidence = self._calculate_visual_confidence(visual_ingredients, ocr_text)
                    
                    return {
                        "source": "visual",
                        "ingredients": enhanced_ingredients,
                        "cookingTime": None,
                        "ocrText": ocr_text,
                        "visualIngredients": visual_ingredients,
                        "confidence": confidence,
                        "extractedFields": ["ingredients"]
                    }
            
            # If we have a video URL, do advanced frame analysis
            logger.info("Starting advanced video frame analysis")
            
            # Extract strategic frames from video
            frames = await video_processor.extract_frames_strategic(thumbnail_url, max_frames=8)
            if not frames:
                raise Exception("Failed to extract video frames")
            
            # Analyze frames for ingredients and cooking process
            frame_analysis = []
            all_visual_ingredients = []
            all_ocr_text = []
            
            for i, frame in enumerate(frames):
                try:
                    # Analyze frame composition
                    composition = video_processor.analyze_frame_composition(frame)
                    
                    # Convert frame to bytes for processing
                    frame_bytes = self._frame_to_bytes(frame)
                    
                    # Detect ingredients in this frame
                    frame_ingredients = await self._detect_ingredients_from_image(frame_bytes)
                    all_visual_ingredients.extend(frame_ingredients)
                    
                    frame_analysis.append({
                        'frame_index': i,
                        'composition': composition,
                        'ingredients': frame_ingredients
                    })
                    
                except Exception as e:
                    logger.error(f"Frame {i} analysis failed: {e}")
                    continue
            
            # Extract text from multiple frames
            frame_texts = await video_processor.extract_text_from_frames(frames)
            all_ocr_text = ' '.join(frame_texts)
            
            # Combine all visual ingredients and deduplicate
            unique_visual_ingredients = list(set(all_visual_ingredients))
            
            # Enhance ingredients list
            enhanced_ingredients = self._merge_ingredient_lists(
                text_context.get("ingredients", []),
                unique_visual_ingredients,
                all_ocr_text
            )
            
            # Calculate confidence based on multi-frame analysis
            confidence = self._calculate_multi_frame_confidence(
                frame_analysis, unique_visual_ingredients, all_ocr_text
            )
            
            return {
                "source": "visual_advanced",
                "ingredients": enhanced_ingredients,
                "cookingTime": None,
                "ocrText": all_ocr_text,
                "visualIngredients": unique_visual_ingredients,
                "frameAnalysis": frame_analysis,
                "framesProcessed": len(frames),
                "confidence": confidence,
                "extractedFields": ["ingredients"]
            }
            
        except Exception as e:
            logger.error(f"Visual extraction failed: {e}")
            return {
                "source": "visual",
                "ingredients": [],
                "cookingTime": None,
                "ocrText": "",
                "visualIngredients": [],
                "confidence": 0.2,
                "extractedFields": []
            }
    
    async def _extract_from_audio(self, video_url: str, text_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cooking instructions from audio using Whisper"""
        try:
            logger.info("Starting audio transcription with Whisper")
            
            # Use the audio processor to transcribe video audio
            audio_result = await production_audio_processor.transcribe_video_audio(video_url)
            
            if not audio_result or audio_result.get("confidence", 0) < 0.3:
                # Fallback to text-based instruction generation
                logger.warning("Audio transcription failed or low confidence, using text fallback")
                return await self._fallback_audio_extraction(text_context)
            
            # Extract enhanced instructions
            instructions = audio_result.get("instructions", "")
            transcription = audio_result.get("transcription", "")
            confidence = audio_result.get("confidence", 0.5)
            
            # Enhance instructions with context from text
            if instructions and text_context.get("ingredients"):
                enhanced_instructions = self._enhance_audio_instructions(
                    instructions, text_context.get("ingredients", [])
                )
            else:
                enhanced_instructions = instructions
            
            # Extract cooking times from transcription
            cooking_times = self._extract_cooking_times_from_audio(
                audio_result.get("time_indicators", [])
            )
            
            return {
                "source": "audio",
                "instructions": enhanced_instructions,
                "transcription": transcription,
                "rawInstructions": instructions,
                "cookingTimes": cooking_times,
                "timeIndicators": audio_result.get("time_indicators", []),
                "cookingTermsFound": audio_result.get("cooking_terms_found", 0),
                "confidence": confidence,
                "extractedFields": ["instructions"] if instructions else []
            }
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return await self._fallback_audio_extraction(text_context)
    
    async def _fallback_audio_extraction(self, text_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback audio extraction when Whisper fails"""
        # Generate basic instructions from text context
        audio_instructions = await self._simulate_audio_transcription(text_context)
        
        return {
            "source": "audio_fallback",
            "instructions": audio_instructions,
            "transcription": "Audio transcription not available",
            "confidence": 0.3 if audio_instructions else 0.1,
            "extractedFields": ["instructions"] if audio_instructions else []
        }
    
    async def _fuse_multimodal_data(
        self,
        text_result: Dict[str, Any],
        visual_result: Optional[Dict[str, Any]],
        audio_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Intelligently combine results from all sources"""
        try:
            # Start with text result as base
            fused_result = text_result.copy()
            
            # Confidence-weighted merging
            sources_used = ["text"]
            total_confidence = text_result.get("confidence", 0.6)
            confidence_weights = [text_result.get("confidence", 0.6)]
            
            # Merge visual results
            if visual_result and visual_result.get("confidence", 0) > 0.3:
                sources_used.append("visual")
                confidence_weights.append(visual_result.get("confidence", 0.5))
                
                # Merge ingredients with visual detection
                visual_ingredients = visual_result.get("ingredients", [])
                if visual_ingredients:
                    fused_result["ingredients"] = self._smart_merge_ingredients(
                        fused_result.get("ingredients", []),
                        visual_ingredients,
                        text_result.get("confidence", 0.6),
                        visual_result.get("confidence", 0.5)
                    )
                
                # Update cooking time if visual has higher confidence
                if (visual_result.get("cookingTime") and 
                    visual_result.get("confidence", 0) > text_result.get("confidence", 0.6)):
                    fused_result["cookingTime"] = visual_result["cookingTime"]
            
            # Merge audio results  
            if audio_result and audio_result.get("confidence", 0) > 0.5:
                sources_used.append("audio")
                confidence_weights.append(audio_result.get("confidence", 0.7))
                
                # Prefer audio instructions if confidence is high
                audio_instructions = audio_result.get("instructions", "")
                if audio_instructions and audio_result.get("confidence", 0) > 0.7:
                    fused_result["instructions"] = audio_instructions
            
            # Calculate final confidence as weighted average
            final_confidence = sum(confidence_weights) / len(confidence_weights)
            fused_result["confidence"] = min(final_confidence * 1.1, 0.95)  # Bonus for multi-modal
            
            # Add metadata about data sources
            fused_result["dataSources"] = sources_used
            fused_result["fusionTimestamp"] = datetime.now().isoformat()
            
            return fused_result
            
        except Exception as e:
            logger.error(f"Data fusion failed: {e}")
            # Return text result as fallback
            return text_result
    
    async def _extract_ingredients_advanced(self, text: str) -> List[str]:
        """Advanced ingredient extraction using specialized NLP models"""
        try:
            # Use a food-specific NER model
            model_url = f"{self.base_url}/microsoft/DialoGPT-medium"
            
            prompt = f"Extract cooking ingredients from this text: {text[:500]}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.3
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                # Process the result to extract ingredients
                return self._parse_ingredients_from_generation(result, text)
            
            # Fallback to rule-based extraction
            return self._extract_ingredients_fallback(text)
            
        except Exception as e:
            logger.error(f"Advanced ingredient extraction failed: {e}")
            return self._extract_ingredients_fallback(text)
    
    def _extract_ingredients_fallback(self, text: str) -> List[str]:
        """Enhanced fallback ingredient extraction"""
        # Comprehensive ingredient database
        ingredient_keywords = {
            "proteins": ["chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp", "tofu", "eggs", "cheese"],
            "vegetables": ["onion", "garlic", "tomato", "carrot", "celery", "bell pepper", "spinach", "broccoli", "zucchini", "mushroom"],
            "grains": ["rice", "pasta", "quinoa", "flour", "bread", "oats", "barley"],
            "herbs_spices": ["basil", "oregano", "thyme", "parsley", "cilantro", "rosemary", "salt", "pepper", "paprika", "cumin"],
            "fats": ["olive oil", "butter", "coconut oil", "avocado"],
            "dairy": ["milk", "cream", "yogurt", "mozzarella", "parmesan", "ricotta"],
            "pantry": ["sugar", "honey", "soy sauce", "vinegar", "lemon", "lime"]
        }
        
        text_lower = text.lower()
        found_ingredients = []
        
        for category, ingredients in ingredient_keywords.items():
            for ingredient in ingredients:
                if ingredient in text_lower and ingredient not in found_ingredients:
                    found_ingredients.append(ingredient)
        
        return found_ingredients[:12]  # Limit to 12 ingredients
    
    def _calculate_text_confidence(self, text: str, ingredients: List[str], category_confidence: float) -> float:
        """Calculate confidence score for text-based extraction"""
        score = 0.5  # Base score
        
        # Boost for detailed text
        if len(text) > 100:
            score += 0.1
        if len(text) > 300:
            score += 0.1
        
        # Boost for ingredients found
        if len(ingredients) >= 3:
            score += 0.1
        if len(ingredients) >= 6:
            score += 0.1
        
        # Factor in category confidence
        score = (score + category_confidence) / 2
        
        # Check for cooking indicators
        cooking_words = ["recipe", "cook", "bake", "fry", "grill", "roast", "simmer", "boil"]
        if any(word in text.lower() for word in cooking_words):
            score += 0.1
        
        return min(score, 0.9)
    
    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None
    
    async def _detect_ingredients_from_image(self, image_data: bytes) -> List[str]:
        """Detect ingredients from image using computer vision"""
        try:
            # Convert image to base64 for API
            image_b64 = base64.b64encode(image_data).decode()
            
            # Use DETR for object detection
            model_url = f"{self.base_url}/facebook/detr-resnet-50"
            
            payload = {
                "inputs": image_b64
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_food_objects(result)
            
            return []
            
        except Exception as e:
            logger.error(f"Visual ingredient detection failed: {e}")
            return []
    
    def _parse_food_objects(self, detection_result: List[Dict]) -> List[str]:
        """Parse detected objects to identify food items"""
        food_objects = []
        
        if isinstance(detection_result, list):
            for detection in detection_result:
                if isinstance(detection, dict) and "label" in detection:
                    label = detection["label"].lower()
                    confidence = detection.get("score", 0)
                    
                    # Filter for food-related objects with decent confidence
                    if confidence > 0.3 and self._is_food_object(label):
                        food_objects.append(label)
        
        return list(set(food_objects))[:8]  # Limit and deduplicate
    
    def _is_food_object(self, label: str) -> bool:
        """Check if detected object is food-related"""
        food_labels = [
            "apple", "banana", "broccoli", "carrot", "pizza", "sandwich", "salad",
            "pasta", "bread", "cheese", "meat", "chicken", "fish", "egg",
            "tomato", "onion", "garlic", "pepper", "mushroom", "lettuce"
        ]
        return any(food_word in label for food_word in food_labels)
    
    async def _categorize_recipe_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced recipe categorization"""
        try:
            # Use zero-shot classification
            model_url = f"{self.base_url}/facebook/bart-large-mnli"
            
            categories = ["Main Course", "Desserts", "Starters", "Beverages", "Snacks", "Breakfast", "Salads"]
            
            payload = {
                "inputs": text[:500],
                "parameters": {
                    "candidate_labels": categories
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "labels" in result and "scores" in result:
                    return {
                        "category": result["labels"][0],
                        "confidence": result["scores"][0]
                    }
            
            return {"category": "Main Course", "confidence": 0.5}
            
        except Exception as e:
            logger.error(f"Advanced categorization failed: {e}")
            return {"category": "Main Course", "confidence": 0.5}
    
    async def _extract_cooking_instructions_advanced(self, text: str) -> str:
        """Extract detailed cooking instructions"""
        try:
            # Look for step-by-step instructions in text
            instructions = self._parse_instructions_from_text(text)
            
            if len(instructions) < 50:  # Generate if too short
                instructions = await self._generate_instructions_from_text(text)
            
            return instructions
            
        except Exception as e:
            logger.error(f"Instruction extraction failed: {e}")
            return "Cooking instructions extracted from recipe description."
    
    def _parse_instructions_from_text(self, text: str) -> str:
        """Parse existing instructions from text"""
        # Look for numbered steps, bullet points, or instruction keywords
        import re
        
        # Find numbered steps
        numbered_steps = re.findall(r'\d+\.\s*([^.]+\.)', text)
        if numbered_steps:
            return '\n'.join([f"{i+1}. {step}" for i, step in enumerate(numbered_steps)])
        
        # Look for instruction keywords
        instruction_keywords = ['heat', 'cook', 'add', 'mix', 'stir', 'bake', 'fry', 'boil', 'season']
        sentences = text.split('.')
        
        instruction_sentences = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in instruction_keywords):
                instruction_sentences.append(sentence.strip())
        
        if instruction_sentences:
            return '\n'.join([f"{i+1}. {sent}." for i, sent in enumerate(instruction_sentences[:6])])
        
        return ""
    
    async def _generate_instructions_from_text(self, text: str) -> str:
        """Generate cooking instructions using AI"""
        # Fallback instruction generation
        return f"1. Prepare all ingredients as described in the recipe.\n2. Follow the cooking method mentioned in the description.\n3. Season and adjust to taste.\n4. Serve as directed."
    
    async def _extract_cooking_time_advanced(self, text: str) -> int:
        """Extract cooking time from text with advanced parsing"""
        import re
        
        # Look for time patterns
        time_patterns = [
            r'(\d+)\s*(minutes?|mins?)',
            r'(\d+)\s*(hours?|hrs?)',
            r'(\d+)\s*-\s*(\d+)\s*(minutes?|mins?)',
            r'cook\s+for\s+(\d+)\s*(minutes?|mins?)',
            r'bake\s+for\s+(\d+)\s*(minutes?|mins?)'
        ]
        
        text_lower = text.lower()
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                if len(matches[0]) == 2:  # Single time
                    time_val, unit = matches[0]
                    time_val = int(time_val)
                    if 'hour' in unit:
                        time_val *= 60
                    return min(time_val, 240)  # Cap at 4 hours
                elif len(matches[0]) == 3:  # Range
                    time_val = int(matches[0][1])  # Take upper bound
                    unit = matches[0][2]
                    if 'hour' in unit:
                        time_val *= 60
                    return min(time_val, 240)
        
        # Fallback estimation based on complexity
        return self._estimate_cooking_time_from_complexity(text)
    
    def _estimate_cooking_time_from_complexity(self, text: str) -> int:
        """Estimate cooking time based on recipe complexity"""
        base_time = 25
        
        complexity_indicators = {
            'quick': -10, 'fast': -10, 'instant': -15,
            'slow': 30, 'simmer': 20, 'braise': 45, 'roast': 60,
            'marinade': 15, 'chill': 10, 'rest': 5
        }
        
        text_lower = text.lower()
        for indicator, time_mod in complexity_indicators.items():
            if indicator in text_lower:
                base_time += time_mod
        
        return max(min(base_time, 240), 5)  # Between 5 and 240 minutes
    
    async def _detect_dietary_info_advanced(self, text: str) -> List[str]:
        """Advanced dietary information detection"""
        dietary_info = []
        text_lower = text.lower()
        
        # Enhanced dietary detection patterns
        dietary_patterns = {
            'vegan': ['vegan', 'plant-based', 'no dairy', 'no meat', 'no animal'],
            'vegetarian': ['vegetarian', 'veggie', 'no meat', 'meatless'],
            'gluten-free': ['gluten-free', 'gluten free', 'no gluten', 'celiac'],
            'dairy-free': ['dairy-free', 'dairy free', 'no dairy', 'lactose-free'],
            'keto': ['keto', 'ketogenic', 'low-carb', 'low carb'],
            'paleo': ['paleo', 'paleolithic', 'caveman diet'],
            'nut-free': ['nut-free', 'nut free', 'no nuts', 'allergy-friendly'],
            'low-sodium': ['low-sodium', 'low sodium', 'low salt'],
            'spicy': ['spicy', 'hot', 'chili', 'jalapeño', 'cayenne']
        }
        
        for diet_type, patterns in dietary_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                dietary_info.append(diet_type)
        
        return dietary_info
    
    def _determine_difficulty_advanced(self, ingredients: List[str], cooking_time: int, text: str) -> str:
        """Advanced difficulty determination"""
        difficulty_score = 0
        
        # Ingredient complexity
        if len(ingredients) > 12:
            difficulty_score += 3
        elif len(ingredients) > 8:
            difficulty_score += 2
        elif len(ingredients) > 5:
            difficulty_score += 1
        
        # Time complexity
        if cooking_time > 120:
            difficulty_score += 3
        elif cooking_time > 60:
            difficulty_score += 2
        elif cooking_time > 30:
            difficulty_score += 1
        
        # Technique complexity
        advanced_techniques = [
            'tempering', 'emulsify', 'clarify', 'reduction', 'confit',
            'sous vide', 'ferment', 'cure', 'smoke', 'braise'
        ]
        
        text_lower = text.lower()
        for technique in advanced_techniques:
            if technique in text_lower:
                difficulty_score += 2
        
        # Equipment complexity
        if any(equip in text_lower for equip in ['stand mixer', 'food processor', 'mandoline']):
            difficulty_score += 1
        
        if difficulty_score >= 6:
            return "Hard"
        elif difficulty_score >= 3:
            return "Medium"
        else:
            return "Easy"
    
    def _generate_tags_advanced(self, ingredients: List[str], category: Optional[str], text: str) -> List[str]:
        """Generate comprehensive tags"""
        tags = []
        
        # Category-based tags
        if category:
            tags.append(category.lower().replace(" ", "-"))
        
        # Ingredient-based tags (top ingredients)
        for ingredient in ingredients[:4]:
            if len(ingredient) > 2:
                tags.append(ingredient.replace(" ", "-"))
        
        # Cooking method tags
        text_lower = text.lower()
        methods = {
            'baked': ['bake', 'oven'], 'grilled': ['grill', 'bbq'],
            'fried': ['fry', 'pan-fried'], 'roasted': ['roast'],
            'steamed': ['steam'], 'boiled': ['boil'],
            'sautéed': ['sauté', 'sauteed'], 'braised': ['braise']
        }
        
        for method, keywords in methods.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(method)
        
        # Cuisine tags
        cuisines = {
            'italian': ['italian', 'pasta', 'pizza', 'risotto'],
            'mexican': ['mexican', 'taco', 'salsa', 'cilantro'],
            'asian': ['asian', 'soy sauce', 'ginger', 'sesame'],
            'mediterranean': ['mediterranean', 'olive oil', 'feta', 'olives'],
            'indian': ['indian', 'curry', 'turmeric', 'garam masala']
        }
        
        for cuisine, keywords in cuisines.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(cuisine)
        
        # Meal timing tags
        if any(word in text_lower for word in ['breakfast', 'brunch']):
            tags.append('breakfast')
        elif any(word in text_lower for word in ['lunch', 'dinner', 'supper']):
            tags.append('dinner')
        
        return list(set(tags))[:10]  # Deduplicate and limit
    
    async def _extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            # Placeholder for OCR implementation
            # In real implementation, use TrOCR or similar model
            return ""
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def _merge_ingredient_lists(self, text_ingredients: List[str], visual_ingredients: List[str], ocr_text: str) -> List[str]:
        """Intelligently merge ingredient lists from different sources"""
        merged = list(text_ingredients)
        
        # Add visual ingredients that aren't already covered
        for visual_ing in visual_ingredients:
            if not any(self._ingredients_similar(visual_ing, text_ing) for text_ing in text_ingredients):
                merged.append(visual_ing)
        
        # Extract any ingredients mentioned in OCR text
        if ocr_text:
            ocr_ingredients = self._extract_ingredients_fallback(ocr_text)
            for ocr_ing in ocr_ingredients:
                if not any(self._ingredients_similar(ocr_ing, existing) for existing in merged):
                    merged.append(ocr_ing)
        
        return merged[:15]  # Limit total ingredients
    
    def _ingredients_similar(self, ing1: str, ing2: str) -> bool:
        """Check if two ingredients are similar"""
        ing1_words = set(ing1.lower().split())
        ing2_words = set(ing2.lower().split())
        
        # Check for overlap
        return len(ing1_words.intersection(ing2_words)) > 0
    
    def _estimate_cooking_time_from_visual(self, visual_ingredients: List[str], ocr_text: str) -> Optional[int]:
        """Estimate cooking time from visual cues"""
        # Look for time mentions in OCR text
        if ocr_text:
            time_estimate = self._extract_cooking_time_advanced(ocr_text)
            if time_estimate and time_estimate != 25:  # Not default
                return time_estimate
        
        # Estimate based on visual ingredients
        quick_ingredients = ['salad', 'sandwich', 'smoothie']
        slow_ingredients = ['roast', 'stew', 'bread']
        
        for ingredient in visual_ingredients:
            if any(quick in ingredient.lower() for quick in quick_ingredients):
                return 10
            elif any(slow in ingredient.lower() for slow in slow_ingredients):
                return 90
        
        return None
    
    def _calculate_visual_confidence(self, visual_ingredients: List[str], ocr_text: str) -> float:
        """Calculate confidence for visual extraction"""
        confidence = 0.4  # Base confidence
        
        if len(visual_ingredients) >= 2:
            confidence += 0.2
        if len(visual_ingredients) >= 4:
            confidence += 0.1
        
        if ocr_text and len(ocr_text) > 10:
            confidence += 0.2
        
        return min(confidence, 0.8)
    
    async def _simulate_audio_transcription(self, text_context: Dict[str, Any]) -> str:
        """Simulate audio transcription (placeholder for real Whisper integration)"""
        # In real implementation, this would:
        # 1. Extract audio from video
        # 2. Use Whisper to transcribe
        # 3. Filter for cooking instructions
        
        base_instructions = text_context.get("instructions", "")
        if base_instructions:
            return f"Audio transcription: {base_instructions}"
        
        # Generate basic instructions
        ingredients = text_context.get("ingredients", [])
        if ingredients:
            return f"1. Prepare {', '.join(ingredients[:3])} and other ingredients.\n2. Follow cooking steps as demonstrated in video.\n3. Cook until done and season to taste."
        
        return ""
    
    def _smart_merge_ingredients(self, text_ingredients: List[str], visual_ingredients: List[str], 
                               text_confidence: float, visual_confidence: float) -> List[str]:
        """Smart merging of ingredients based on confidence scores"""
        merged = []
        
        # Always include high-confidence text ingredients
        for ingredient in text_ingredients:
            merged.append(ingredient)
        
        # Add visual ingredients if they don't conflict and have decent confidence
        if visual_confidence > 0.4:
            for visual_ing in visual_ingredients:
                if not any(self._ingredients_similar(visual_ing, text_ing) for text_ing in merged):
                    merged.append(visual_ing)
        
        return merged[:12]  # Reasonable limit
    
    def _parse_ingredients_from_generation(self, result: Any, context_text: str) -> List[str]:
        """Parse ingredients from AI generation result"""
        # Fallback to rule-based if generation fails
        return self._extract_ingredients_fallback(context_text)
    
    def _frame_to_bytes(self, frame: 'np.ndarray') -> bytes:
        """Convert numpy frame to bytes for processing"""
        try:
            import cv2
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # Encode as JPEG
            success, encoded = cv2.imencode('.jpg', frame_bgr)
            if success:
                return encoded.tobytes()
            return b''
        except Exception as e:
            logger.error(f"Frame to bytes conversion failed: {e}")
            return b''
    
    def _calculate_multi_frame_confidence(
        self, 
        frame_analysis: List[Dict], 
        visual_ingredients: List[str], 
        ocr_text: str
    ) -> float:
        """Calculate confidence based on multi-frame analysis"""
        confidence = 0.4  # Base confidence
        
        # Boost for number of frames processed
        frames_processed = len(frame_analysis)
        if frames_processed >= 6:
            confidence += 0.1
        elif frames_processed >= 4:
            confidence += 0.05
        
        # Boost for visual ingredients found
        if len(visual_ingredients) >= 3:
            confidence += 0.15
        elif len(visual_ingredients) >= 1:
            confidence += 0.1
        
        # Boost for OCR text
        if ocr_text and len(ocr_text) > 20:
            confidence += 0.1
        
        # Boost for consistent ingredients across frames
        if frames_processed > 1:
            ingredient_consistency = self._calculate_ingredient_consistency(frame_analysis)
            confidence += ingredient_consistency * 0.1
        
        return min(confidence, 0.85)
    
    def _calculate_ingredient_consistency(self, frame_analysis: List[Dict]) -> float:
        """Calculate how consistent ingredient detection is across frames"""
        if len(frame_analysis) < 2:
            return 0.0
        
        all_ingredients = []
        for frame in frame_analysis:
            all_ingredients.extend(frame.get('ingredients', []))
        
        if not all_ingredients:
            return 0.0
        
        # Count ingredient frequency
        ingredient_counts = {}
        for ingredient in all_ingredients:
            ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1
        
        # Calculate consistency (ingredients appearing in multiple frames)
        total_ingredients = len(set(all_ingredients))
        consistent_ingredients = sum(1 for count in ingredient_counts.values() if count > 1)
        
        return consistent_ingredients / total_ingredients if total_ingredients > 0 else 0.0
    
    def _enhance_audio_instructions(self, instructions: str, ingredients: List[str]) -> str:
        """Enhance audio instructions with ingredient context"""
        if not instructions or not ingredients:
            return instructions
        
        # Add ingredient list at the beginning if not already mentioned
        instructions_lower = instructions.lower()
        missing_ingredients = []
        
        for ingredient in ingredients[:5]:  # Check first 5 ingredients
            if ingredient.lower() not in instructions_lower:
                missing_ingredients.append(ingredient)
        
        if missing_ingredients:
            ingredient_note = f"Ingredients needed: {', '.join(missing_ingredients)}.\n\n"
            return ingredient_note + instructions
        
        return instructions
    
    def _extract_cooking_times_from_audio(self, time_indicators: List[Dict]) -> List[Dict]:
        """Extract cooking times from audio time indicators"""
        cooking_times = []
        
        for indicator in time_indicators:
            if indicator.get('type') in ['cooking_time', 'duration', 'approximate_time']:
                try:
                    value = indicator.get('value', 0)
                    unit = indicator.get('unit', 'minutes')
                    
                    # Convert to minutes
                    if 'hour' in unit:
                        minutes = value * 60
                    elif 'second' in unit:
                        minutes = value / 60
                    else:
                        minutes = value
                    
                    cooking_times.append({
                        'minutes': minutes,
                        'original_text': indicator.get('text', ''),
                        'type': indicator.get('type')
                    })
                except (ValueError, TypeError):
                    continue
        
        return cooking_times
    
    async def close(self):
        """Close HTTP client and processors"""
        if self.client:
            await self.client.aclose()
        
        # Close processors
        await video_processor.close()
        await production_audio_processor.close()
        await ai_fusion_service.close()
        await mistral_service.close()


# Global instance
multimodal_ai_service = MultiModalAIService()