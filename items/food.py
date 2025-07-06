from items import Item
from helper import CheckType
from summary import Registry

def filler():
    i=0
    pass

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
                 vitamin_d: float, calcium: float, iron: float, potassium: float):  
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
        
        filler() #This will be where it recaluclates kcal, if needed

        filler() #ItemRegistry.update_item(self.item_name, Item.to_registry_dict(self)) ###I need to make update_item method