from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..items import Item, Recipe

class NutritionalCalculator():
    """
    Utility class for calculating and aggregating nutritional data.
    """

    # Why:
        # Handles all nutrient math in one place.

    # Interactions:
        # Called by Recipe, DayLog, possibly Workout.
    
    def sum_nutrition(items: list['Item']):
        pass
    
    def adjust_amount(item: 'Item', factor: float):
        pass
    
    def calculate_recipe_totals(recipe: 'Recipe'):
        pass
    
    def calculate_daylog_totals():
        pass