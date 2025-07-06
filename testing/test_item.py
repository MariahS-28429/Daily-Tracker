from items import Item

import unittest
from unittest.mock import patch, MagicMock

class TestItem(unittest.TestCase):
    def setUp(self):
        # Patch Index.load_index and Registry methods
        patcher_index = patch('summary.Index.load_index', return_value = [])
        patcher_update = patch('summary.Registry.update_item_by_id')
        patcher_get_using = patch('summary.Registry.get_items_using', return_value=[])
        patcher_load_registry = patch('summary.Registry.load_registry', return_value=[])
        patcher_save_registry = patch('summary.Registry.save_registry')

        self.mock_load_index = patcher_index.start()
        self.mock_update = patcher_update.start()
        self.mock_get_items_using = patcher_get_using.start()
        self.mock_load_registry = patcher_load_registry.start()
        self.mock_save_registry = patcher_save_registry.start()

        self.addCleanup(patcher_index.stop)
        self.addCleanup(patcher_update.stop)
        self.addCleanup(patcher_get_using.stop)
        self.addCleanup(patcher_load_registry.stop)
        self.addCleanup(patcher_save_registry.stop)

    def test_initialization(self):
        item = Item('Apple', 'Food', 'Non-Ingredient', 95.0, ['fruit'], 'Walmart')
        self.assertEqual(item.name, 'apple')
        self.assertEqual(item.item_type, 'food')
        self.assertEqual(item.sub_type, 'non-ingredient')
        self.assertEqual(item.brand, 'walmart')
        self.assertEqual(item.kcal, 95.0)  # Should match the passed kcal, not 0.0
        self.assertEqual(item.tags, ['fruit'])
        self.assertTrue(item.id.startswith('f'))

    def test_id_gen_creates_next_id(self):
        # simulate existing ids f001, f002, f004
        self.mock_load_index.return_value = [
            {'id': 'f001'}, {'id': 'f002'}, {'id': 'f004'}
        ]
        item = Item('Banana', 'Food', 'Non-Ingredient', 105, [], 'Dole')
        # next id should be f003 (gap filled)
        self.assertEqual(item.id, 'f003')

    def test_to_registry_dict(self):
        item = Item('Carrot', 'Food', 'Ingredient', 25, ['vegetable'], 'Local')
        d = item.to_registry_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['name'], 'carrot')
        self.assertEqual(d['item_type'], 'food')
        self.assertEqual(d['tags'], ['vegetable'])

    def test_update_field_valid_and_invalid(self):
        item = Item('Egg', 'Food', 'Ingredient', 70, [], 'Farm')
        result_invalid = item.update_field('non_existent_field', 'value')
        self.assertFalse(result_invalid)

        # Updating name works and converts to lowercase
        result = item.update_field('name', 'Chicken Egg')
        self.assertTrue(result)
        self.assertEqual(item.name, 'chicken egg')  # lowercased


    def test_update_field_item_type_changes_id(self):
        # Simulate existing IDs in both 'f' and 's' categories
        self.mock_load_index.return_value = [
            {'id': 'f001'}, {'id': 'f002'}, {'id': 's001'}
        ]

        item = Item('Milk', 'Food', 'Drink', 150, [], 'BrandA')  # f003

        with patch.object(item, 'auto_update_dependents') as mock_auto_update:
            old_id = item.id  # f003
            item.update_field('item_type', 'supplement')  # triggers s002
            new_id = item.id

            self.assertNotEqual(old_id, new_id)
            self.assertTrue(new_id.startswith('s'))
            mock_auto_update.assert_called_with(new_id)
            
            self.mock_update.assert_called_once()
            self.assertEqual(self.mock_update.call_args[0][1]['item_type'], 'supplement')


    def test_auto_update_dependents_with_change(self):
        item = Item('Test', 'Food', 'Ingredient', 50, [], 'Brand')
        with patch('summary.Registry.get_items_using') as mock_get_items, \
             patch('summary.Registry.load_registry') as mock_load_reg, \
             patch('summary.Registry.save_registry') as mock_save_reg:

            mock_get_items.return_value = [{'id': 'r001', 'makeup': [item.id]}]
            mock_load_reg.return_value = [{'id': 'r001', 'makeup': [item.id]}]

            item.auto_update_dependents(change='f999')

            mock_save_reg.assert_called_once()

    def test_add_tag_and_delete_tag(self):
        item = Item('Orange', 'Food', 'Fruit', 60, ['citrus'], 'BrandX')

        # Add new tag
        item.add_tag('sweet')
        self.assertIn('sweet', item.tags)

        # Add duplicate tag, should not add again
        item.add_tag('sweet')
        self.assertEqual(item.tags.count('sweet'), 1)

        # Delete tag
        item.delete_tag('citrus')
        self.assertNotIn('citrus', item.tags)

        # Delete non-existing tag does nothing
        item.delete_tag('nonexistent')

    def test_str_and_repr(self):
        item = Item('Peach', 'Food', 'Fruit', 40, [], 'BrandY')
        self.assertIn('Peach', str(item))
        self.assertIn('Item(', repr(item))

    def test_eq(self):
        item1 = Item('Pear', 'Food', 'Fruit', 50, [], 'BrandZ')
        item2 = Item('Pear', 'Food', 'Fruit', 50, [], 'BrandZ')
        self.assertEqual(item1, item2)
        item2.name = 'Apple'
        self.assertNotEqual(item1, item2)

    def test_from_dict_basic(self):
        data = {
            "name": "Almond",
            "item_type": "food",
            "sub_type": "nut",
            "tags": ["healthy", "snack"],
            "brand": "Nature's Best",
            "kcal": 160
        }
        item = Item.from_dict(data)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.name, "almond")
        self.assertEqual(item.item_type, "food")
        self.assertEqual(item.sub_type, "nut")
        self.assertEqual(item.tags, ["healthy", "snack"])
        self.assertEqual(item.brand, "nature's best")
        self.assertEqual(item.kcal, 160)

    def test_from_dict_missing_fields(self):
        data = {"name": "Unknown"}
        item = Item.from_dict(data)
        self.assertEqual(item.name, "unknown")
        self.assertEqual(item.item_type, "unknown")  # fallback default
        self.assertEqual(item.sub_type, "unknown")
        self.assertEqual(item.tags, [])
        self.assertEqual(item.brand, "unknown")
        self.assertEqual(item.kcal, 0.0)

    def test_has_tag(self):
        item = Item('Berry', 'Food', 'Fruit', 30, ['fresh', 'sweet'], 'BrandB')
        self.assertTrue(item.has_tag('fresh'))
        self.assertTrue(item.has_tag('FRESH'))  # case-insensitive check
        self.assertFalse(item.has_tag('sour'))
    
    def test_summary_fallback(self):
        item = Item("TestItem", "food", "basic", 100, ["tag1", "tag2"], "GenericBrand")
        summary = item.summary()
        self.assertIn("Testitem", summary)
        self.assertIn("Genericbrand", summary)
        self.assertIn("100 kcal", summary)
        self.assertIn("tag1", summary)

    def test_add_to_makeup(self):
        item = Item("Trail Mix", "Recipe", "Snack", 300, [], "Generic")

        with patch('summary.Registry.update_item_by_id') as mock_update_item, \
             patch('summary.Registry.update_dependents') as mock_update_dependents:
            
            # First time adding
            result_1 = item.add_to_makeup("f001")
            self.assertTrue(result_1)
            self.assertIn({'id': 'f001'}, item.makeup)
            mock_update_item.assert_called_once_with(item.id, item.to_registry_dict())
            mock_update_dependents.assert_called_once_with(item.id)

            # Reset mocks for next check
            mock_update_item.reset_mock()
            mock_update_dependents.reset_mock()

            # Attempt duplicate
            result_2 = item.add_to_makeup("f001")
            self.assertFalse(result_2)
            self.assertEqual(item.makeup.count({'id': 'f001'}), 1)
            mock_update_item.assert_not_called()
            mock_update_dependents.assert_not_called()

if __name__ == '__main__':
    unittest.main()