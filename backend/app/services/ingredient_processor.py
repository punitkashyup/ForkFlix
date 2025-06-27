import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from fractions import Fraction
from app.models.shopping_list import Unit, ItemCategory
from app.schemas.shopping_list import ProcessedIngredient

logger = logging.getLogger(__name__)


class IngredientProcessor:
    """Advanced ingredient processing engine with NLP capabilities."""
    
    def __init__(self):
        self._setup_patterns()
        self._setup_unit_mappings()
        self._setup_category_mappings()
        self._setup_dietary_flags()
    
    def _setup_patterns(self):
        """Setup regex patterns for ingredient parsing."""
        # Quantity patterns (numbers, fractions, ranges)
        self.quantity_patterns = [
            r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)',  # Range: 2-3
            r'(\d+)\s*(\d+)/(\d+)',  # Mixed fraction: 1 1/2
            r'(\d+)/(\d+)',  # Simple fraction: 1/2
            r'(\d+(?:\.\d+)?)',  # Decimal: 2.5
        ]
        
        # Unit patterns
        self.unit_patterns = [
            # Volume
            r'\b(cups?|c\.?)\b',
            r'\b(tablespoons?|tbsps?|tbs?|T\.?)\b',
            r'\b(teaspoons?|tsps?|tsp\.?|t\.?)\b',
            r'\b(liters?|litres?|l\.?)\b',
            r'\b(milliliters?|millilitres?|ml\.?)\b',
            r'\b(fluid\s+ounces?|fl\.?\s*oz\.?)\b',
            
            # Weight
            r'\b(pounds?|lbs?|lb\.?)\b',
            r'\b(ounces?|oz\.?)\b',
            r'\b(grams?|g\.?)\b',
            r'\b(kilograms?|kg\.?)\b',
            
            # Count
            r'\b(pieces?|pcs?)\b',
            r'\b(items?)\b',
            r'\b(cloves?)\b',
            
            # Containers
            r'\b(packages?|pkgs?)\b',
            r'\b(cans?)\b',
            r'\b(bottles?)\b',
            
            # Descriptive
            r'\b(pinch|dash)\b',
            r'\b(to\s+taste)\b',
        ]
        
        # Preparation methods to remove
        self.prep_words = {
            'chopped', 'diced', 'sliced', 'minced', 'grated', 'shredded',
            'crushed', 'ground', 'fresh', 'dried', 'frozen', 'canned',
            'cooked', 'raw', 'peeled', 'seeded', 'stemmed', 'trimmed',
            'rinsed', 'drained', 'thawed', 'softened', 'melted', 'beaten',
            'whisked', 'sifted', 'room temperature', 'cold', 'hot', 'warm'
        }
    
    def _setup_unit_mappings(self):
        """Setup unit conversion mappings."""
        self.unit_mappings = {
            # Volume
            'cup': Unit.CUP, 'cups': Unit.CUPS, 'c': Unit.CUP,
            'tablespoon': Unit.TABLESPOON, 'tablespoons': Unit.TABLESPOONS,
            'tbsp': Unit.TABLESPOON, 'tbsps': Unit.TABLESPOONS,
            'tbs': Unit.TABLESPOON, 'T': Unit.TABLESPOON,
            'teaspoon': Unit.TEASPOON, 'teaspoons': Unit.TEASPOONS,
            'tsp': Unit.TEASPOON, 'tsps': Unit.TEASPOONS, 't': Unit.TEASPOON,
            'liter': Unit.LITER, 'liters': Unit.LITERS, 'l': Unit.LITER,
            'milliliter': Unit.MILLILITER, 'milliliters': Unit.MILLILITERS, 'ml': Unit.MILLILITER,
            'fluid ounce': Unit.FLUID_OUNCE, 'fluid ounces': Unit.FLUID_OUNCES,
            'fl oz': Unit.FLUID_OUNCE, 'fl. oz': Unit.FLUID_OUNCE,
            
            # Weight
            'pound': Unit.POUND, 'pounds': Unit.POUNDS, 'lb': Unit.POUND, 'lbs': Unit.POUNDS,
            'ounce': Unit.OUNCE, 'ounces': Unit.OUNCES, 'oz': Unit.OUNCE,
            'gram': Unit.GRAM, 'grams': Unit.GRAMS, 'g': Unit.GRAM,
            'kilogram': Unit.KILOGRAM, 'kilograms': Unit.KILOGRAMS, 'kg': Unit.KILOGRAM,
            
            # Count
            'piece': Unit.PIECE, 'pieces': Unit.PIECES, 'pc': Unit.PIECE, 'pcs': Unit.PIECES,
            'item': Unit.ITEM, 'items': Unit.ITEMS,
            'clove': Unit.CLOVE, 'cloves': Unit.CLOVES,
            
            # Containers
            'package': Unit.PACKAGE, 'packages': Unit.PACKAGES, 'pkg': Unit.PACKAGE,
            'can': Unit.CAN, 'cans': Unit.CANS,
            'bottle': Unit.BOTTLE, 'bottles': Unit.BOTTLES,
            
            # Other
            'pinch': Unit.PINCH, 'dash': Unit.DASH,
            'to taste': Unit.TO_TASTE,
        }
    
    def _setup_category_mappings(self):
        """Setup ingredient to category mappings."""
        self.category_mappings = {
            # Produce
            'produce': [
                'tomato', 'onion', 'garlic', 'carrot', 'celery', 'potato', 'bell pepper',
                'lettuce', 'spinach', 'broccoli', 'cauliflower', 'cucumber', 'zucchini',
                'apple', 'banana', 'orange', 'lemon', 'lime', 'strawberry', 'avocado',
                'herbs', 'parsley', 'cilantro', 'basil', 'oregano', 'thyme', 'rosemary',
                'ginger', 'mushroom', 'corn', 'peas', 'beans', 'asparagus'
            ],
            
            # Meat & Seafood
            'meat_seafood': [
                'chicken', 'beef', 'pork', 'turkey', 'lamb', 'bacon', 'sausage',
                'salmon', 'tuna', 'shrimp', 'fish', 'crab', 'lobster', 'scallops',
                'ground beef', 'ground turkey', 'ground chicken', 'steak', 'chops'
            ],
            
            # Dairy & Eggs
            'dairy_eggs': [
                'milk', 'cream', 'butter', 'cheese', 'yogurt', 'eggs', 'sour cream',
                'cream cheese', 'mozzarella', 'cheddar', 'parmesan', 'cottage cheese',
                'heavy cream', 'half and half', 'buttermilk'
            ],
            
            # Pantry
            'pantry': [
                'flour', 'sugar', 'salt', 'pepper', 'oil', 'vinegar', 'rice', 'pasta',
                'bread', 'oats', 'quinoa', 'lentils', 'beans', 'chickpeas', 'nuts',
                'spices', 'vanilla', 'baking powder', 'baking soda', 'honey', 'maple syrup',
                'soy sauce', 'olive oil', 'coconut oil', 'vegetable oil', 'sesame oil',
                'hot sauce', 'mustard', 'ketchup', 'mayonnaise', 'worcestershire sauce'
            ],
            
            # Frozen
            'frozen': [
                'frozen vegetables', 'frozen fruit', 'ice cream', 'frozen pizza',
                'frozen chicken', 'frozen fish', 'frozen berries', 'frozen peas'
            ],
            
            # Bakery
            'bakery': [
                'bread', 'bagels', 'muffins', 'croissants', 'rolls', 'tortillas',
                'pita bread', 'naan', 'baguette', 'sourdough'
            ],
            
            # Beverages
            'beverages': [
                'water', 'juice', 'soda', 'beer', 'wine', 'coffee', 'tea',
                'milk', 'coconut water', 'sports drink', 'energy drink'
            ],
            
            # Snacks
            'snacks': [
                'chips', 'crackers', 'cookies', 'candy', 'chocolate', 'granola bars',
                'popcorn', 'pretzels', 'trail mix', 'dried fruit'
            ]
        }
    
    def _setup_dietary_flags(self):
        """Setup dietary restriction flags."""
        self.dietary_flags = {
            'gluten': ['wheat', 'flour', 'bread', 'pasta', 'soy sauce', 'beer'],
            'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt'],
            'nuts': ['almonds', 'walnuts', 'pecans', 'cashews', 'peanuts', 'pine nuts'],
            'shellfish': ['shrimp', 'crab', 'lobster', 'scallops', 'mussels', 'clams'],
            'soy': ['soy sauce', 'tofu', 'tempeh', 'edamame', 'miso'],
            'eggs': ['eggs', 'egg whites', 'egg yolks']
        }
    
    def process_ingredient(self, ingredient_text: str, recipe_id: Optional[str] = None) -> ProcessedIngredient:
        """Process a single ingredient string into structured data."""
        
        try:
            # Clean the ingredient text
            cleaned_text = self._clean_ingredient_text(ingredient_text)
            
            # Extract quantity and unit
            quantity, unit = self._extract_quantity_and_unit(cleaned_text)
            
            # Extract ingredient name
            name = self._extract_ingredient_name(cleaned_text, quantity, unit)
            
            # Determine category
            category = self._categorize_ingredient(name)
            
            # Get alternatives
            alternatives = self._get_alternatives(name)
            
            # Note: dietary_flags functionality available but not used in current schema
            
            # Calculate confidence
            confidence = self._calculate_confidence(ingredient_text, name, quantity, unit)
            
            return ProcessedIngredient(
                original_text=ingredient_text,
                name=name,
                quantity=quantity,
                unit=unit,
                category=category,
                confidence=confidence,
                alternatives=alternatives
            )
            
        except Exception as e:
            logger.error(f"Error processing ingredient '{ingredient_text}': {e}")
            return ProcessedIngredient(
                original_text=ingredient_text,
                name=ingredient_text,
                quantity=None,
                unit=None,
                category=ItemCategory.OTHER,
                confidence=0.1,
                alternatives=[]
            )
    
    def process_ingredients_bulk(self, ingredients: List[str], recipe_id: Optional[str] = None,
                               dietary_restrictions: List[str] = None) -> List[ProcessedIngredient]:
        """Process multiple ingredients in bulk."""
        return [
            self.process_ingredient(ingredient, recipe_id)
            for ingredient in ingredients
        ]
    
    def _clean_ingredient_text(self, text: str) -> str:
        """Clean and normalize ingredient text."""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove parenthetical notes
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_quantity_and_unit(self, text: str) -> Tuple[Optional[float], Optional[Unit]]:
        """Extract quantity and unit from ingredient text."""
        quantity = None
        unit = None
        
        # Try to find quantity patterns
        for pattern in self.quantity_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2 and '-' in match.group(0):
                    # Range pattern (take average)
                    q1, q2 = float(match.group(1)), float(match.group(2))
                    quantity = (q1 + q2) / 2
                elif len(match.groups()) == 3:
                    # Mixed fraction pattern
                    whole, num, den = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    quantity = whole + (num / den)
                elif len(match.groups()) == 2:
                    # Simple fraction pattern
                    num, den = int(match.group(1)), int(match.group(2))
                    quantity = num / den
                else:
                    # Decimal pattern
                    quantity = float(match.group(1))
                break
        
        # Try to find unit patterns
        for pattern in self.unit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                unit_text = match.group(1).lower().strip()
                unit = self.unit_mappings.get(unit_text)
                break
        
        return quantity, unit
    
    def _extract_ingredient_name(self, text: str, quantity: Optional[float], unit: Optional[Unit]) -> str:
        """Extract the core ingredient name from text."""
        # Remove quantity and unit
        if quantity is not None:
            text = re.sub(r'\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?', '', text)
            text = re.sub(r'\d+\s*\d+/\d+', '', text)
            text = re.sub(r'\d+/\d+', '', text)
        
        if unit is not None:
            for pattern in self.unit_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove preparation words
        words = text.split()
        filtered_words = []
        for word in words:
            if word not in self.prep_words and len(word) > 1:
                filtered_words.append(word)
        
        # Clean up and return
        name = ' '.join(filtered_words).strip()
        name = re.sub(r'\s+', ' ', name)
        
        return name if name else text.strip()
    
    def _categorize_ingredient(self, name: str) -> ItemCategory:
        """Categorize ingredient based on its name."""
        name_lower = name.lower()
        
        for category, keywords in self.category_mappings.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return ItemCategory(category)
        
        return ItemCategory.OTHER
    
    def _get_alternatives(self, name: str) -> List[str]:
        """Get basic alternative ingredient suggestions."""
        # For now, return empty list as alternatives feature is simplified
        return []
    
    def _check_dietary_flags(self, name: str) -> List[str]:
        """Check for dietary restriction flags."""
        flags = []
        name_lower = name.lower()
        
        for restriction, keywords in self.dietary_flags.items():
            for keyword in keywords:
                if keyword in name_lower:
                    flags.append(restriction)
                    break
        
        return flags
    
    def _calculate_confidence(self, original: str, name: str, quantity: Optional[float], 
                            unit: Optional[Unit]) -> float:
        """Calculate processing confidence score."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence if we extracted quantity
        if quantity is not None:
            confidence += 0.2
        
        # Boost confidence if we extracted unit
        if unit is not None:
            confidence += 0.2
        
        # Boost confidence if name seems reasonable
        if len(name) > 2 and name.replace(' ', '').isalpha():
            confidence += 0.1
        
        # Penalize if original text is very long or complex
        if len(original) > 100:
            confidence -= 0.2
        
        return min(1.0, max(0.1, confidence))


# Global instance
ingredient_processor = IngredientProcessor()