from items import Item
from helper import CheckType, NutritionalCalculator
from summary import Registry

class Food(Item):
    """
    Basic data model for a food item with full nutritional information.

    Inherits from the Item class and adds support for serving details, macronutrients, 
    and micronutrients. Validates inputs, stores structured data, and optionally registers 
    the item in the global registry.

    Attributes:
        data (dict): A nested dictionary containing serving information and nutritional values.
    """
    
    KCAL_PER_GRAM_PROTEIN = 4
    KCAL_PER_GRAM_CARBS = 4
    KCAL_PER_GRAM_FAT = 9

    # --- Initialization ---

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
        """
        Initialize a Food item with full nutritional and serving data.

        Validates and structures nutritional information, optionally saving the item to the registry.

        Args:
            item_name (str): Name of the food item.
            sub_type (str): Sub-category of the food.
            kcal (float): Total calories.
            tags (list): List of associated tags or keywords.
            brand (str): Brand name of the food item.
            serving_size (float): Size of a single serving.
            serving_unit (str): Unit for serving size (e.g., g, oz).
            servings (float): Number of servings per container.
            protein (float): Protein content in grams.
            carbs (float): Carbohydrate content in grams.
            total_fat (float): Total fat content in grams.
            saturated_fat (float): Saturated fat content in grams.
            trans_fat (float): Trans fat content in grams.
            cholesterol (float): Cholesterol in milligrams.
            sodium (float): Sodium in milligrams.
            fiber (float): Fiber in grams.
            total_sugars (float): Total sugar content in grams.
            added_sugars (float): Added sugar content in grams.
            vitamin_d (float): Vitamin D content in micrograms.
            calcium (float): Calcium content in milligrams.
            iron (float): Iron content in milligrams.
            potassium (float): Potassium content in milligrams.
            save (bool, optional): Whether to save the item to the registry. Defaults to True.
        """

        NutritionalCalculator.check_nutritional_data(self)

        if CheckType.is_bool(save):
            Registry.register_item(Item.to_registry_dict(self))

    # --- Editing ---
    
    def edit_macros(self, macro_type: str, change: float) -> bool:
        """
        Modify the macronutrient value of a specific macro and update kcal accordingly.

        Automatically recalculates kcal from updated macros and saves the changes to the registry.

        Args:
            macro_type (str): One of 'protein', 'carbs', 'total_fat', 'saturated_fat', or 'trans_fat'.
            change (float): Amount to add (or subtract) from the current macro value.

        Raises:
            ValueError: If the macro type is not recognized.
        """
        
        CheckType.is_string(macro_type)
        CheckType.is_float(change)
        
        macro_type = macro_type.lower()
        macro_paths = {
            "protein": ("nutrition", "macros", "protein"),
            "carbs": ("nutrition", "macros", "carbs"),
            "total_fat": ("nutrition", "macros", "fats", "total_fat"),
            "saturated_fat": ("nutrition", "macros", "fats", "saturated_fat"),
            "trans_fat": ("nutrition", "macros", "fats", "trans_fat"),
        }
        
        if macro_type not in macro_paths:
            raise ValueError("Invalid macro input.")
        d = self.data

        for key in macro_paths[macro_type][:-1]:
            d = d[key]
        d[macro_paths[macro_type][-1]] += CheckType.is_float(change)
        
        self.kcal = NutritionalCalculator.kcal_from_macros(self)

        return Registry.update_item_by_id(self.id, Item.to_registry_dict(self))
    
    # --- Display ---
    
    def summary(self) -> str:
        """
        Generate a formatted summary string for display purposes.

        Includes food name, subtype, brand, serving size, servings per container, 
        total kcal, and main macronutrients.

        Returns:
            str: Summary of the food item in readable format.
        """

        base = f"{self.name.title()} ({self.sub_type}), Brand: {self.brand.title()}"

        serving = self.data.get("serving_information", {})
        serving_size = serving.get("serving_size", "?")
        serving_unit = serving.get("serving_unit", "")
        servings = serving.get("servings", "?")
        serving_info = f"Serving: {serving_size} {serving_unit}, Servings per container: {servings}"

        protein, carbs, fat = self.get_macros()
        kcal_str = f"{self.kcal} kcal" if self.kcal is not None else "No kcal info"

        macro_summary = f"Protein: {protein}g | Carbs: {carbs}g | Fat: {fat}g"

        return f"{base} | {serving_info} | {macro_summary} | {kcal_str}"
    
    def get_macro_ratio(self) -> str:
        """
        Calculate the macro calorie ratio as percentages of total kcal from macros.

        Converts grams of protein, carbs, and fat into kcal and computes 
        each as a percentage of total macro kcal.

        Returns:
            str: Formatted string representing macro ratio (e.g., "P:C:F = 40.0%:40.0%:20.0%").
        """

        protein_g, carbs_g, fat_g = self.get_macros()

        # Convert grams to kcal
        protein_kcal = protein_g * self.KCAL_PER_GRAM_PROTEIN
        carbs_kcal = carbs_g * self.KCAL_PER_GRAM_CARBS
        fat_kcal = fat_g * self.KCAL_PER_GRAM_FAT

        total_macro_kcal = protein_kcal + carbs_kcal + fat_kcal

        if total_macro_kcal == 0:
            return "P:C:F = 0.0%:0.0%:0.0%"

        # Calculate percentages
        protein_pct = (protein_kcal / total_macro_kcal) * 100
        carbs_pct = (carbs_kcal / total_macro_kcal) * 100
        fat_pct = (fat_kcal / total_macro_kcal) * 100
 
        return f"P:C:F = {protein_pct:.1f}%:{carbs_pct:.1f}%:{fat_pct:.1f}%"
    
    def get_micronutrient_summary(self) -> str:
        """
        Generate a summary string of key micronutrients.

        Includes cholesterol, sodium, fiber, calcium, iron, and potassium.

        Returns:
            str: Summary of micronutrient content.
        """

        n = self.data["nutrition"]
        return (f"Cholesterol: {n['cholesterol']}mg | Sodium: {n['sodium']}mg | "
                f"Fiber: {n['fiber']}g | Calcium: {n['calcium']}mg | "
                f"Iron: {n['iron']}mg | Potassium: {n['potassium']}mg")

    # --- Serialization ---     
    
    @classmethod
    def from_dict(cls, data: dict) -> "Food":
        """
        Create a Food instance from a dictionary of saved values.

        Used when loading from a file or registry record. Assumes data is valid and 
        matches the Food structure.

        Args:
            data (dict): Dictionary containing food item data.

        Returns:
            Food: A new Food object reconstructed from the data.
        """

        CheckType.is_dict(data)

        item_name = data["item_name"]
        sub_type = data["sub_type"]
        kcal = data["kcal"]
        tags = data.get("tags", [])
        brand = data["brand"]

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
    
    # --- Helpers ---
    
    def get_macros(self) -> tuple:
        """
        Retrieve the basic macro values: protein, carbs, and total fat.

        Returns:
            tuple: (protein_g, carbs_g, total_fat_g)
        """
        
        macros = self.data.get("nutrition", {}).get("macros", {})
        fats = macros.get("fats", {})
        return macros.get("protein", 0), macros.get("carbs", 0), fats.get("total_fat", 0)