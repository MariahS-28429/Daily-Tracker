from items import Item

class Recipe(Item):
    """
    A recipe composed of multiple food items, referenced by their IDs.
    """

    # Why:
        # Composed of Food IDs (ingredients)
        # Needs to auto-update if a food changes.

    # Interactions:
        # Calls NutritionalCalculator to total up nutrients.
        # Uses ItemRegistry to resolve Ids to actual Food items.

    def __init__(self):
        self.data = {"serving_information": {
                            "serving_size": 0.0,
                            "serving_unit": "",
                            "servings": 0.0},
                        "nutrition": {
                            "macros": {
                                "protein": 0.0,
                                "carbs": 0.0,
                                "fats": {
                                    "total_fat": 0.0,
                                    "saturated_fat": 0.0,
                                    "trans_fat": 0.0}},
                            "cholesterol": 0.0,
                            "sodium": 0.0,
                            "fiber": 0.0,
                            "sugars": {
                                "total_sugars": 0.0,
                                "added_sugars": 0.0},
                            "vitamin_d": 0.0,
                            "calcium": 0.0,
                            "iron": 0.0,
                            "potassium": 0.0}}
    
    def build_from_ingredients(list_of_food_ids):
        """
        Assign ingredient IDs to this recipe's makeup field.
        """
        pass

    def calculate_totals():
        """
        Calculate the total nutrition of this recipe using NutritionalCalculator.
        """
        pass

    def update_ingredient(food_id, new_food_id):
        """
        Replace one ingredient with another.
        """
        pass

    def update_on_food_change():
        """
        Recalculate totals if any ingredient has changed in the registry.
        """
        pass

    def recalculate():
        pass