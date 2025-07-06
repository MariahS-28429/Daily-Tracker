from Item_Class import Item

class Supplement(Item):
    """
    A supplement item (e.g., vitamin) with data feilds.
    """

    def __init__(self, item_name: str, sub_type: str, tags: list, brand: str,
                 serving_size: float, serving_unit: str, servings: float,
                 active_ingredients: List[dict],
                 notes: str = "",
                 protein: float = 0.0, carbs: float = 0.0, total_fat: float = 0.0,
                 kcal: float = 0.0):
        """
        Initialize a supplement item. Most supplements don't include macros, but some do (e.g., protein powders).
        """        
        
        super().__init__(item_name, "supplement", sub_type, kcal, tags, brand)        
        self.data = {
            "serving_information": {
                "serving_size": CheckType.is_float(serving_size),
                "serving_unit": CheckType.is_string(serving_unit),
                "servings": CheckType.is_float(servings)
            },
            "active_ingredients": [
                {
                    "name": CheckType.is_string(ing.get("name")),
                    "amount": CheckType.is_float(ing.get("amount")),
                    "unit": CheckType.is_string(ing.get("unit"))
                } for ing in active_ingredients
            ]
        }

        # Only include nutrition if relevant
        if kcal > 0 or protein > 0 or carbs > 0 or total_fat > 0:
            self.data["nutrition"] = {
                "kcal": CheckType.is_float(kcal),
                "protein": CheckType.is_float(protein),
                "carbs": CheckType.is_float(carbs),
                "fat": CheckType.is_float(total_fat)
            }

        ItemRegistry.register_item(self.to_registry_dict())

    @classmethod
    def from_dict(cls, data: dict):
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
    
    def summary(self, max_ingredients=3) -> str:
        """
        Return a concise string summary of the supplement,
        including name, serving info, and key active ingredients.

        Args:
            max_ingredients (int): Max number of active ingredients to list.

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
