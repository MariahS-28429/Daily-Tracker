import unittest
from unittest.mock import patch, MagicMock

from items import Supplement  # adjust import as needed


class TestSupplement(unittest.TestCase):
    def setUp(self):
        # Patch Registry.register_item to avoid side effects during tests
        patcher_register = patch('summary.Registry.register_item')
        self.mock_register = patcher_register.start()
        self.addCleanup(patcher_register.stop)

    def test_initialization_basic(self):
        supp = Supplement(
            item_name="Vitamin C",
            sub_type="vitamin",
            tags=["immune", "antioxidant"],
            brand="HealthCo",
            serving_size=500,
            serving_unit="mg",
            servings=60,
            active_ingredients=[
                {"name": "Ascorbic Acid", "amount": 500, "unit": "mg"}
            ],
            kcal=0.0
        )
        self.assertEqual(supp.name, "vitamin c")
        self.assertEqual(supp.sub_type, "vitamin")
        self.assertEqual(supp.brand, "healthco")
        self.assertEqual(supp.data["serving_information"]["serving_size"], 500)
        self.assertIn("active_ingredients", supp.data)
        self.assertFalse("nutrition" in supp.data)
        self.mock_register.assert_called_once()

    def test_initialization_with_macros(self):
        supp = Supplement(
            item_name="Protein Powder",
            sub_type="powder",
            tags=["protein", "supplement"],
            brand="MuscleFuel",
            serving_size=30,
            serving_unit="g",
            servings=25,
            active_ingredients=[
                {"name": "Whey Protein", "amount": 24, "unit": "g"}
            ],
            kcal=120,
            protein=24.0,
            carbs=3.0,
            total_fat=1.0
        )
        self.assertIn("nutrition", supp.data)
        self.assertEqual(supp.data["nutrition"]["protein"], 24.0)
        self.assertEqual(supp.data["nutrition"]["kcal"], 120)

    def test_from_dict_minimal(self):
        data = {
            "name": "Zinc Supplement",
            "sub_type": "mineral",
            "tags": ["immune"],
            "brand": "MineralBest",
            "kcal": 0,
            "data": {
                "serving_information": {
                    "serving_size": 15,
                    "serving_unit": "mg",
                    "servings": 100
                },
                "active_ingredients": [
                    {"name": "Zinc", "amount": 15, "unit": "mg"}
                ],
                "notes": "Take with food"
            }
        }
        supp = Supplement.from_dict(data)
        self.assertEqual(supp.name, "zinc supplement")
        self.assertEqual(supp.brand, "mineralbest")
        self.assertEqual(supp.data["serving_information"]["serving_unit"], "mg")
        self.assertEqual(len(supp.data["active_ingredients"]), 1)
        self.assertEqual(supp.data.get("nutrition"), None)
        self.assertEqual(supp.data.get("notes", ""), "")

    def test_from_dict_with_nutrition(self):
        data = {
            "name": "Energy Gel",
            "sub_type": "gel",
            "tags": ["energy", "carb"],
            "brand": "RunFast",
            "data": {
                "serving_information": {
                    "serving_size": 30,
                    "serving_unit": "g",
                    "servings": 1
                },
                "active_ingredients": [
                    {"name": "Carbohydrate", "amount": 25, "unit": "g"}
                ],
                "nutrition": {
                    "kcal": 100,
                    "protein": 0,
                    "carbs": 25,
                    "fat": 0
                }
            }
        }
        supp = Supplement.from_dict(data)
        self.assertEqual(supp.data["nutrition"]["carbs"], 25)
        self.assertEqual(supp.kcal, 100)

    def test_summary_output(self):
        supp = Supplement(
            item_name="Fish Oil",
            sub_type="oil",
            tags=["omega3"],
            brand="HealthyLife",
            serving_size=1000,
            serving_unit="mg",
            servings=120,
            active_ingredients=[
                {"name": "EPA", "amount": 300, "unit": "mg"},
                {"name": "DHA", "amount": 200, "unit": "mg"},
                {"name": "Vitamin E", "amount": 10, "unit": "IU"},
                {"name": "Other", "amount": 5, "unit": "mg"}
            ],
            kcal=9
        )
        summary = supp.summary()
        self.assertIn("Fish Oil", summary)
        self.assertIn("Serving: 1000.0 mg", summary)
        self.assertIn("EPA (300.0mg)", summary)
        self.assertIn("DHA (200.0mg)", summary)
        self.assertIn("Vitamin E (10.0IU)", summary)
        self.assertIn("...", summary)  # because more than max_ingredients by default (3)
        self.assertIn("9.0 kcal", summary)

        summary_custom = supp.summary(max_ingredients=2)
        self.assertNotIn("Vitamin E", summary_custom)
        self.assertIn("...", summary_custom)

    def test_summary_no_ingredients(self):
        supp = Supplement(
            item_name="Empty Supplement",
            sub_type="none",
            tags=[],
            brand="NoBrand",
            serving_size=0,
            serving_unit="unknown",
            servings=0,
            active_ingredients=[],
            kcal=0
        )
        summary = supp.summary()
        self.assertIn("No active ingredients listed", summary)

if __name__ == '__main__':
    unittest.main()
