from items import Item
from helper import CheckType, NutritionalCalculator
from summary import Registry

class Food(Item):
    """
    A basic food item with full nutritional data.
    Inherits from Item.
    """
    
    def __init__(self, item_name: str, sub_type: str, kcal: float, tags: list, brand: str,
                 serving_size: float, serving_unit: str, servings: float, 
                 protein: float, carbs: float, total_fat: float, saturated_fat: float, trans_fat: float, 
                 cholesterol: float, sodium: float, fiber: float,
                 total_sugars: float, added_sugars: float,
                 vitamin_d: float, calcium: float, iron: float, potassium: float, save: bool = True):  
        super().__init__(item_name, "food", sub_type, kcal, tags, brand)         
        self.data = {"serving_information": {
                        "serving_size": CheckType.is_float(serving_size),
                        "serving_unit": CheckType.is_string(serving_unit),
                        "servings": CheckType.is_float(servings)},
                    "nutrition": {
                        "macros": {
                            "protein": CheckType.is_float(protein),
                            "carbs": CheckType.is_float(carbs),
                            "fats": {
                                "total_fat": CheckType.is_float(total_fat),
                                "saturated_fat": CheckType.is_float(saturated_fat),
                                "trans_fat": CheckType.is_float(trans_fat)}},
                        "cholesterol": CheckType.is_float(cholesterol),
                        "sodium": CheckType.is_float(sodium),
                        "fiber": CheckType.is_float(fiber),
                        "sugars": {
                            "total_sugars": CheckType.is_float(total_sugars),
                            "added_sugars": CheckType.is_float(added_sugars)},
                        "vitamin_d": CheckType.is_float(vitamin_d),
                        "calcium": CheckType.is_float(calcium),
                        "iron": CheckType.is_float(iron),
                        "potassium": CheckType.is_float(potassium)}}
        
        NutritionalCalculator.check_nutritional_data(self)

        if save:
            Registry.register_item(Item.to_registry_dict(self))

    def edit_macros(self, macro_type: str, change: float):
        macros = self.data["nutrition"]["macros"]

        if macro_type.lower() in ["protein", "carbs"]:
            macros[macro_type] += CheckType.is_float(change)
        
        elif macro_type.lower() in ["total_fat", "saturated_fat", "trans_fat"]:
            macros["fats"][macro_type] += CheckType.is_float(change)
        
        else:
            raise ValueError(f"Invalid macro type: {macro_type}. Must be one of: "
                            "'protein', 'carbs', 'total_fat', 'saturated_fat', 'trans_fat'.")
        
        self.kcal = NutritionalCalculator.kcal_from_macros(self)

        Registry.update_item_by_id(self.id, Item.to_registry_dict(self))
    
    @classmethod
    def from_dict(cls, data: dict) -> "Food":
        """
        Creates a Food instance from a dictionary of data.

        Args:
            data (dict): A dictionary with keys matching Food's structure.

        Returns:
            Food: A new Food object.
        """
        item_name = CheckType.is_string(data["item_name"])
        sub_type = CheckType.is_string(data["sub_type"])
        kcal = CheckType.is_float(data["kcal"])
        tags = data.get("tags", [])
        brand = CheckType.is_string(data["brand"])

        # Serving info
        serving_info = data["data"]["serving_information"]
        serving_size = serving_info["serving_size"]
        serving_unit = serving_info["serving_unit"]
        servings = serving_info["servings"]

        # Macros
        macros = data["data"]["nutrition"]["macros"]
        protein = macros["protein"]
        carbs = macros["carbs"]
        fats = macros["fats"]
        total_fat = fats["total_fat"]
        saturated_fat = fats["saturated_fat"]
        trans_fat = fats["trans_fat"]

        # Micros and others
        nutrition = data["data"]["nutrition"]
        cholesterol = nutrition["cholesterol"]
        sodium = nutrition["sodium"]
        fiber = nutrition["fiber"]
        sugars = nutrition["sugars"]
        total_sugars = sugars["total_sugars"]
        added_sugars = sugars["added_sugars"]
        vitamin_d = nutrition["vitamin_d"]
        calcium = nutrition["calcium"]
        iron = nutrition["iron"]
        potassium = nutrition["potassium"]

        obj = cls(
            item_name, sub_type, kcal, tags, brand,
            serving_size, serving_unit, servings,
            protein, carbs, total_fat, saturated_fat, trans_fat,
            cholesterol, sodium, fiber,
            total_sugars, added_sugars,
            vitamin_d, calcium, iron, potassium, save = False
        )
        obj.id = data.get("id", obj.id)
        return obj

    def summary(self) -> str:
        """
        Generate a concise string summary of the food item.

        Includes name, subtype, brand, serving information, calories,
        and main macronutrients (protein, carbs, fat).

        Returns:
            str: Summary string.
        """
        base = f"{self.item_name.title()} ({self.sub_type}), Brand: {self.brand.title()}"

        serving = self.data.get("serving_information", {})
        serving_size = serving.get("serving_size", "?")
        serving_unit = serving.get("serving_unit", "")
        servings = serving.get("servings", "?")
        serving_info = f"Serving: {serving_size} {serving_unit}, Servings per container: {servings}"

        macros = self.data.get("nutrition", {}).get("macros", {})
        fats = macros.get("fats", {})
        protein = macros.get("protein", "?")
        carbs = macros.get("carbs", "?")
        fat = fats.get("total_fat", "?")
        kcal_str = f"{self.kcal} kcal" if self.kcal is not None else "No kcal info"

        macro_summary = f"Protein: {protein}g | Carbs: {carbs}g | Fat: {fat}g"

        return f"{base} | {serving_info} | {macro_summary} | {kcal_str}"
    
    def get_macro_ratio(self) -> str:
        """
        Returns the macronutrient ratio (protein, carbs, fat) as percentages of total macro-based kcal.

        Returns:
            tuple: (protein%, carbs%, fat%)
        """
        macros = self.data["nutrition"]["macros"]
        fats = macros["fats"]

        protein_g = macros["protein"]
        carbs_g = macros["carbs"]
        fat_g = fats["total_fat"]

        # Convert grams to kcal
        protein_kcal = protein_g * 4
        carbs_kcal = carbs_g * 4
        fat_kcal = fat_g * 9

        total_macro_kcal = protein_kcal + carbs_kcal + fat_kcal

        if total_macro_kcal == 0:
            return (0.0, 0.0, 0.0)

        # Calculate percentages
        protein_pct = (protein_kcal / total_macro_kcal) * 100
        carbs_pct = (carbs_kcal / total_macro_kcal) * 100
        fat_pct = (fat_kcal / total_macro_kcal) * 100
 
        return f"P:C:F = {round(protein_pct, 1):.1f}%:{round(carbs_pct, 1):.1f}%:{round(fat_pct, 1):.1f}%"
    
    def get_micronutrient_summary(self) -> str:
        """
        Returns a string summarizing key micronutrients.

        Returns:
            str: Micronutrient summary.
        """
        n = self.data["nutrition"]
        return (f"Cholesterol: {n['cholesterol']}mg | Sodium: {n['sodium']}mg | "
                f"Fiber: {n['fiber']}g | Calcium: {n['calcium']}mg | "
                f"Iron: {n['iron']}mg | Potassium: {n['potassium']}mg")