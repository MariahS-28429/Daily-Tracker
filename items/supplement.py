from items import Item
from helper.type import CheckType
from summary import Registry

from typing import List

class Supplement(Item):
    """
    Represents a nutritional supplement item (e.g., multivitamin, protein powder).

    Stores detailed information about the supplement including serving size,
    brand, active ingredients, and optionally macronutrient content.

    Attributes:
        name (str): The name of the supplement.
        sub_type (str): A subtype or category of the supplement (e.g., "vitamin", "protein powder").
        tags (list): List of tags for categorization.
        brand (str): Brand name of the supplement.
        data (dict): Dictionary containing detailed serving information, active ingredients,
            and optionally nutrition info.
        kcal (float): Calories per serving (optional).
        protein (float): Protein content per serving in grams (optional).
        carbs (float): Carbohydrate content per serving in grams (optional).
        total_fat (float): Total fat content per serving in grams (optional).
    """
    
    # --- Initialization & Construction ---

    def __init__(self, item_name: str, sub_type: str, tags: list, brand: str,
                 serving_size: float, serving_unit: str, servings: float,
                 active_ingredients: List[dict],
                 notes: str = "",
                 protein: float = 0.0, carbs: float = 0.0, total_fat: float = 0.0,
                 kcal: float = 0.0):
        """
        Initialize a Supplement instance.

        Most supplements don't include macronutrients, but some do (e.g., protein powders).

        Args:
            item_name (str): Name of the supplement.
            sub_type (str): Supplement subtype.
            tags (list): List of tags.
            brand (str): Brand name.
            serving_size (float): Size of a single serving.
            serving_unit (str): Unit of the serving size (e.g., "mg", "g", "capsule").
            servings (float): Number of servings per container.
            active_ingredients (List[dict]): List of active ingredient dicts with keys
                'name' (str), 'amount' (float), and 'unit' (str).
            notes (str, optional): Additional notes about the supplement.
            protein (float, optional): Protein content per serving (default 0.0).
            carbs (float, optional): Carbohydrate content per serving (default 0.0).
            total_fat (float, optional): Fat content per serving (default 0.0).
            kcal (float, optional): Calories per serving (default 0.0).
        """
        
        super().__init__(item_name, "supplement", sub_type, kcal, tags, brand)        
        
        # Store serving info with type validation
        self.data = {
            "serving_information": {
                "serving_size": CheckType.is_float(serving_size),
                "serving_unit": CheckType.is_string(serving_unit),
                "servings": CheckType.is_float(servings)
            },
            # Store active ingredients with validation
            "active_ingredients": [
                {
                    "name": CheckType.is_string(ing.get("name")),
                    "amount": CheckType.is_float(ing.get("amount")),
                    "unit": CheckType.is_string(ing.get("unit"))
                } for ing in active_ingredients
            ]
        }

        # Include nutrition info only if any value > 0
        if kcal > 0 or protein > 0 or carbs > 0 or total_fat > 0:
            self.data["nutrition"] = {
                "kcal": CheckType.is_float(kcal),
                "protein": CheckType.is_float(protein),
                "carbs": CheckType.is_float(carbs),
                "fat": CheckType.is_float(total_fat)
            }

        # Register this item globally
        Registry.register_item(self.to_registry_dict())

    @classmethod
    def from_dict(cls, data: dict) -> 'Supplement':
        """
        Create a Supplement instance from a dictionary (e.g., parsed JSON).

        Args:
            data (dict): Dictionary containing supplement data.

        Returns:
            Supplement: A new Supplement instance populated from `data`.
        """

        # Extract the basic fields expected by Item
        item_name = data.get("name", "")
        sub_type = data.get("sub_type", "")
        tags = data.get("tags", [])
        brand = data.get("brand", "")
        
        # Extract kcal and optional macros (may be missing)
        kcal = data.get("kcal", 0.0)
        protein = 0.0
        carbs = 0.0
        total_fat = 0.0
        
        # Extract nested nutrition if present
        nutrition = data.get("data", {}).get("nutrition", {})
        if nutrition:
            kcal = nutrition.get("kcal", kcal)
            protein = nutrition.get("protein", 0.0)
            carbs = nutrition.get("carbs", 0.0)
            total_fat = nutrition.get("fat", 0.0)
        
        # Extract serving info safely
        serving_info = data.get("data", {}).get("serving_information", {})
        serving_size = serving_info.get("serving_size", 0.0)
        serving_unit = serving_info.get("serving_unit", "")
        servings = serving_info.get("servings", 0.0)
        
        # Extract active ingredients, defaulting to empty list
        active_ingredients = data.get("data", {}).get("active_ingredients", [])
        
        # Notes field (optional)
        notes = data.get("data", {}).get("notes", "")
        
        # Build and return the Supplement instance
        return cls(
            item_name=item_name,
            sub_type=sub_type,
            tags=tags,
            brand=brand,
            serving_size=serving_size,
            serving_unit=serving_unit,
            servings=servings,
            active_ingredients=active_ingredients,
            notes=notes,
            protein=protein,
            carbs=carbs,
            total_fat=total_fat,
            kcal=kcal
        )
    
    # --- Representation & Summary ---
    
    def summary(self, max_ingredients=3) -> str:
        """"
        Generate a concise string summary of the supplement.

        Includes name, subtype, brand, serving information, key active ingredients,
        and calorie content.

        Args:
            max_ingredients (int): Maximum number of active ingredients to list.

        Returns:
            str: Summary string.
        """

        base = f"{self.name.title()} ({self.sub_type}), Brand: {self.brand.title()}"
        
        serving = self.data.get("serving_information", {})
        serving_size = serving.get("serving_size", "?")
        serving_unit = serving.get("serving_unit", "")
        servings = serving.get("servings", "?")
        serving_info = f"Serving: {serving_size} {serving_unit}, Servings per container: {servings}"

        ingredients = self.data.get("active_ingredients", [])
        if not ingredients:
            ingredient_summary = "No active ingredients listed"
        else:
            listed = ingredients[:max_ingredients]
            ingredient_summary = ", ".join(f"{ing['name']} ({ing['amount']}{ing['unit']})" for ing in listed)
            if len(ingredients) > max_ingredients:
                ingredient_summary += ", ..."

        nutrition = self.data.get("nutrition", {})
        kcal = nutrition.get("kcal")
        kcal_str = f"{kcal} kcal" if kcal is not None else "No kcal info"

        return f"{base} | {serving_info} | Active Ingredients: {ingredient_summary} | {kcal_str}"

    # --- Data Access & Helpers ---
    
    def get_active_ingredient_names(self) -> List[str]:
        """
        Get the list of active ingredient names in the supplement.

        Returns:
            List[str]: Names of active ingredients.
        """

        return [ing["name"] for ing in self.data.get("active_ingredients", [])]
    
    def has_macros(self) -> bool:
        """
        Determine whether the supplement includes macronutrient information.

        Returns:
            bool: True if macronutrient info is present, False otherwise.
        """

        return "nutrition" in self.data
