import asyncio
import httpx
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class MistralService:
    """
    Mistral AI service for final recipe data extraction and refinement
    
    This service takes the raw output from all multimodal processing phases
    and uses Mistral AI to extract clean, structured recipe data with high accuracy.
    """
    
    def __init__(self):
        self.client = None
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-latest"  # Use the most capable model
        
    async def extract_structured_recipe(self, multimodal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Mistral AI to extract structured recipe data from multimodal processing results
        
        Args:
            multimodal_data: Complete output from the multimodal pipeline
            
        Returns:
            Dict containing clean, structured recipe data
        """
        try:
            logger.info("🧠 Starting Mistral AI final processing for recipe extraction")
            
            # Create the prompt for Mistral AI
            prompt = self._create_extraction_prompt(multimodal_data)
            
            # Call Mistral AI
            mistral_response = await self._call_mistral_api(prompt)
            
            if mistral_response and mistral_response.get("success"):
                # Parse the structured response
                recipe_data = self._parse_mistral_response(mistral_response["content"])
                
                # Add metadata
                recipe_data.update({
                    "extraction_method": "mistral_ai_final_processing",
                    "confidence": 0.95,  # Mistral AI provides very high accuracy
                    "processing_timestamp": datetime.now().isoformat(),
                    "original_data_phases": len([k for k in multimodal_data.keys() if k.startswith("phase_")]),
                })
                
                logger.info("✅ Mistral AI extraction completed successfully")
                return {
                    "success": True,
                    "recipe_data": recipe_data,
                    "confidence": 0.95
                }
            else:
                logger.error("❌ Mistral AI processing failed")
                return self._create_fallback_result(multimodal_data)
                
        except Exception as e:
            logger.error(f"❌ Mistral AI service error: {e}")
            return self._create_fallback_result(multimodal_data)
    
    def _create_extraction_prompt(self, data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for Mistral AI"""
        
        # Filter and prioritize data for better results
        filtered_data = self._filter_and_prioritize_data(data)
        
        prompt = f"""You are an expert recipe analyst. I will provide you with data extracted from Instagram recipe content using multiple AI methods (text analysis, video analysis, audio transcription, and AI fusion). Your task is to extract clean, accurate recipe information.

DATA:
{json.dumps(filtered_data, indent=2)}

IMPORTANT GUIDELINES:
- PRIORITIZE audio transcription data (phase_3_audio) as it contains the most detailed and accurate information
- Use AI fusion results (phase_4_fusion) for title and category guidance
- Cross-reference all phases to ensure consistency and completeness
- For ingredients mentioned in audio but not listed, include them with realistic quantities
- Create a proper recipe title that describes the actual dish being made

TASK: Extract the following recipe information with maximum accuracy:

1. **Recipe Name**: Clear, descriptive title
2. **Ingredients**: Complete list with quantities and measurements  
3. **Category**: Type of dish (e.g., "Appetizer", "Main Course", "Dessert", "Snack", "Sauce", "Beverage")
4. **Cooking Time**: Total time needed (preparation + cooking)
5. **Instructions**: Step-by-step cooking directions

IMPORTANT GUIDELINES:
- Use ALL available data sources (text, video, audio) to make informed decisions
- If audio transcription mentions ingredients/steps, prioritize that information
- If video analysis detected ingredients, include them in your list
- For cooking time, use explicit mentions or reasonable estimates based on the dish type
- For category, classify based on the dish description and ingredients
- Make instructions clear and actionable
- If some information is missing or unclear, use your culinary knowledge to fill gaps reasonably

RESPONSE FORMAT (JSON only, no markdown):
{{
  "recipe_name": "Clear recipe title",
  "ingredients": [
    {{"name": "ingredient name", "amount": "quantity", "unit": "measurement unit"}},
    {{"name": "ingredient name", "amount": "quantity", "unit": "measurement unit"}}
  ],
  "category": "Recipe category",
  "cooking_time": {{"prep_minutes": 10, "cook_minutes": 15, "total_minutes": 25}},
  "instructions": [
    "Step 1: Clear instruction",
    "Step 2: Clear instruction",
    "Step 3: Clear instruction"
  ],
  "difficulty": "Easy|Medium|Hard",
  "servings": "Number of servings",
  "notes": "Any special tips or variations"
}}

Extract the recipe data now:
"""
        return prompt.strip()
    
    def _filter_and_prioritize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and prioritize data to improve Mistral AI results"""
        filtered_data = {}
        
        # Always include audio data (highest priority)
        if "phase_3_audio" in data:
            filtered_data["phase_3_audio"] = data["phase_3_audio"]
        
        # Include AI fusion results (second priority) 
        if "phase_4_fusion" in data:
            filtered_data["phase_4_fusion"] = data["phase_4_fusion"]
        
        # Include video analysis if available
        if "phase_2_video" in data:
            filtered_data["phase_2_video"] = data["phase_2_video"]
        
        # Only include Phase 1 text if it has meaningful content
        if "phase_1_text" in data:
            phase_1 = data["phase_1_text"]
            source_text = phase_1.get("source_text", "")
            # Skip generic placeholder text
            if source_text and "A recipe shared on Instagram" not in source_text:
                filtered_data["phase_1_text"] = phase_1
        
        # Include metadata
        filtered_data["instagram_url"] = data.get("instagram_url")
        filtered_data["extraction_timestamp"] = data.get("extraction_timestamp")
        
        return filtered_data
    
    async def _call_mistral_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call the Mistral AI API"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=30.0)
            
            headers = {
                "Authorization": f"Bearer {settings.mistral_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  # Low temperature for consistent, factual output
                "max_tokens": 2000,
                "top_p": 0.9
            }
            
            logger.info(f"🔗 Calling Mistral AI API with model: {self.model}")
            
            response = await self.client.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "content": content,
                    "usage": result.get("usage", {}),
                    "model": result.get("model", self.model)
                }
            else:
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Mistral API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_mistral_response(self, content: str) -> Dict[str, Any]:
        """Parse the JSON response from Mistral AI"""
        try:
            # Clean the response - remove any markdown formatting
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Fix common JSON formatting issues from Mistral
            import re
            # Fix unquoted ranges like "amount": 4-5 -> "amount": "4-5"
            content = re.sub(r'"amount":\s*(\d+-\d+),', r'"amount": "\1",', content)
            
            # Parse JSON
            recipe_data = json.loads(content)
            
            # Validate and clean the data
            return self._validate_recipe_data(recipe_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Mistral response as JSON: {e}")
            logger.error(f"Raw content: {content}")
            
            # Try to extract data manually if JSON parsing fails
            return self._extract_data_manually(content)
    
    def _validate_recipe_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the recipe data from Mistral"""
        
        # Ensure required fields exist
        validated = {
            "recipe_name": data.get("recipe_name", "Unnamed Recipe"),
            "ingredients": data.get("ingredients", []),
            "category": data.get("category", "Main Course"),
            "cooking_time": data.get("cooking_time", {"total_minutes": 30}),
            "instructions": data.get("instructions", []),
            "difficulty": data.get("difficulty", "Medium"),
            "servings": data.get("servings", "4"),
            "notes": data.get("notes", "")
        }
        
        # Ensure ingredients are properly formatted
        if validated["ingredients"]:
            formatted_ingredients = []
            for ing in validated["ingredients"]:
                if isinstance(ing, dict):
                    formatted_ingredients.append({
                        "name": ing.get("name", "Unknown ingredient"),
                        "amount": ing.get("amount", ""),
                        "unit": ing.get("unit", "")
                    })
                elif isinstance(ing, str):
                    formatted_ingredients.append({
                        "name": ing,
                        "amount": "",
                        "unit": ""
                    })
            validated["ingredients"] = formatted_ingredients
        
        # Ensure cooking time is properly formatted
        if not isinstance(validated["cooking_time"], dict):
            validated["cooking_time"] = {"total_minutes": 30}
        
        # Ensure instructions is a list
        if isinstance(validated["instructions"], str):
            validated["instructions"] = [validated["instructions"]]
        
        return validated
    
    def _extract_data_manually(self, content: str) -> Dict[str, Any]:
        """Manually extract recipe data if JSON parsing fails"""
        logger.warning("Attempting manual data extraction from Mistral response")
        
        # Basic fallback extraction
        return {
            "recipe_name": "Recipe from Instagram",
            "ingredients": [],
            "category": "Main Course", 
            "cooking_time": {"total_minutes": 30},
            "instructions": [content[:500] + "..." if len(content) > 500 else content],
            "difficulty": "Medium",
            "servings": "4",
            "notes": "Extracted from multimodal analysis"
        }
    
    def _create_fallback_result(self, multimodal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback result if Mistral AI fails"""
        logger.warning("Creating fallback result due to Mistral AI failure")
        
        # Try to extract basic info from existing data
        fallback_recipe = {
            "recipe_name": "Instagram Recipe",
            "ingredients": [],
            "category": "Main Course",
            "cooking_time": {"total_minutes": 30},
            "instructions": [],
            "difficulty": "Medium", 
            "servings": "4",
            "notes": "Extracted using fallback method"
        }
        
        # Try to get some data from the multimodal results
        for phase_key, phase_data in multimodal_data.items():
            if isinstance(phase_data, dict):
                # Look for ingredients
                if "ingredients" in phase_data:
                    fallback_recipe["ingredients"] = phase_data["ingredients"]
                
                # Look for transcription text for instructions
                if "transcription" in phase_data and phase_data["transcription"]:
                    fallback_recipe["instructions"] = [phase_data["transcription"]]
        
        return {
            "success": False,
            "recipe_data": fallback_recipe,
            "confidence": 0.3,
            "note": "Fallback extraction used due to Mistral AI failure"
        }
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()


# Global instance
mistral_service = MistralService()