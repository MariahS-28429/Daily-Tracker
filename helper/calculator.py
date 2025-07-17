from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..items import Item, Recipe, Food

from helper.type import CheckType

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

    def total_amounts_based_on_serving(): # Outputs the total nutritional data for a total of all the servings (as opposed to the default serving size nutrition)
        pass

    # @staticmethod
    # def total_weight(item: Union[Food, Recipe]) -> float: # CHATGPT GENERATED, HAVEN'T CHECKED YET
    #     if isinstance(item, Food):
    #         s = item.data["serving_information"]
    #         return s["serving_size"] * s["servings"]
    #     elif isinstance(item, Recipe):
    #         return sum(NutritionalCalculator.total_weight(i) for i in item.ingredients)
    #     else:
    #         raise TypeError("Item must be a Food or Recipe.")
        
    # @staticmethod
    # def nutrient_density_score(item: Union[Food, Recipe], method: str = "per_kcal") -> float: # CHATGPT GENERATED, HAVEN'T CHECKED YET
    #     """
    #     Calculate a crude nutrient density score for a food or recipe.
        
    #     method: "per_kcal", "per_gram", or "rdi"
    #     """
    #     n = item.data["nutrition"]
    #     nutrients = [n["fiber"], n["iron"], n["calcium"], n["vitamin_d"], n["potassium"]]

    #     if method == "per_kcal":
    #         return sum(nutrients) / item.kcal * 100 if item.kcal else 0

    #     elif method == "per_gram":
    #         weight = NutritionalCalculator.total_weight(item)
    #         return sum(nutrients) / weight if weight else 0

    #     elif method == "rdi":
    #         from .constants import RDI  # Assuming you have a shared constants module
    #         rdi_sum = sum(nutrient / RDI[name] for nutrient, name in zip(nutrients, ["fiber", "iron", "calcium", "vitamin_d", "potassium"]))
    #         return rdi_sum * 100  # Percent of RDI sum

        # else:
        #     raise ValueError(f"Invalid method: {method}")

    @staticmethod
    def kcal_from_macros(item: 'Item', food: bool = True):
        if food:
            return CheckType.is_float((item.data["nutrition"]["macros"]["protein"] * 4 + item.data["nutrition"]["macros"]["fats"]["total_fat"] * 9 + item.data["nutrition"]["macros"]["carbs"] * 4))
        else:
            if item.data["nutrition"]:
                return CheckType.is_float((item.data["nutrition"]["protein"] * 4 + item.data["nutrition"]["fat"] * 9 + item.data["nutrition"]["carbs"] * 4))
            return 0.0

    @classmethod
    def check_nutritional_data(cls, item: 'Item', food: bool = True): 
        if food:
            cls.check_total_fat_to_fats(item)
            cls.check_total_sugar_to_sugars(item)

            # Servings check
            servings = item.data.get("serving_information", {}).get("servings")
            if servings is not None and servings <= 0:
                print("⚠️ Servings must be greater than 0.")

        cls.check_kcal_to_macro(item, food)

    @staticmethod
    def check_total_sugar_to_sugars(item):
        sugars = item["nutrition"]["sugars"]
        total = sugars["total_sugars"]
        added = sugars["added_sugars"]
        
        if total < added:
            print(f"Warning: sugar types do not match total_sugars.")
            print(f"   → Added sugars: {added}")
            print(f"   → Current total sugars: {total}, Calculated: {added}")

            choice = input("Would you like to recalculate (r), edit (e), or keep (k) this information? ").strip().lower()

            if choice == 'r':
                item.data["nutrients"]["sugars"]["total_sugar"] = added

            elif choice == 'e':
                # Prompt user for new values
                new_total = CheckType.is_float(input(f"New total sugars (current: {total}): "))
                new_added = CheckType.is_float(input(f"New added sugars (current: {added}): "))

                # Update fields through structured access
                item.data["nutrition"]["sugars"]["total_sugars"] = new_total
                item.data["nutrition"]["sugars"]["added_sugars"] = new_added

            elif choice == 'k':
                print("Keeping existing kcal value.")
            
            else:
                print("Invalid choice. No changes made.")
    
    @staticmethod
    def check_total_fat_to_fats(item):
        fats = item.data["nutrients"]["macros"]["fats"]
        total_fat = fats["total_fat"]
        sat_fat = fats["saturated_fat"]
        tran_fat = fats["trans_fat"]

        if abs((sat_fat + tran_fat) - total_fat) > 1e-2:
            print(f"Warning: fat types do not match total_fat.")
            print(f"   → Saturated Fat: {sat_fat}g | Trans Fat: {tran_fat}g")
            print(f"   → Current Total Fat: {total_fat}, Calculated: {sat_fat + tran_fat}")

            choice = input("Would you like to recalculate (r), edit (e), or keep (k) this information? ").strip().lower()

            if choice == 'r':
                item.data["nutrients"]["macros"]["fats"]["total_fat"] = sat_fat + tran_fat

            elif choice == 'e':
                # Prompt user for new values
                new_sat = CheckType.is_float(input(f"New saturated fat (current: {sat_fat}): "))
                new_tran = CheckType.is_float(input(f"New trans fat (current: {tran_fat}): "))
                new_fat = CheckType.is_float(input(f"New total fat (current: {total_fat}): "))

                # Update fields through structured access
                item.data["nutrition"]["macros"]["fats"]["total_fat"] = new_fat
                item.data["nutrition"]["macros"]["fats"]["saturated_fat"] = new_sat
                item.data["nutrition"]["macros"]["fats"]["trans_fat"] = new_tran

            elif choice == 'k':
                print("Keeping existing kcal value.")
            
            else:
                print("Invalid choice. No changes made.")

    @staticmethod
    def check_kcal_to_macro(item: 'Item', food: bool = True):
        """
        Checks if an item's kcal matches the calculated value from macros.
        If mismatched, prompts user to recalculate, edit, or keep as-is.

        Args:
            item (Item): The item to validate and optionally update.
        """

        calculated_kcal = NutritionalCalculator.kcal_from_macros(item, food)
        
        if food:
            try:
                macros = item.data["nutrition"]["macros"]
                fats = macros.get("fats", {})
                protein = macros["protein"]
                carbs = macros["carbs"]
                total_fat = fats["total_fat"]
            except (KeyError, TypeError):
                print("Invalid macro structure.")
                return
            
            # All macros 0?
            if protein == 0 and carbs == 0 and total_fat == 0:
                print("⚠️ All macros are 0. Is this complete?")

        else:
            try:
                macros = item.data["nutrition"]
                protein = macros["protein"]
                carbs = macros["carbs"]
                total_fat = macros["fat"]
            except (KeyError, TypeError):
                print("Invalid macro structure.")
                return

        all_values = [protein, carbs, total_fat]
        if any(val < 0 for val in all_values if isinstance(val, (int, float))):
            print("Warning: One or more nutrient values are negative.")

        if abs(calculated_kcal - item.kcal) > 0.1:
            print(f"Warning: Macros do not match kcal.")
            print(f"   → Protein: {protein}g | Carbs: {carbs}g | Fat: {total_fat}g")
            print(f"   → Current kcal: {item.kcal}, Calculated: {calculated_kcal}")

            choice = input("Would you like to recalculate (r), edit (e), or keep (k) this information? ").strip().lower()

            if choice == 'r':
                item.kcal = calculated_kcal

            elif choice == 'e':
                # Prompt user for new values
                new_protein = CheckType.is_float(input(f"New protein (current: {protein}): "))
                new_carbs = CheckType.is_float(input(f"New carbs (current: {carbs}): "))
                new_fat = CheckType.is_float(input(f"New total fat (current: {total_fat}): "))

                # Update fields through structured access
                if food:
                    item.data["nutrition"]["macros"]["protein"] = new_protein
                    item.data["nutrition"]["macros"]["carbs"] = new_carbs
                    item.data["nutrition"]["macros"]["fats"]["total_fat"] = new_fat
                    new_kcal = NutritionalCalculator.kcal_from_macros(item)
                
                else:
                    item.data["nutrition"]["protein"] = new_protein
                    item.data["nutrition"]["carbs"] = new_carbs
                    item.data["nutrition"]["fat"] = new_fat
                    new_kcal = NutritionalCalculator.kcal_from_macros(item, food = False)

                # Update kcal after new macro values
                item.kcal = new_kcal

            elif choice == 'k':
                print("Keeping existing kcal value.")
            
            else:
                print("Invalid choice. No changes made.")

        def compare_to(self, other: "Food") -> str: #CHATGPT MADE PLZ CHECK BEFORE SAYING ITS ALL GOOD
            """
            Compare this food to another food based on key nutritional values.
            Includes directional differences (↑/↓/=/+/-).

            Args:
                other (Food): The other Food instance to compare with.

            Returns:
                str: A formatted string highlighting the differences.
            """
            if not isinstance(other, Food):
                raise TypeError("Can only compare Food with another Food.")

            def format_diff(val1, val2, unit="g"):
                try:
                    diff = val2 - val1
                    if abs(diff) < 0.01:
                        return "(=)"
                    arrow = "↑" if diff > 0 else "↓"
                    return f"({arrow} {diff:+.1f}{unit})"
                except TypeError:
                    return "(n/a)"

            lines = [f"Comparison: {self.item_name.title()} vs {other.item_name.title()}",
                    "Macronutrients (per container):"]

            macros1 = self.data["nutrition"]["macros"]
            macros2 = other.data["nutrition"]["macros"]

            for key in ["protein", "carbs"]:
                val1 = macros1.get(key, 0)
                val2 = macros2.get(key, 0)
                lines.append(f"  {key.title():<15}: {val1}g vs {val2}g  {format_diff(val1, val2)}")

            for key in ["total_fat", "saturated_fat", "trans_fat"]:
                name = key.replace("_", " ").title()
                val1 = macros1["fats"].get(key, 0)
                val2 = macros2["fats"].get(key, 0)
                lines.append(f"  {name:<15}: {val1}g vs {val2}g  {format_diff(val1, val2)}")

            lines.append(f"  {'Calories':<15}: {self.kcal} kcal vs {other.kcal} kcal  {format_diff(self.kcal, other.kcal, ' kcal')}")

            n1 = self.data["nutrition"]
            n2 = other.data["nutrition"]

            # Fiber
            fiber1 = n1.get("fiber", 0)
            fiber2 = n2.get("fiber", 0)
            lines.append(f"  {'Fiber':<15}: {fiber1}g vs {fiber2}g  {format_diff(fiber1, fiber2)}")

            # Total Sugar
            sugar1 = n1["sugars"].get("total_sugars", 0)
            sugar2 = n2["sugars"].get("total_sugars", 0)
            lines.append(f"  {'Total Sugar':<15}: {sugar1}g vs {sugar2}g  {format_diff(sugar1, sugar2)}")

            # Cholesterol (mg)
            chol1 = n1.get("cholesterol", 0)
            chol2 = n2.get("cholesterol", 0)
            lines.append(f"  {'Cholesterol':<15}: {chol1}mg vs {chol2}mg  {format_diff(chol1, chol2, 'mg')}")

            # Sodium (mg)
            sodium1 = n1.get("sodium", 0)
            sodium2 = n2.get("sodium", 0)
            lines.append(f"  {'Sodium':<15}: {sodium1}mg vs {sodium2}mg  {format_diff(sodium1, sodium2, 'mg')}")

            return "\n".join(lines)