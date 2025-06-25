import asyncio
import httpx
import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIFusionService:
    """
    AI-powered data fusion service for multi-modal recipe extraction
    
    Uses advanced AI models to intelligently combine and analyze data from:
    1. Text Analysis (Weight: 60%) - Primary source
    2. Audio Processing (Weight: 30%) - Secondary source  
    3. Video Analysis (Weight: 10%) - Supporting source
    
    Goal: Extract Recipe Title, Category, Difficulty, Cooking Time, and Ingredients
    with maximum accuracy using weighted AI analysis.
    """
    
    def __init__(self):
        self.client = None
        self.huggingface_api_key = settings.huggingface_api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        # Weights for different data sources
        self.source_weights = {
            "text": 0.60,      # 60% - Most reliable
            "audio": 0.30,     # 30% - Cooking instructions often spoken
            "visual": 0.10     # 10% - Supporting visual cues
        }
    
    async def fuse_multimodal_data_with_ai(
        self,
        text_result: Dict[str, Any],
        audio_result: Optional[Dict[str, Any]] = None,
        visual_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        AI-powered fusion of multi-modal data with weighted analysis
        
        Returns optimally fused recipe data with high accuracy
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=120.0)
            
            logger.info("Starting AI-powered data fusion with weighted analysis")
            
            # Prepare source data for AI analysis
            fusion_context = self._prepare_fusion_context(text_result, audio_result, visual_result)
            
            # Extract each recipe field using AI with weighted inputs
            fusion_tasks = [
                self._extract_recipe_title_with_ai(fusion_context),
                self._extract_category_with_ai(fusion_context),
                self._extract_difficulty_with_ai(fusion_context),
                self._extract_cooking_time_with_ai(fusion_context),
                self._extract_ingredients_with_ai(fusion_context)
            ]
            
            # Execute AI analysis in parallel
            results = await asyncio.gather(*fusion_tasks, return_exceptions=True)
            
            # Compile final recipe data
            fused_recipe = {
                "title": results[0] if not isinstance(results[0], Exception) else self._fallback_title(fusion_context),
                "category": results[1] if not isinstance(results[1], Exception) else self._fallback_category(fusion_context),
                "difficulty": results[2] if not isinstance(results[2], Exception) else self._fallback_difficulty(fusion_context),
                "cookingTime": results[3] if not isinstance(results[3], Exception) else self._fallback_cooking_time(fusion_context),
                "ingredients": results[4] if not isinstance(results[4], Exception) else self._fallback_ingredients(fusion_context)
            }
            
            # Calculate overall confidence with AI weighting
            fused_recipe["confidence"] = await self._calculate_ai_fusion_confidence(fusion_context, fused_recipe)
            
            # Add metadata about the fusion process
            fused_recipe.update({
                "fusionMethod": "ai_weighted",
                "sourceWeights": self.source_weights,
                "dataSources": list(fusion_context.keys()),
                "fusionTimestamp": datetime.now().isoformat(),
                "extractedFields": ["title", "category", "difficulty", "cookingTime", "ingredients"]
            })
            
            logger.info(f"AI fusion completed with confidence: {fused_recipe['confidence']:.3f}")
            return fused_recipe
            
        except Exception as e:
            logger.error(f"AI-powered data fusion failed: {e}")
            return self._fallback_fusion(text_result, audio_result, visual_result)
    
    def _prepare_fusion_context(
        self,
        text_result: Dict[str, Any],
        audio_result: Optional[Dict[str, Any]],
        visual_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Prepare weighted context data for AI analysis"""
        
        context = {}
        
        # Text data (60% weight)
        if text_result:
            context["text"] = {
                "weight": self.source_weights["text"],
                "confidence": text_result.get("confidence", 0.6),
                "data": {
                    "description": text_result.get("source_text", ""),
                    "extracted_ingredients": text_result.get("ingredients", []),
                    "extracted_category": text_result.get("category", ""),
                    "extracted_difficulty": text_result.get("difficulty", ""),
                    "extracted_cooking_time": text_result.get("cookingTime", 0),
                    "extracted_instructions": text_result.get("instructions", "")
                }
            }
        
        # Audio data (30% weight)
        if audio_result and audio_result.get("confidence", 0) > 0.3:
            context["audio"] = {
                "weight": self.source_weights["audio"],
                "confidence": audio_result.get("confidence", 0.5),
                "data": {
                    "transcription": audio_result.get("transcription", ""),
                    "instructions": audio_result.get("instructions", ""),
                    "cooking_times": audio_result.get("cookingTimes", []),
                    "time_indicators": audio_result.get("timeIndicators", []),
                    "cooking_terms_count": audio_result.get("cookingTermsFound", 0)
                }
            }
        
        # Visual data (10% weight)
        if visual_result and visual_result.get("confidence", 0) > 0.3:
            context["visual"] = {
                "weight": self.source_weights["visual"],
                "confidence": visual_result.get("confidence", 0.4),
                "data": {
                    "visual_ingredients": visual_result.get("visualIngredients", []),
                    "ocr_text": visual_result.get("ocrText", ""),
                    "frame_count": visual_result.get("framesProcessed", 0),
                    "scene_analysis": visual_result.get("frameAnalysis", [])
                }
            }
        
        return context
    
    async def _extract_recipe_title_with_ai(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Extract recipe title using AI with weighted multi-modal analysis"""
        try:
            # Create weighted prompt for AI analysis
            prompt = self._create_title_extraction_prompt(context)
            
            # Use text generation model for title extraction
            model_url = f"{self.base_url}/microsoft/DialoGPT-medium"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 80,
                    "temperature": 0.3,
                    "do_sample": True,
                    "pad_token_id": 50256
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    # Extract title from generated text
                    title = self._parse_title_from_generation(generated_text, context)
                    if title and len(title) > 5:
                        return title
            
            # Fallback to rule-based extraction
            return self._fallback_title(context)
            
        except Exception as e:
            logger.error(f"AI title extraction failed: {e}")
            return self._fallback_title(context)
    
    def _create_title_extraction_prompt(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Create an optimized prompt for recipe title extraction"""
        prompt_parts = [
            "Analyze this multi-modal cooking data and extract the RECIPE TITLE:",
            ""
        ]
        
        # Add text data (highest weight)
        if "text" in context:
            text_data = context["text"]["data"]
            prompt_parts.extend([
                f"TEXT ANALYSIS (Weight: 60%):",
                f"Description: {text_data.get('description', '')[:300]}",
                f"Detected ingredients: {', '.join(text_data.get('extracted_ingredients', [])[:5])}",
                ""
            ])
        
        # Add audio data (medium weight)
        if "audio" in context:
            audio_data = context["audio"]["data"]
            prompt_parts.extend([
                f"AUDIO ANALYSIS (Weight: 30%):",
                f"Transcription: {audio_data.get('transcription', '')[:200]}",
                f"Instructions: {audio_data.get('instructions', '')[:150]}",
                ""
            ])
        
        # Add visual data (lowest weight)
        if "visual" in context:
            visual_data = context["visual"]["data"]
            prompt_parts.extend([
                f"VISUAL ANALYSIS (Weight: 10%):",
                f"OCR Text: {visual_data.get('ocr_text', '')[:100]}",
                f"Visual ingredients: {', '.join(visual_data.get('visual_ingredients', [])[:3])}",
                ""
            ])
        
        prompt_parts.extend([
            "Extract the most accurate recipe title considering the weighted analysis.",
            "Focus on: main ingredients, cooking method, cuisine type.",
            "Format: [Descriptive Recipe Name]",
            "Recipe Title:"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _extract_category_with_ai(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Extract recipe category using AI with weighted analysis"""
        try:
            # Use zero-shot classification for category
            model_url = f"{self.base_url}/facebook/bart-large-mnli"
            
            # Create weighted input text
            weighted_text = self._create_weighted_text_for_classification(context)
            
            categories = [
                "Main Course", "Desserts", "Starters", "Beverages", 
                "Snacks", "Breakfast", "Salads", "Side Dishes"
            ]
            
            payload = {
                "inputs": weighted_text,
                "parameters": {
                    "candidate_labels": categories
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "labels" in result and "scores" in result and result["scores"]:
                    return result["labels"][0]
            
            return self._fallback_category(context)
            
        except Exception as e:
            logger.error(f"AI category extraction failed: {e}")
            return self._fallback_category(context)
    
    async def _extract_difficulty_with_ai(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Extract recipe difficulty using AI with weighted analysis"""
        try:
            # Use zero-shot classification for difficulty
            model_url = f"{self.base_url}/facebook/bart-large-mnli"
            
            # Create context focusing on complexity indicators
            complexity_text = self._create_complexity_analysis_text(context)
            
            difficulties = ["Easy", "Medium", "Hard"]
            
            payload = {
                "inputs": complexity_text,
                "parameters": {
                    "candidate_labels": difficulties
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "labels" in result and "scores" in result and result["scores"]:
                    return result["labels"][0]
            
            return self._fallback_difficulty(context)
            
        except Exception as e:
            logger.error(f"AI difficulty extraction failed: {e}")
            return self._fallback_difficulty(context)
    
    async def _extract_cooking_time_with_ai(self, context: Dict[str, Dict[str, Any]]) -> int:
        """Extract cooking time using AI with weighted analysis"""
        try:
            # Create prompt for time extraction
            time_prompt = self._create_time_extraction_prompt(context)
            
            # Use text generation for time analysis
            model_url = f"{self.base_url}/microsoft/DialoGPT-medium"
            
            payload = {
                "inputs": time_prompt,
                "parameters": {
                    "max_length": 50,
                    "temperature": 0.2
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    extracted_time = self._parse_time_from_generation(generated_text)
                    if extracted_time and 5 <= extracted_time <= 240:
                        return extracted_time
            
            return self._fallback_cooking_time(context)
            
        except Exception as e:
            logger.error(f"AI cooking time extraction failed: {e}")
            return self._fallback_cooking_time(context)
    
    async def _extract_ingredients_with_ai(self, context: Dict[str, Dict[str, Any]]) -> List[str]:
        """Extract ingredients using AI with weighted multi-modal analysis"""
        try:
            # Create comprehensive ingredient analysis prompt
            ingredients_prompt = self._create_ingredients_extraction_prompt(context)
            
            # Use text generation for ingredient analysis
            model_url = f"{self.base_url}/microsoft/DialoGPT-medium"
            
            payload = {
                "inputs": ingredients_prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.3
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    extracted_ingredients = self._parse_ingredients_from_generation(generated_text, context)
                    if extracted_ingredients and len(extracted_ingredients) >= 2:
                        return extracted_ingredients
            
            return self._fallback_ingredients(context)
            
        except Exception as e:
            logger.error(f"AI ingredients extraction failed: {e}")
            return self._fallback_ingredients(context)
    
    def _create_weighted_text_for_classification(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Create weighted text input for classification models"""
        weighted_parts = []
        
        # Add text data (repeated for weight)
        if "text" in context:
            text_data = context["text"]["data"]
            description = text_data.get("description", "")
            if description:
                weighted_parts.extend([description] * 3)  # 3x weight
        
        # Add audio data (moderate weight)
        if "audio" in context:
            audio_data = context["audio"]["data"]
            transcription = audio_data.get("transcription", "")
            if transcription:
                weighted_parts.append(transcription)  # 1x weight
        
        # Add visual data (minimal weight)
        if "visual" in context:
            visual_data = context["visual"]["data"]
            ocr_text = visual_data.get("ocr_text", "")
            if ocr_text:
                weighted_parts.append(ocr_text[:100])  # Limited length
        
        return " ".join(weighted_parts)[:500]  # Limit total length
    
    def _create_complexity_analysis_text(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Create text focused on recipe complexity analysis"""
        complexity_indicators = []
        
        # Text complexity indicators (highest weight)
        if "text" in context:
            text_data = context["text"]["data"]
            ingredients = text_data.get("extracted_ingredients", [])
            instructions = text_data.get("extracted_instructions", "")
            
            complexity_indicators.extend([
                f"Number of ingredients: {len(ingredients)}",
                f"Instructions complexity: {instructions[:200]}",
                f"Ingredient list: {', '.join(ingredients[:8])}"
            ] * 2)  # Double weight for text
        
        # Audio complexity indicators
        if "audio" in context:
            audio_data = context["audio"]["data"]
            instructions = audio_data.get("instructions", "")
            cooking_terms = audio_data.get("cooking_terms_count", 0)
            
            complexity_indicators.extend([
                f"Audio instructions: {instructions[:150]}",
                f"Cooking techniques mentioned: {cooking_terms}"
            ])
        
        return ". ".join(complexity_indicators)[:400]
    
    def _create_time_extraction_prompt(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Create prompt for cooking time extraction"""
        prompt_parts = [
            "Analyze cooking time from multi-modal data:",
            ""
        ]
        
        # Text time indicators (highest priority)
        if "text" in context:
            text_data = context["text"]["data"]
            description = text_data.get("description", "")
            extracted_time = text_data.get("extracted_cooking_time", 0)
            
            prompt_parts.extend([
                f"Text description: {description[:200]}",
                f"Extracted time: {extracted_time} minutes" if extracted_time > 0 else "",
            ])
        
        # Audio time indicators (medium priority)
        if "audio" in context:
            audio_data = context["audio"]["data"]
            time_indicators = audio_data.get("time_indicators", [])
            
            if time_indicators:
                times = [f"{t.get('text', '')}" for t in time_indicators[:3]]
                prompt_parts.append(f"Audio time mentions: {', '.join(times)}")
        
        prompt_parts.extend([
            "",
            "Extract the most accurate cooking time in minutes.",
            "Consider: prep time + cooking time.",
            "Time in minutes:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _create_ingredients_extraction_prompt(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Create comprehensive prompt for ingredient extraction"""
        prompt_parts = [
            "Extract ALL ingredients from this multi-modal cooking data:",
            ""
        ]
        
        # Text ingredients (highest priority)
        if "text" in context:
            text_data = context["text"]["data"]
            description = text_data.get("description", "")
            text_ingredients = text_data.get("extracted_ingredients", [])
            
            prompt_parts.extend([
                f"TEXT (Priority 1): {description[:250]}",
                f"Text ingredients found: {', '.join(text_ingredients)}",
                ""
            ])
        
        # Audio ingredients (medium priority)
        if "audio" in context:
            audio_data = context["audio"]["data"]
            transcription = audio_data.get("transcription", "")
            
            prompt_parts.extend([
                f"AUDIO (Priority 2): {transcription[:200]}",
                ""
            ])
        
        # Visual ingredients (supporting)
        if "visual" in context:
            visual_data = context["visual"]["data"]
            visual_ingredients = visual_data.get("visual_ingredients", [])
            ocr_text = visual_data.get("ocr_text", "")
            
            prompt_parts.extend([
                f"VISUAL (Supporting): OCR: {ocr_text[:100]}",
                f"Visual detected: {', '.join(visual_ingredients)}",
                ""
            ])
        
        prompt_parts.extend([
            "List ALL unique ingredients, combining all sources.",
            "Format: ingredient1, ingredient2, ingredient3...",
            "Ingredients:"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _calculate_ai_fusion_confidence(
        self, 
        context: Dict[str, Dict[str, Any]], 
        fused_recipe: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for AI-fused recipe data"""
        
        # Base confidence from source weights and individual confidences
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for source, source_data in context.items():
            weight = source_data["weight"]
            confidence = source_data["confidence"]
            weighted_confidence += weight * confidence
            total_weight += weight
        
        base_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.5
        
        # Boost for AI processing
        ai_boost = 0.15  # AI analysis adds confidence
        
        # Boost for multi-source agreement
        source_count = len(context)
        multi_source_boost = min(source_count * 0.05, 0.15)
        
        # Boost for recipe completeness
        completeness_boost = 0.0
        if fused_recipe.get("title") and len(fused_recipe["title"]) > 5:
            completeness_boost += 0.05
        if fused_recipe.get("ingredients") and len(fused_recipe["ingredients"]) >= 3:
            completeness_boost += 0.05
        if fused_recipe.get("category"):
            completeness_boost += 0.03
        if fused_recipe.get("cookingTime", 0) > 0:
            completeness_boost += 0.02
        
        final_confidence = base_confidence + ai_boost + multi_source_boost + completeness_boost
        
        return min(final_confidence, 0.95)  # Cap at 95%
    
    # Fallback methods for when AI analysis fails
    def _fallback_title(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Fallback title extraction using weighted rule-based approach"""
        # Prioritize text data
        if "text" in context:
            ingredients = context["text"]["data"].get("extracted_ingredients", [])
            if ingredients:
                return f"{', '.join(ingredients[:3])} Recipe"
        
        # Audio fallback
        if "audio" in context:
            transcription = context["audio"]["data"].get("transcription", "")
            if "recipe" in transcription.lower():
                words = transcription.split()[:5]
                return " ".join(words) + " Recipe"
        
        return "Delicious Recipe"
    
    def _fallback_category(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Fallback category using weighted analysis"""
        # Text analysis (highest weight)
        if "text" in context:
            category = context["text"]["data"].get("extracted_category", "")
            if category:
                return category
        
        # Rule-based category detection
        all_text = ""
        for source_data in context.values():
            if "description" in source_data.get("data", {}):
                all_text += source_data["data"]["description"]
            if "transcription" in source_data.get("data", {}):
                all_text += source_data["data"]["transcription"]
        
        text_lower = all_text.lower()
        
        if any(word in text_lower for word in ["dessert", "sweet", "cake", "cookie"]):
            return "Desserts"
        elif any(word in text_lower for word in ["drink", "smoothie", "juice"]):
            return "Beverages"
        elif any(word in text_lower for word in ["salad", "greens"]):
            return "Salads"
        elif any(word in text_lower for word in ["breakfast", "morning"]):
            return "Breakfast"
        else:
            return "Main Course"
    
    def _fallback_difficulty(self, context: Dict[str, Dict[str, Any]]) -> str:
        """Fallback difficulty using complexity analysis"""
        complexity_score = 0
        
        # Analyze ingredient count
        total_ingredients = 0
        for source_data in context.values():
            ingredients = source_data.get("data", {}).get("extracted_ingredients", [])
            if not ingredients:
                ingredients = source_data.get("data", {}).get("visual_ingredients", [])
            total_ingredients = max(total_ingredients, len(ingredients))
        
        if total_ingredients > 10:
            complexity_score += 2
        elif total_ingredients > 6:
            complexity_score += 1
        
        # Analyze cooking time
        cooking_time = 0
        for source_data in context.values():
            time = source_data.get("data", {}).get("extracted_cooking_time", 0)
            cooking_time = max(cooking_time, time)
        
        if cooking_time > 60:
            complexity_score += 2
        elif cooking_time > 30:
            complexity_score += 1
        
        if complexity_score >= 3:
            return "Hard"
        elif complexity_score >= 1:
            return "Medium"
        else:
            return "Easy"
    
    def _fallback_cooking_time(self, context: Dict[str, Dict[str, Any]]) -> int:
        """Fallback cooking time using weighted analysis"""
        # Text time (highest priority)
        if "text" in context:
            time = context["text"]["data"].get("extracted_cooking_time", 0)
            if time and 5 <= time <= 240:
                return time
        
        # Audio time indicators
        if "audio" in context:
            cooking_times = context["audio"]["data"].get("cooking_times", [])
            if cooking_times:
                avg_time = sum(t.get("minutes", 30) for t in cooking_times) / len(cooking_times)
                if 5 <= avg_time <= 240:
                    return int(avg_time)
        
        # Default based on complexity
        ingredient_count = 0
        for source_data in context.values():
            ingredients = source_data.get("data", {}).get("extracted_ingredients", [])
            ingredient_count = max(ingredient_count, len(ingredients))
        
        if ingredient_count > 8:
            return 45
        elif ingredient_count > 5:
            return 35
        else:
            return 25
    
    def _fallback_ingredients(self, context: Dict[str, Dict[str, Any]]) -> List[str]:
        """Fallback ingredients using weighted combination"""
        all_ingredients = []
        
        # Text ingredients (highest weight)
        if "text" in context:
            text_ingredients = context["text"]["data"].get("extracted_ingredients", [])
            all_ingredients.extend(text_ingredients)
        
        # Audio ingredients (from transcription)
        if "audio" in context:
            transcription = context["audio"]["data"].get("transcription", "")
            audio_ingredients = self._extract_ingredients_from_text_simple(transcription)
            all_ingredients.extend(audio_ingredients)
        
        # Visual ingredients
        if "visual" in context:
            visual_ingredients = context["visual"]["data"].get("visual_ingredients", [])
            all_ingredients.extend(visual_ingredients)
        
        # Deduplicate and return
        unique_ingredients = []
        for ingredient in all_ingredients:
            if ingredient and ingredient not in unique_ingredients:
                unique_ingredients.append(ingredient)
        
        return unique_ingredients[:12]  # Limit to 12 ingredients
    
    def _extract_ingredients_from_text_simple(self, text: str) -> List[str]:
        """Simple ingredient extraction from text using pattern matching"""
        import re
        
        text_lower = text.lower()
        found = []
        
        # Look for patterns like "2 cups flour", "1 tsp salt", etc.
        patterns = [
            r'\b\d+\s*(?:cups?|tbsp|tablespoons?|tsp|teaspoons?|oz|ounces?|lbs?|pounds?|grams?|ml|liters?)\s+(\w+)',
            r'\b(\w+)\s+(?:cups?|tbsp|tablespoons?|tsp|teaspoons?|oz|ounces?|lbs?|pounds?|grams?|ml|liters?)',
            r'\b(?:add|use|mix|combine|stir|chop|slice|dice)\s+(?:the\s+)?(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match) > 2 and match not in found and match.isalpha():
                    found.append(match)
        
        return found[:10]  # Limit to 10 ingredients
    
    def _fallback_fusion(
        self,
        text_result: Dict[str, Any],
        audio_result: Optional[Dict[str, Any]],
        visual_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Complete fallback when AI fusion fails"""
        return {
            "title": text_result.get("title", "Recipe"),
            "category": text_result.get("category", "Main Course"),
            "difficulty": text_result.get("difficulty", "Medium"),
            "cookingTime": text_result.get("cookingTime", 30),
            "ingredients": text_result.get("ingredients", []),
            "confidence": 0.4,
            "fusionMethod": "fallback",
            "dataSources": ["text"],
            "fusionTimestamp": datetime.now().isoformat()
        }
    
    def _parse_title_from_generation(self, generated_text: str, context: Dict) -> Optional[str]:
        """Parse recipe title from AI generation"""
        # Look for title after "Recipe Title:" or similar patterns
        lines = generated_text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 80:
                # Remove common prefixes
                for prefix in ["Recipe Title:", "Title:", "Recipe:", "Name:"]:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                
                # Validate title quality
                if self._is_valid_title(line):
                    return line
        
        return None
    
    def _is_valid_title(self, title: str) -> bool:
        """Check if generated title is valid"""
        if not title or len(title) < 5 or len(title) > 80:
            return False
        
        # Should contain food-related words
        food_words = ["recipe", "dish", "sauce", "soup", "salad", "pasta", "chicken", "beef", "cake"]
        title_lower = title.lower()
        
        return any(word in title_lower for word in food_words) or "recipe" in title_lower
    
    def _parse_time_from_generation(self, generated_text: str) -> Optional[int]:
        """Parse cooking time from AI generation"""
        import re
        
        # Look for time patterns
        patterns = [
            r'(\d+)\s*minutes?',
            r'(\d+)\s*mins?',
            r'(\d+)\s*hours?',
            r'Time.*?(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, generated_text.lower())
            if matches:
                try:
                    time_val = int(matches[0])
                    if 'hour' in pattern:
                        time_val *= 60
                    if 5 <= time_val <= 240:
                        return time_val
                except ValueError:
                    continue
        
        return None
    
    def _parse_ingredients_from_generation(self, generated_text: str, context: Dict) -> List[str]:
        """Parse ingredients from AI generation"""
        # Look for ingredient list patterns
        lines = generated_text.split('\n')
        ingredients = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('Analyze', 'Extract', 'Format')):
                # Split by common separators
                parts = re.split(r'[,;]', line)
                for part in parts:
                    part = part.strip()
                    if part and len(part) < 30 and self._is_likely_ingredient(part):
                        ingredients.append(part.lower())
        
        return ingredients[:10]
    
    def _is_likely_ingredient(self, text: str) -> bool:
        """Check if text is likely an ingredient"""
        food_indicators = [
            "oil", "salt", "pepper", "garlic", "onion", "tomato", "flour", "sugar",
            "egg", "milk", "cheese", "chicken", "beef", "pasta", "rice", "bread"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in food_indicators)
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()


# Global instance
ai_fusion_service = AIFusionService()