import logging
import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import asyncio
from app.models.shopping_list import ShoppingList, IngredientItem, ItemCategory
from app.core.database import firebase_service
from app.services.mistral_service import mistral_service

logger = logging.getLogger(__name__)


class ShoppingOptimizer:
    """Advanced ML-powered shopping list optimizer with preference learning."""
    
    def __init__(self):
        self.db = None
        
        # Price prediction models (simplified - in production would use actual ML models)
        self.seasonal_price_multipliers = {
            'spring': {'produce': 0.8, 'other': 1.0},
            'summer': {'produce': 0.7, 'other': 1.0},
            'fall': {'produce': 0.9, 'other': 1.0},
            'winter': {'produce': 1.2, 'other': 1.0}
        }
        
        # Store layout optimization
        self.store_layouts = {
            'whole_foods': {
                ItemCategory.PRODUCE: {'aisle': 1, 'priority': 1},
                ItemCategory.BAKERY: {'aisle': 2, 'priority': 2},
                ItemCategory.MEAT_SEAFOOD: {'aisle': 3, 'priority': 3},
                ItemCategory.DAIRY_EGGS: {'aisle': 4, 'priority': 4},
                ItemCategory.FROZEN: {'aisle': 5, 'priority': 5},
                ItemCategory.PANTRY: {'aisle': 6, 'priority': 6},
                ItemCategory.BEVERAGES: {'aisle': 7, 'priority': 7},
                ItemCategory.SNACKS: {'aisle': 8, 'priority': 8},
                ItemCategory.HOUSEHOLD: {'aisle': 9, 'priority': 9},
                ItemCategory.OTHER: {'aisle': 10, 'priority': 10}
            },
            'default': {
                ItemCategory.PRODUCE: {'aisle': 1, 'priority': 1},
                ItemCategory.MEAT_SEAFOOD: {'aisle': 2, 'priority': 2},
                ItemCategory.DAIRY_EGGS: {'aisle': 3, 'priority': 3},
                ItemCategory.FROZEN: {'aisle': 4, 'priority': 4},
                ItemCategory.BAKERY: {'aisle': 5, 'priority': 5},
                ItemCategory.PANTRY: {'aisle': 6, 'priority': 6},
                ItemCategory.BEVERAGES: {'aisle': 7, 'priority': 7},
                ItemCategory.SNACKS: {'aisle': 8, 'priority': 8},
                ItemCategory.HOUSEHOLD: {'aisle': 9, 'priority': 9},
                ItemCategory.OTHER: {'aisle': 10, 'priority': 10}
            }
        }
        
        # Bulk buying thresholds
        self.bulk_thresholds = {
            ItemCategory.PANTRY: {'min_quantity': 2, 'savings_percent': 0.15},
            ItemCategory.FROZEN: {'min_quantity': 3, 'savings_percent': 0.12},
            ItemCategory.HOUSEHOLD: {'min_quantity': 2, 'savings_percent': 0.20},
            ItemCategory.SNACKS: {'min_quantity': 3, 'savings_percent': 0.10}
        }
    
    def _get_db(self):
        """Get database connection, initialize if needed."""
        if self.db is None:
            self.db = firebase_service.get_db()
        return self.db

    async def optimize_shopping_list(self, shopping_list: ShoppingList, 
                                   preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize a shopping list using ML-powered recommendations."""
        try:
            if preferences is None:
                preferences = {}
            
            # Get user preferences and history
            user_profile = await self._get_user_profile(shopping_list.user_id)
            
            # Run parallel optimization tasks
            optimization_tasks = [
                self._optimize_for_cost(shopping_list, user_profile),
                self._optimize_for_time(shopping_list, user_profile),
                self._generate_bulk_recommendations(shopping_list, user_profile),
                self._predict_seasonal_alternatives(shopping_list),
                self._optimize_store_route(shopping_list, preferences.get('store_preference')),
                self._predict_price_trends(shopping_list),
            ]
            
            results = await asyncio.gather(*optimization_tasks, return_exceptions=True)
            
            # Combine optimization results
            optimization_data = {
                'cost_optimization': results[0] if not isinstance(results[0], Exception) else {},
                'time_optimization': results[1] if not isinstance(results[1], Exception) else {},
                'bulk_recommendations': results[2] if not isinstance(results[2], Exception) else [],
                'seasonal_alternatives': results[3] if not isinstance(results[3], Exception) else [],
                'optimized_route': results[4] if not isinstance(results[4], Exception) else [],
                'price_predictions': results[5] if not isinstance(results[5], Exception) else {},
                'user_preferences': user_profile
            }
            
            # Generate AI-powered insights
            ai_insights = await self._generate_ai_insights(shopping_list, optimization_data)
            optimization_data['ai_insights'] = ai_insights
            
            # Calculate savings potential
            savings_summary = self._calculate_savings_potential(shopping_list, optimization_data)
            
            # Update user preferences based on this shopping list
            await self._update_user_preferences(shopping_list, user_profile)
            
            return {
                'optimization_data': optimization_data,
                'savings_summary': savings_summary,
                'total_estimated_savings': savings_summary.get('total_savings', 0),
                'optimization_score': self._calculate_optimization_score(optimization_data),
                'recommendations': self._generate_actionable_recommendations(optimization_data)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing shopping list: {e}")
            return {
                'optimization_data': {},
                'savings_summary': {'total_savings': 0},
                'total_estimated_savings': 0,
                'optimization_score': 0.5,
                'recommendations': []
            }

    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get or create user shopping preference profile."""
        try:
            # Try to get existing profile
            db = self._get_db()
            if not db:
                logger.warning("Database not available - using default profile")
                return self._get_default_profile(user_id)
            
            doc = db.collection('user_shopping_profiles').document(user_id).get()
            
            if doc.exists:
                profile = doc.to_dict()
            else:
                # Create new profile with defaults
                profile = {
                    'user_id': user_id,
                    'preferred_stores': [],
                    'dietary_restrictions': [],
                    'budget_preferences': {
                        'average_weekly_budget': 150.0,
                        'price_sensitivity': 'medium',  # low, medium, high
                        'bulk_buying_preference': True
                    },
                    'shopping_patterns': {
                        'preferred_shopping_day': 'saturday',
                        'preferred_time': 'morning',
                        'avg_items_per_trip': 25,
                        'frequency_per_week': 1
                    },
                    'brand_preferences': {},  # ingredient_name: preferred_brand
                    'category_priorities': {},  # category: priority_score
                    'created_at': datetime.utcnow().isoformat(),
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                # Save new profile
                db.collection('user_shopping_profiles').document(user_id).set(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return self._get_default_profile(user_id)
    
    def _get_default_profile(self, user_id: str) -> Dict[str, Any]:
        """Get default user profile for development."""
        return {
            'user_id': user_id,
            'preferred_stores': [],
            'dietary_restrictions': [],
            'budget_preferences': {'average_weekly_budget': 150.0},
            'shopping_patterns': {},
            'brand_preferences': {},
            'category_priorities': {}
        }

    async def _optimize_for_cost(self, shopping_list: ShoppingList, 
                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize shopping list for cost savings."""
        total_estimated = shopping_list.estimated_total or 0
        budget_limit = shopping_list.budget_limit or user_profile.get('budget_preferences', {}).get('average_weekly_budget', 150)
        
        optimization = {
            'current_total': total_estimated,
            'budget_limit': budget_limit,
            'over_budget': total_estimated > budget_limit,
            'budget_utilization': (total_estimated / budget_limit) * 100 if budget_limit > 0 else 0,
            'cost_reduction_suggestions': [],
            'generic_alternatives': [],
            'price_comparison_opportunities': []
        }
        
        # Analyze expensive items
        expensive_items = sorted(
            [item for item in shopping_list.items if item.estimated_price and item.estimated_price > 10],
            key=lambda x: x.estimated_price or 0,
            reverse=True
        )
        
        for item in expensive_items[:5]:  # Top 5 expensive items
            optimization['cost_reduction_suggestions'].append({
                'item': item.name,
                'current_price': item.estimated_price,
                'suggestion': f"Consider generic brand for {item.name}",
                'potential_savings': (item.estimated_price or 0) * 0.3,  # 30% savings with generic
                'alternative': f"Generic {item.name.lower()}"
            })
        
        # Suggest store brands for categories with high markup
        high_markup_categories = [ItemCategory.SNACKS, ItemCategory.HOUSEHOLD, ItemCategory.BEVERAGES]
        for item in shopping_list.items:
            if item.category in high_markup_categories and item.estimated_price and item.estimated_price > 5:
                optimization['generic_alternatives'].append({
                    'item': item.name,
                    'category': item.category.value,
                    'current_price': item.estimated_price,
                    'generic_price': item.estimated_price * 0.7,  # 30% savings
                    'savings': item.estimated_price * 0.3
                })
        
        return optimization

    async def _optimize_for_time(self, shopping_list: ShoppingList, 
                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize shopping list for time efficiency."""
        patterns = user_profile.get('shopping_patterns', {})
        
        # Calculate estimated shopping time
        base_time = 20  # Base shopping time
        item_time = len(shopping_list.items) * 1.5  # 1.5 minutes per item
        category_changes = len(set(item.category for item in shopping_list.items)) * 2  # 2 minutes per category change
        
        estimated_time = base_time + item_time + category_changes
        
        optimization = {
            'estimated_shopping_time': estimated_time,
            'optimal_shopping_hours': self._get_optimal_shopping_hours(),
            'time_saving_tips': [
                "Group items by store section to minimize backtracking",
                "Shop during off-peak hours (weekday mornings)",
                "Use store mobile app for faster checkout",
                "Prepare shopping list in order of store layout"
            ],
            'efficiency_score': max(0, min(100, 100 - (estimated_time - 30) * 2)),  # Score based on time
            'category_organization': self._optimize_category_order(shopping_list.items),
            'peak_hours_to_avoid': ['saturday_afternoon', 'sunday_afternoon', 'weekday_evening']
        }
        
        return optimization

    async def _generate_bulk_recommendations(self, shopping_list: ShoppingList,
                                           user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate bulk buying recommendations."""
        bulk_recommendations = []
        
        # Check if user prefers bulk buying
        bulk_preference = user_profile.get('budget_preferences', {}).get('bulk_buying_preference', True)
        if not bulk_preference:
            return bulk_recommendations
        
        for item in shopping_list.items:
            threshold = self.bulk_thresholds.get(item.category)
            if not threshold or not item.estimated_price:
                continue
            
            if item.quantity and item.quantity >= threshold['min_quantity']:
                savings_percent = threshold['savings_percent']
                bulk_price = item.estimated_price * (1 - savings_percent)
                savings = item.estimated_price - bulk_price
                
                bulk_recommendations.append({
                    'item': item.name,
                    'category': item.category.value,
                    'current_quantity': item.quantity,
                    'bulk_quantity': item.quantity * 2,  # Suggest doubling
                    'current_price': item.estimated_price,
                    'bulk_price_per_unit': bulk_price / item.quantity,
                    'total_bulk_price': bulk_price * 2,
                    'savings_per_unit': savings,
                    'total_savings': savings * 2,
                    'recommendation': f"Buy 2x {item.name} in bulk to save ${savings * 2:.2f}",
                    'storage_consideration': self._get_storage_consideration(item.category),
                    'expiration_consideration': self._get_expiration_consideration(item.category)
                })
        
        # Sort by potential savings
        bulk_recommendations.sort(key=lambda x: x['total_savings'], reverse=True)
        
        return bulk_recommendations[:5]  # Top 5 recommendations

    async def _predict_seasonal_alternatives(self, shopping_list: ShoppingList) -> List[Dict[str, Any]]:
        """Predict seasonal alternatives for better pricing."""
        current_season = self._get_current_season()
        seasonal_alternatives = []
        
        for item in shopping_list.items:
            if item.category == ItemCategory.PRODUCE:
                alternatives = self._get_seasonal_produce_alternatives(item.name, current_season)
                
                if alternatives:
                    for alt in alternatives:
                        seasonal_alternatives.append({
                            'original_item': item.name,
                            'alternative': alt['name'],
                            'season': current_season,
                            'price_advantage': alt['price_multiplier'],
                            'availability': alt['availability'],
                            'suggestion': f"Consider {alt['name']} instead of {item.name} - {alt['advantage']}"
                        })
        
        return seasonal_alternatives

    async def _optimize_store_route(self, shopping_list: ShoppingList, 
                                  store_preference: Optional[str] = None) -> List[Dict[str, Any]]:
        """Optimize route through store based on layout."""
        store_key = store_preference.lower().replace(' ', '_') if store_preference else 'default'
        store_layout = self.store_layouts.get(store_key, self.store_layouts['default'])
        
        # Group items by category and sort by store layout
        category_groups = defaultdict(list)
        for item in shopping_list.items:
            category_groups[item.category].append(item)
        
        # Sort categories by store layout priority
        sorted_categories = sorted(
            category_groups.keys(),
            key=lambda cat: store_layout.get(cat, {}).get('priority', 999)
        )
        
        route = []
        for category in sorted_categories:
            items = category_groups[category]
            layout_info = store_layout.get(category, {'aisle': 0, 'priority': 999})
            
            route.append({
                'step': len(route) + 1,
                'category': category.value,
                'aisle': layout_info.get('aisle', 0),
                'items': [item.name for item in items],
                'item_count': len(items),
                'estimated_time': len(items) * 1.5 + 2,  # 1.5 min per item + 2 min category setup
                'tips': self._get_category_shopping_tips(category)
            })
        
        return route

    async def _predict_price_trends(self, shopping_list: ShoppingList) -> Dict[str, Any]:
        """Predict price trends for items in the shopping list."""
        current_season = self._get_current_season()
        price_predictions = {}
        
        for item in shopping_list.items:
            if not item.estimated_price:
                continue
            
            category_multiplier = self.seasonal_price_multipliers.get(current_season, {}).get(item.category.value, 1.0)
            predicted_price = item.estimated_price * category_multiplier
            
            price_predictions[item.name] = {
                'current_price': item.estimated_price,
                'predicted_price': predicted_price,
                'trend': 'increasing' if predicted_price > item.estimated_price else 'decreasing' if predicted_price < item.estimated_price else 'stable',
                'confidence': 0.7,  # Simplified confidence score
                'season_factor': category_multiplier,
                'recommendation': 'buy_now' if predicted_price > item.estimated_price else 'wait' if predicted_price < item.estimated_price else 'neutral'
            }
        
        return price_predictions

    async def _generate_ai_insights(self, shopping_list: ShoppingList, 
                                  optimization_data: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights using Mistral."""
        try:
            # Prepare context for AI
            context = {
                'total_items': shopping_list.total_items,
                'estimated_total': shopping_list.estimated_total,
                'budget_limit': shopping_list.budget_limit,
                'categories': list(set(item.category.value for item in shopping_list.items)),
                'optimization_summary': {
                    'cost_savings': optimization_data.get('cost_optimization', {}).get('cost_reduction_suggestions', []),
                    'bulk_opportunities': len(optimization_data.get('bulk_recommendations', [])),
                    'seasonal_alternatives': len(optimization_data.get('seasonal_alternatives', []))
                }
            }
            
            prompt = f"""
            Based on this shopping list analysis, provide 3-5 actionable insights and recommendations:
            
            Shopping List Summary:
            - Total Items: {context['total_items']}
            - Estimated Total: ${context['estimated_total']:.2f}
            - Budget Limit: ${context['budget_limit']:.2f}
            - Categories: {', '.join(context['categories'])}
            - Cost Savings Opportunities: {len(context['optimization_summary']['cost_savings'])}
            - Bulk Buying Opportunities: {context['optimization_summary']['bulk_opportunities']}
            - Seasonal Alternatives: {context['optimization_summary']['seasonal_alternatives']}
            
            Please provide specific, actionable insights that would help optimize this shopping trip for cost and efficiency.
            Each insight should be a complete sentence and practical.
            """
            
            response = await mistral_service.generate_text(prompt, max_tokens=300)
            
            if response and 'choices' in response and response['choices']:
                insights_text = response['choices'][0]['message']['content']
                # Split into individual insights (assuming they're separated by bullet points or newlines)
                insights = [
                    insight.strip().lstrip('•-*').strip() 
                    for insight in insights_text.split('\n') 
                    if insight.strip() and len(insight.strip()) > 20
                ]
                return insights[:5]  # Limit to 5 insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
        
        # Fallback insights
        return [
            "Consider shopping during off-peak hours to save time and avoid crowds.",
            "Group similar items together to minimize walking through the store.",
            "Check for store brand alternatives to reduce costs by 20-30%.",
            "Look for bulk buying opportunities for non-perishable items.",
            "Use seasonal produce when possible for better prices and freshness."
        ]

    def _calculate_savings_potential(self, shopping_list: ShoppingList, 
                                   optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total savings potential from all optimizations."""
        total_savings = 0
        savings_breakdown = {}
        
        # Cost optimization savings
        cost_opt = optimization_data.get('cost_optimization', {})
        cost_savings = sum(
            item.get('potential_savings', 0) 
            for item in cost_opt.get('cost_reduction_suggestions', [])
        )
        generic_savings = sum(
            item.get('savings', 0) 
            for item in cost_opt.get('generic_alternatives', [])
        )
        
        # Bulk buying savings
        bulk_savings = sum(
            item.get('total_savings', 0) 
            for item in optimization_data.get('bulk_recommendations', [])
        )
        
        total_savings = cost_savings + generic_savings + bulk_savings
        
        savings_breakdown = {
            'cost_optimization': cost_savings,
            'generic_alternatives': generic_savings,
            'bulk_buying': bulk_savings,
            'total_savings': total_savings,
            'percentage_savings': (total_savings / (shopping_list.estimated_total or 1)) * 100
        }
        
        return savings_breakdown

    def _calculate_optimization_score(self, optimization_data: Dict[str, Any]) -> float:
        """Calculate overall optimization score (0-1)."""
        scores = []
        
        # Cost optimization score
        cost_opt = optimization_data.get('cost_optimization', {})
        budget_utilization = cost_opt.get('budget_utilization', 100)
        cost_score = max(0, min(1, 1 - (budget_utilization - 80) / 40))  # Ideal is 80% budget utilization
        scores.append(cost_score)
        
        # Time optimization score
        time_opt = optimization_data.get('time_optimization', {})
        efficiency_score = time_opt.get('efficiency_score', 50) / 100
        scores.append(efficiency_score)
        
        # Bulk opportunities score
        bulk_count = len(optimization_data.get('bulk_recommendations', []))
        bulk_score = min(1, bulk_count / 3)  # Ideal is 3+ bulk opportunities
        scores.append(bulk_score)
        
        # Seasonal alternatives score
        seasonal_count = len(optimization_data.get('seasonal_alternatives', []))
        seasonal_score = min(1, seasonal_count / 2)  # Ideal is 2+ seasonal alternatives
        scores.append(seasonal_score)
        
        return sum(scores) / len(scores) if scores else 0.5

    def _generate_actionable_recommendations(self, optimization_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized, actionable recommendations."""
        recommendations = []
        
        # High impact cost savings
        cost_suggestions = optimization_data.get('cost_optimization', {}).get('cost_reduction_suggestions', [])
        for suggestion in cost_suggestions[:3]:
            recommendations.append({
                'priority': 'high',
                'category': 'cost_savings',
                'action': suggestion.get('suggestion', ''),
                'impact': f"Save ${suggestion.get('potential_savings', 0):.2f}",
                'effort': 'low'
            })
        
        # Bulk buying opportunities
        bulk_recs = optimization_data.get('bulk_recommendations', [])
        for bulk in bulk_recs[:2]:
            recommendations.append({
                'priority': 'medium',
                'category': 'bulk_buying',
                'action': bulk.get('recommendation', ''),
                'impact': f"Save ${bulk.get('total_savings', 0):.2f}",
                'effort': 'medium'
            })
        
        # Time optimization
        time_tips = optimization_data.get('time_optimization', {}).get('time_saving_tips', [])
        if time_tips:
            recommendations.append({
                'priority': 'medium',
                'category': 'time_efficiency',
                'action': time_tips[0],
                'impact': 'Save 10-15 minutes',
                'effort': 'low'
            })
        
        # Sort by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return recommendations[:6]  # Top 6 recommendations

    async def _update_user_preferences(self, shopping_list: ShoppingList, 
                                     user_profile: Dict[str, Any]) -> None:
        """Update user preferences based on shopping behavior."""
        try:
            # Update category priorities based on frequency
            category_counts = Counter(item.category.value for item in shopping_list.items)
            for category, count in category_counts.items():
                current_priority = user_profile.get('category_priorities', {}).get(category, 0)
                user_profile.setdefault('category_priorities', {})[category] = current_priority + count
            
            # Update shopping patterns
            user_profile.setdefault('shopping_patterns', {})['last_shopping_date'] = datetime.utcnow().isoformat()
            user_profile['last_updated'] = datetime.utcnow().isoformat()
            
            # Save updated profile
            db = self._get_db()
            if db:
                db.collection('user_shopping_profiles').document(shopping_list.user_id).set(user_profile)
            else:
                logger.warning("Database not available - skipping profile update")
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")

    # Helper methods
    def _get_current_season(self) -> str:
        """Get current season based on date."""
        month = datetime.now().month
        if 3 <= month <= 5:
            return 'spring'
        elif 6 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 11:
            return 'fall'
        else:
            return 'winter'

    def _get_optimal_shopping_hours(self) -> List[str]:
        """Get optimal shopping hours to avoid crowds."""
        return [
            "Weekday mornings (8-10 AM)",
            "Early weekday afternoons (1-3 PM)",
            "Late weekday evenings (8-9 PM)",
            "Early Sunday mornings (8-9 AM)"
        ]

    def _optimize_category_order(self, items: List[IngredientItem]) -> List[str]:
        """Optimize the order of categories for efficient shopping."""
        category_counts = Counter(item.category for item in items)
        # Sort by frequency (shop most common categories first)
        return [cat.value for cat, count in category_counts.most_common()]

    def _get_storage_consideration(self, category: ItemCategory) -> str:
        """Get storage consideration for bulk buying."""
        considerations = {
            ItemCategory.FROZEN: "Ensure adequate freezer space",
            ItemCategory.PRODUCE: "Check refrigerator space and freshness timeline",
            ItemCategory.PANTRY: "Verify pantry storage and expiration dates",
            ItemCategory.HOUSEHOLD: "No special storage requirements"
        }
        return considerations.get(category, "Consider available storage space")

    def _get_expiration_consideration(self, category: ItemCategory) -> str:
        """Get expiration consideration for bulk buying."""
        considerations = {
            ItemCategory.FROZEN: "Long shelf life - safe for bulk buying",
            ItemCategory.PRODUCE: "Short shelf life - buy only what you'll use",
            ItemCategory.DAIRY_EGGS: "Medium shelf life - check expiration dates",
            ItemCategory.PANTRY: "Long shelf life - ideal for bulk buying"
        }
        return considerations.get(category, "Check expiration dates before bulk buying")

    def _get_seasonal_produce_alternatives(self, item_name: str, season: str) -> List[Dict[str, Any]]:
        """Get seasonal alternatives for produce items."""
        seasonal_produce = {
            'spring': [
                {'name': 'asparagus', 'price_multiplier': 0.7, 'availability': 'peak', 'advantage': 'in season, 30% cheaper'},
                {'name': 'strawberries', 'price_multiplier': 0.8, 'availability': 'peak', 'advantage': 'peak freshness, 20% cheaper'},
                {'name': 'peas', 'price_multiplier': 0.9, 'availability': 'good', 'advantage': 'fresh and affordable'}
            ],
            'summer': [
                {'name': 'tomatoes', 'price_multiplier': 0.6, 'availability': 'peak', 'advantage': 'peak season, 40% cheaper'},
                {'name': 'corn', 'price_multiplier': 0.7, 'availability': 'peak', 'advantage': 'locally grown, 30% cheaper'},
                {'name': 'berries', 'price_multiplier': 0.8, 'availability': 'peak', 'advantage': 'fresh and sweet'}
            ],
            'fall': [
                {'name': 'apples', 'price_multiplier': 0.8, 'availability': 'peak', 'advantage': 'harvest season, 20% cheaper'},
                {'name': 'squash', 'price_multiplier': 0.7, 'availability': 'peak', 'advantage': 'locally harvested'},
                {'name': 'cranberries', 'price_multiplier': 0.9, 'availability': 'peak', 'advantage': 'fresh harvest'}
            ],
            'winter': [
                {'name': 'citrus', 'price_multiplier': 0.8, 'availability': 'peak', 'advantage': 'winter season fruit'},
                {'name': 'root vegetables', 'price_multiplier': 0.9, 'availability': 'good', 'advantage': 'storage crops'},
                {'name': 'brussels sprouts', 'price_multiplier': 0.85, 'availability': 'good', 'advantage': 'cold weather crop'}
            ]
        }
        
        # Simple matching - in production would use more sophisticated NLP
        alternatives = []
        seasonal_items = seasonal_produce.get(season, [])
        
        for seasonal_item in seasonal_items:
            if seasonal_item['name'].lower() in item_name.lower() or item_name.lower() in seasonal_item['name'].lower():
                alternatives.append(seasonal_item)
        
        return alternatives

    def _get_category_shopping_tips(self, category: ItemCategory) -> List[str]:
        """Get shopping tips for specific categories."""
        tips = {
            ItemCategory.PRODUCE: [
                "Shop for produce first to ensure freshness",
                "Check for seasonal specials and local options"
            ],
            ItemCategory.MEAT_SEAFOOD: [
                "Shop for meat and seafood after produce",
                "Look for manager's specials near closing time"
            ],
            ItemCategory.FROZEN: [
                "Shop for frozen items last to prevent thawing",
                "Check for bulk deals on frozen vegetables"
            ],
            ItemCategory.PANTRY: [
                "Stock up on non-perishables when on sale",
                "Compare unit prices for best value"
            ]
        }
        return tips.get(category, ["Compare prices and check expiration dates"])


# Global instance
shopping_optimizer = ShoppingOptimizer()