import asyncio
import httpx
from typing import Dict, Any, List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = None
        self.api_key = settings.huggingface_api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def extract_from_instagram(
        self,
        instagram_url: str,
        thumbnail_url: Optional[str] = None,
        description: str = "",
        caption: str = "",
        extract_ingredients: bool = True,
        categorize: bool = True,
        extract_instructions: bool = True
    ) -> Dict[str, Any]:
        """Extract recipe information from Instagram content using AI"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=60.0)
            
            # Combine all available text content
            combined_text = f"{description} {caption}".strip()
            
            result = {}
            
            # Extract ingredients using NER model
            if extract_ingredients:
                ingredients = await self.extract_ingredients_from_text(combined_text)
                result["ingredients"] = ingredients
            else:
                result["ingredients"] = []
            
            # Categorize recipe
            if categorize:
                category_result = await self.categorize_recipe(combined_text, result.get("ingredients", []))
                result["category"] = category_result["category"]
                confidence = category_result["confidence"]
            else:
                result["category"] = None
                confidence = 0.8
            
            # Predict cooking time
            cooking_time = await self.predict_cooking_time(result.get("ingredients", []), combined_text)
            result["cookingTime"] = cooking_time
            
            # Determine difficulty based on ingredients and cooking time
            difficulty = self._determine_difficulty(result.get("ingredients", []), cooking_time, combined_text)
            result["difficulty"] = difficulty
            
            # Detect dietary information
            dietary_info = await self.detect_dietary_info(result.get("ingredients", []), combined_text)
            result["dietaryInfo"] = dietary_info
            
            # Generate tags
            tags = self._generate_tags(result.get("ingredients", []), result.get("category"), combined_text)
            result["tags"] = tags
            
            # Extract instructions using text generation model
            if extract_instructions:
                instructions = await self.extract_instructions_from_text(combined_text, result.get("ingredients", []))
                result["instructions"] = instructions
            else:
                result["instructions"] = ""
            
            result["confidence"] = confidence
            
            logger.info(f"AI extraction completed for {instagram_url} with confidence {result['confidence']}")
            return result
            
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            # Return minimal fallback data on error
            return {
                "ingredients": [],
                "category": None,
                "cookingTime": None,
                "difficulty": None,
                "dietaryInfo": [],
                "tags": [],
                "instructions": "",
                "confidence": 0.0
            }
    
    async def categorize_recipe(self, text: str, ingredients: List[str]) -> Dict[str, Any]:
        """Categorize recipe using AI"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=60.0)
            
            # Use BART for zero-shot classification
            model_url = f"{self.base_url}/facebook/bart-large-mnli"
            
            # Combine text and ingredients for classification
            combined_text = f"{text} Ingredients: {', '.join(ingredients)}"
            
            categories = ["Main Course", "Desserts", "Starters", "Beverages", "Snacks"]
            
            payload = {
                "inputs": combined_text,
                "parameters": {
                    "candidate_labels": categories
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "labels" in result and "scores" in result:
                    category = result["labels"][0]
                    confidence = result["scores"][0]
                    return {
                        "category": category,
                        "confidence": confidence
                    }
            
            # Fallback to rule-based classification
            return await self._fallback_categorize_recipe(text, ingredients)
            
        except Exception as e:
            logger.error(f"Recipe categorization failed: {e}")
            return await self._fallback_categorize_recipe(text, ingredients)
    
    async def _fallback_categorize_recipe(self, text: str, ingredients: List[str]) -> Dict[str, Any]:
        """Fallback categorization when AI model is unavailable"""
        text_lower = text.lower()
        ingredients_text = " ".join(ingredients).lower()
        
        if any(word in text_lower or word in ingredients_text for word in ["dessert", "cake", "cookie", "sweet", "chocolate", "sugar"]):
            category = "Desserts"
            confidence = 0.9
        elif any(word in text_lower or word in ingredients_text for word in ["drink", "juice", "smoothie", "coffee", "tea"]):
            category = "Beverages"
            confidence = 0.85
        elif any(word in text_lower or word in ingredients_text for word in ["snack", "appetizer", "starter", "finger"]):
            category = "Starters"
            confidence = 0.8
        elif any(word in text_lower or word in ingredients_text for word in ["breakfast", "morning", "cereal", "toast"]):
            category = "Snacks"
            confidence = 0.75
        else:
            category = "Main Course"
            confidence = 0.7
        
        return {
            "category": category,
            "confidence": confidence
        }
    
    async def extract_ingredients_from_text(self, text: str) -> List[str]:
        """Extract ingredients from text using AI"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=60.0)
            
            # Use NER model to extract entities (ingredients)
            model_url = f"{self.base_url}/dbmdz/bert-large-cased-finetuned-conll03-english"
            
            payload = {
                "inputs": text
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract food-related entities
                ingredients = []
                if isinstance(result, list):
                    for entity in result:
                        if isinstance(entity, dict) and "word" in entity:
                            word = entity["word"].strip("#")
                            if self._is_food_ingredient(word):
                                ingredients.append(word.lower())
                
                # Remove duplicates and limit
                ingredients = list(dict.fromkeys(ingredients))[:10]
                
                if ingredients:
                    return ingredients
            
            # Fallback to rule-based extraction
            return await self._fallback_extract_ingredients(text)
            
        except Exception as e:
            logger.error(f"Ingredient extraction failed: {e}")
            return await self._fallback_extract_ingredients(text)
    
    async def _fallback_extract_ingredients(self, text: str) -> List[str]:
        """Fallback ingredient extraction when AI model is unavailable"""
        # Use simple text analysis instead of hardcoded ingredients
        text_lower = text.lower()
        found_ingredients = []
        
        # Basic ingredient detection patterns
        ingredient_patterns = [
            r'\b\d+\s*(?:cups?|tbsp|tsp|oz|lbs?|grams?|ml|liters?)\s+(\w+)',
            r'\b(\w+)\s+(?:cups?|tbsp|tsp|oz|lbs?|grams?|ml|liters?)',
            r'\b(?:add|use|mix|combine|stir)\s+(\w+)',
        ]
        
        import re
        for pattern in ingredient_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match) > 2 and match not in found_ingredients:
                    found_ingredients.append(match)
        
        # Return empty list if no ingredients found rather than hardcoded ones
        return found_ingredients[:10] if found_ingredients else []
    
    def _is_food_ingredient(self, word: str) -> bool:
        """Check if a word is likely a food ingredient"""
        food_keywords = [
            "oil", "salt", "pepper", "garlic", "onion", "tomato", "flour", "sugar",
            "egg", "milk", "cheese", "chicken", "beef", "pasta", "rice", "bread",
            "potato", "carrot", "celery", "basil", "parsley", "thyme", "oregano",
            "paprika", "cumin", "butter", "cream", "yogurt", "fish", "meat", "herbs",
            "spices", "vegetable", "fruit", "grain", "bean", "nut", "seed"
        ]
        return any(keyword in word.lower() for keyword in food_keywords)
    
    async def predict_cooking_time(self, ingredients: List[str], description: str) -> int:
        """Predict cooking time based on ingredients and description"""
        try:
            # Enhanced time prediction logic
            base_time = 20
            
            # Add time based on ingredients
            time_adding_ingredients = {
                "rice": 25, "pasta": 15, "chicken": 30, "beef": 45, "potato": 30,
                "beans": 60, "lentils": 25, "quinoa": 20, "barley": 45,
                "roast": 60, "steak": 15, "fish": 20, "shrimp": 10
            }
            
            for ingredient in ingredients:
                for food_item, time_add in time_adding_ingredients.items():
                    if food_item in ingredient.lower():
                        base_time += time_add
                        break
            
            # Adjust based on description keywords
            description_lower = description.lower()
            
            # Quick cooking indicators
            if any(word in description_lower for word in ["quick", "fast", "instant", "microwave", "5 minutes", "10 minutes"]):
                base_time = max(10, base_time - 15)
            
            # Slow cooking indicators
            elif any(word in description_lower for word in ["slow", "bake", "roast", "braise", "simmer", "stew", "oven"]):
                base_time += 30
            
            # Complexity indicators
            if any(word in description_lower for word in ["marinade", "overnight", "rest", "chill"]):
                base_time += 20
            
            return min(max(base_time, 5), 240)  # Between 5 and 240 minutes
            
        except Exception as e:
            logger.error(f"Cooking time prediction failed: {e}")
            return 30
    
    async def detect_dietary_info(self, ingredients: List[str], description: str) -> List[str]:
        """Detect dietary information from ingredients and description"""
        try:
            dietary_info = []
            
            ingredients_text = " ".join(ingredients).lower()
            description_lower = description.lower()
            combined_text = f"{ingredients_text} {description_lower}"
            
            # Enhanced dietary detection
            
            # Check for meat products
            meat_keywords = ["chicken", "beef", "pork", "fish", "meat", "turkey", "lamb", "bacon", "ham", "sausage", "seafood", "shrimp", "salmon"]
            has_meat = any(keyword in combined_text for keyword in meat_keywords)
            
            # Check for dairy products
            dairy_keywords = ["milk", "cheese", "butter", "cream", "yogurt", "mozzarella", "parmesan", "cheddar", "ricotta"]
            has_dairy = any(keyword in combined_text for keyword in dairy_keywords)
            
            # Check for eggs
            has_eggs = any(keyword in combined_text for keyword in ["egg", "eggs", "mayonnaise"])
            
            # Check for gluten
            gluten_keywords = ["flour", "bread", "pasta", "wheat", "barley", "rye", "oats", "noodles", "couscous"]
            has_gluten = any(keyword in combined_text for keyword in gluten_keywords)
            
            # Check for nuts
            nut_keywords = ["nuts", "peanut", "almond", "walnut", "cashew", "pecan", "hazelnut", "pistachio"]
            has_nuts = any(keyword in combined_text for keyword in nut_keywords)
            
            # Check for spicy indicators
            spicy_keywords = ["spicy", "hot", "chili", "pepper", "jalapeño", "cayenne", "paprika", "sriracha"]
            is_spicy = any(keyword in combined_text for keyword in spicy_keywords)
            
            # Check for low-carb indicators
            low_carb_keywords = ["keto", "low-carb", "cauliflower", "zucchini noodles"]
            is_low_carb = any(keyword in combined_text for keyword in low_carb_keywords)
            
            # Determine dietary categories
            if not has_meat and not has_dairy and not has_eggs:
                dietary_info.append("vegan")
            elif not has_meat:
                dietary_info.append("vegetarian")
            
            if not has_gluten:
                dietary_info.append("gluten-free")
            
            if not has_dairy:
                dietary_info.append("dairy-free")
            
            if not has_nuts:
                dietary_info.append("nut-free")
            
            # Check for keto/low-carb
            if is_low_carb or "keto" in combined_text:
                dietary_info.append("keto")
            
            # Check for explicit dietary mentions
            if "paleo" in combined_text:
                dietary_info.append("paleo")
            
            return dietary_info
            
        except Exception as e:
            logger.error(f"Dietary info detection failed: {e}")
            return []


    async def extract_instructions_from_text(self, text: str, ingredients: List[str]) -> str:
        """Extract cooking instructions from text using AI"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=60.0)
            
            # Use DialoGPT for text generation
            model_url = f"{self.base_url}/microsoft/DialoGPT-medium"
            
            # Create a prompt for instruction generation
            prompt = f"Given these ingredients: {', '.join(ingredients)}, here is a recipe: {text}. Generate step-by-step cooking instructions:"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 200,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = await self.client.post(model_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    # Extract instructions part
                    if "instructions:" in generated_text.lower():
                        instructions = generated_text.split("instructions:")[-1].strip()
                        return self._format_instructions(instructions)
            
            # Fallback to basic instruction generation
            return self._generate_basic_instructions(ingredients, text)
            
        except Exception as e:
            logger.error(f"Instruction extraction failed: {e}")
            return self._generate_basic_instructions(ingredients, text)
    
    def _generate_basic_instructions(self, ingredients: List[str], description: str) -> str:
        """Generate basic cooking instructions as fallback"""
        if not ingredients or not description:
            return "Instructions not available. Please refer to the original source."
        
        # Create more dynamic instructions based on actual content
        instructions = []
        description_lower = description.lower()
        
        # Extract any cooking methods mentioned in the description
        cooking_methods = []
        if "bake" in description_lower or "oven" in description_lower:
            cooking_methods.append("baking")
        if "fry" in description_lower or "pan" in description_lower:
            cooking_methods.append("frying")
        if "boil" in description_lower or "simmer" in description_lower:
            cooking_methods.append("boiling")
        if "grill" in description_lower:
            cooking_methods.append("grilling")
        
        if cooking_methods:
            instructions.append(f"1. Prepare ingredients for {' and '.join(cooking_methods)}.")
            instructions.append("2. Follow the cooking method shown in the original content.")
        else:
            instructions.append("1. Prepare ingredients as shown in the source.")
            instructions.append("2. Follow the cooking steps demonstrated in the original content.")
        
        instructions.append("3. Refer to the original Instagram post for detailed steps and timing.")
        
        return "\n".join(instructions)
    
    def _format_instructions(self, instructions: str) -> str:
        """Format instructions into numbered steps"""
        lines = instructions.split(".")
        formatted = []
        for i, line in enumerate(lines, 1):
            if line.strip():
                formatted.append(f"{i}. {line.strip()}.")
        return "\n".join(formatted)
    
    def _determine_difficulty(self, ingredients: List[str], cooking_time: int, description: str) -> str:
        """Determine recipe difficulty based on various factors"""
        difficulty_score = 0
        
        # Base score on number of ingredients
        if len(ingredients) > 10:
            difficulty_score += 2
        elif len(ingredients) > 5:
            difficulty_score += 1
        
        # Score based on cooking time
        if cooking_time > 60:
            difficulty_score += 2
        elif cooking_time > 30:
            difficulty_score += 1
        
        # Score based on cooking methods
        description_lower = description.lower()
        if any(word in description_lower for word in ["braise", "confit", "sous vide", "ferment"]):
            difficulty_score += 3
        elif any(word in description_lower for word in ["roast", "bake", "grill", "sauté"]):
            difficulty_score += 1
        
        # Score based on techniques
        if any(word in description_lower for word in ["fold", "whip", "temper", "caramelize"]):
            difficulty_score += 2
        
        if difficulty_score >= 4:
            return "Hard"
        elif difficulty_score >= 2:
            return "Medium"
        else:
            return "Easy"
    
    def _generate_tags(self, ingredients: List[str], category: Optional[str], description: str) -> List[str]:
        """Generate relevant tags for the recipe"""
        tags = []
        
        # Add category-based tags
        if category:
            tags.append(category.lower().replace(" ", "-"))
        
        # Add ingredient-based tags
        for ingredient in ingredients[:3]:  # Top 3 ingredients
            if len(ingredient) > 2:
                tags.append(ingredient)
        
        # Add cooking method tags
        description_lower = description.lower()
        cooking_methods = ["baked", "grilled", "fried", "roasted", "steamed", "boiled"]
        for method in cooking_methods:
            if method in description_lower:
                tags.append(method)
        
        # Add cuisine tags
        cuisines = ["italian", "mexican", "asian", "mediterranean", "indian", "chinese"]
        for cuisine in cuisines:
            if cuisine in description_lower:
                tags.append(cuisine)
        
        # Add meal time tags
        if any(word in description_lower for word in ["breakfast", "morning"]):
            tags.append("breakfast")
        elif any(word in description_lower for word in ["lunch", "dinner"]):
            tags.append("dinner")
        
        # Limit to 8 tags
        return list(dict.fromkeys(tags))[:8]
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()


# Global instance
ai_service = AIService()