import unittest
from unittest.mock import patch, MagicMock
from items import Food  # Assuming your class is in food.py

class TestFood(unittest.TestCase):
    def setUp(self):
        # Patch Registry and NutritionalCalculator methods
        self.patcher_registry = patch('summary.Registry.register_item')
        self.patcher_update = patch('summary.Registry.update_item_by_id')
        self.patcher_calc = patch('helper.NutritionalCalculator.check_nutritional_data')
        self.patcher_to_registry_dict = patch('items.Item.to_registry_dict', return_value={})

        self.mock_register = self.patcher_registry.start()
        self.mock_update = self.patcher_update.start()
        self.mock_calc = self.patcher_calc.start()
        self.mock_to_registry_dict = self.patcher_to_registry_dict.start()

        self.addCleanup(self.patcher_registry.stop)
        self.addCleanup(self.patcher_update.stop)
        self.addCleanup(self.patcher_calc.stop)
        self.addCleanup(self.patcher_to_registry_dict.stop)

    def test_initialization_creates_correct_data_structure(self):
        food = Food(
            item_name="Oatmeal", sub_type="grain", kcal=150, tags=["breakfast"], brand="Quaker",
            serving_size=40, serving_unit="g", servings=1,
            protein=5, carbs=27, total_fat=3, saturated_fat=0.5, trans_fat=0,
            cholesterol=0, sodium=0, fiber=4,
            total_sugars=1, added_sugars=0,
            vitamin_d=0, calcium=20, iron=1.5, potassium=150
        )
        self.assertEqual(food.name, "oatmeal")
        self.assertEqual(food.sub_type, "grain")
        self.assertEqual(food.data["nutrition"]["macros"]["protein"], 5.0)
        self.assertEqual(food.data["serving_information"]["serving_unit"], "g")
        self.mock_calc.assert_called_once()

    def test_edit_macros_valid(self):
        food = Food(
            "Egg", "protein", 78, [], "Generic", 50, "g", 1,
            6, 1, 5, 1.5, 0, 187, 62, 0,
            0, 0, 1.1, 28, 0.9, 63
        )
        food.edit_macros("protein", 2)
        self.assertEqual(food.data["nutrition"]["macros"]["protein"], 8.0)

        food.edit_macros("saturated_fat", 0.5)
        self.assertEqual(food.data["nutrition"]["macros"]["fats"]["saturated_fat"], 2.0)

    def test_edit_macros_invalid_type(self):
        food = Food(
            "Milk", "dairy", 120, [], "FarmCo", 240, "ml", 1,
            8, 12, 5, 3, 0, 20, 100, 0,
            11, 10, 2.5, 300, 0.5, 400
        )
        with self.assertRaises(ValueError):
            food.edit_macros("invalid_macro", 10)

    def test_summary_output(self):
        food = Food(
            "Toast", "bread", 80, [], "Bakery", 30, "g", 2,
            2, 15, 1, 0.5, 0, 0, 130, 1,
            2, 1, 0, 50, 0.5, 50
        )
        summary = food.summary()
        self.assertIn("Toast", summary)
        self.assertIn("Serving:", summary)
        self.assertIn("Protein:", summary)

    def test_macro_ratio_calculation(self):
        food = Food(
            "Avocado", "fruit", 160, [], "Hass", 100, "g", 1,
            2, 9, 15, 2, 0, 0, 7, 7,
            0, 0, 0, 10, 1, 500
        )
        ratio = food.get_macro_ratio()
        self.assertTrue(ratio.startswith("P:C:F ="))

    def test_micronutrient_summary(self):
        food = Food(
            "Kale", "vegetable", 33, [], "OrganicFarm", 100, "g", 1,
            3, 6, 0.5, 0.1, 0, 0, 25, 2,
            1, 0, 1, 100, 1, 200
        )
        summary = food.get_micronutrient_summary()
        self.assertIn("Calcium", summary)
        self.assertIn("Iron", summary)

    def test_from_dict_creates_valid_instance(self):
        data = {
            "item_name": "Yogurt",
            "sub_type": "dairy",
            "kcal": 100,
            "tags": ["snack"],
            "brand": "GreekCo",
            "data": {
                "serving_information": {
                    "serving_size": 150,
                    "serving_unit": "g",
                    "servings": 1
                },
                "nutrition": {
                    "macros": {
                        "protein": 10,
                        "carbs": 8,
                        "fats": {
                            "total_fat": 3,
                            "saturated_fat": 2,
                            "trans_fat": 0
                        }
                    },
                    "cholesterol": 5,
                    "sodium": 50,
                    "fiber": 0,
                    "sugars": {
                        "total_sugars": 7,
                        "added_sugars": 5
                    },
                    "vitamin_d": 1.2,
                    "calcium": 150,
                    "iron": 0.1,
                    "potassium": 200
                }
            }
        }

        food = Food.from_dict(data)
        self.assertIsInstance(food, Food)
        self.assertEqual(food.data["nutrition"]["macros"]["protein"], 10.0)
        self.assertEqual(food.data["nutrition"]["sodium"], 50.0)

    def test_get_macros(self):
        food = Food(
            "Tuna", "fish", 100, [], "OceanBrand", 100, "g", 1,
            20, 0, 5, 1, 0, 50, 200, 0,
            0, 0, 0, 10, 0.3, 250
        )
        protein, carbs, fat = food.get_macros()
        self.assertEqual(protein, 20)
        self.assertEqual(carbs, 0)
        self.assertEqual(fat, 5)

if __name__ == "__main__":
    unittest.main()
