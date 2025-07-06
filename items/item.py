import csv, json, sys, re, os
from typing import List, Dict, Any


class Item():
    """
    Abstract base class for all items in the nutritional planner.

    Handles shared attributes such as name, kcal, tags, and methods for serialization.
    Subclasses like Food, Recipe, etc., inherit from this to ensure a consistent structure.

    Used by:
    - Subclasses (e.g., Food, Recipe, Workout)
    - Registry (for saving/loading data)
    - Calculator and DayLog (via methods like to_registry_dict)
    """
    
    """
    Attributes:
    - name (str): Lowercase name of the item
    - item_type (str): 'food', 'recipe', etc.
    - sub_type (str): 'ingredient', 'meal', etc.
    - kcal (float): Caloric value
    - brand (str): Brand name in lowercase
    - id (str): Unique identifier generated
    - tags (list): List of associated tags
    - time (float): Optional time-related metric (e.g. cooking time)
    - data (dict): Extra metadata
    - makeup (list): Used in recipes to store ingredient composition
    """
    
    def __init__(self, item_name: str, item_type: str, sub_type: str, kcal: float, tags: List[str], brand: str):
        """
        Initialize all attributes for an item. Autosaves the item to the registry upon initialization.

        Input: ('apple', 'food', 'non-ingredient', 95.0, ['fruit'], 'Walmart'), etc.
        """

        # Attributes that are brought in. Will always be defined in every child class
        self.name = CheckType.is_string(item_name).lower()
        self.item_type = CheckType.is_string(item_type).lower()
        self.sub_type = CheckType.is_string(sub_type).lower()
        self.brand = CheckType.is_string(brand).lower()
        self.id = self.id_gen()
        self.tags = CheckType.is_list(tags)
        
        # Attributes are aren't brought in. Only used in some child classes
        self.time = 0.0
        self.data = {}
        self.makeup = []
        self.kcal = 0.0

    def id_gen(self):
        """
        Generate the lowest available unique ID for this item based on its type prefix.

        Ex: 'f001', 'r002', 'w003', 's004', etc.
        """

        prefix = self.item_type[0]
        summary = SummaryIndex.load_index()
        
        # generates a list of used id's in the class
        used_numbers = []
        for item in summary:
            if item['id'].startswith(prefix):
                num_part = item['id'][1:]
                if num_part.isdigit():
                    used_numbers.append(int(num_part))
        
        # check ths list of used id's to make sure none are missing. If one is, it will make the gap the new ID, if not it will create a new ID
        used_numbers.sort()
        next_num = 1
        for num in used_numbers:
            if num == next_num:
                next_num += 1
            else:
                break
        
        return f"{prefix}{next_num:03d}"
    
    def to_registry_dict(self):
        """
        Return a full dict of the item for serialization to registry.
        """
        
        return {
            'id': self.id,
            'name': self.name,
            'item_type': self.item_type,
            'sub_type': self.sub_type,
            'brand': self.brand,
            'kcal': self.kcal,
            'time': self.time,
            'data': self.data,
            'tags': self.tags,
            'makeup': self.makeup
        }

    def update_field(self, field_name: str, new_value):
        """
        Lets the user update a field for an already existing item (if the item has been made in the same code and doesn't only exist in the registry)

        Input: Item.update_field(item, "name", "green apple")
        Output: True
        """
        # checks that the field_name is valid
        if field_name not in vars(self).keys():
            print(f"'{field_name}' is not a valid field name.")
            return False
        
        # updates id if the item_type is changed and updates all dependents to change to the new id
        if field_name == 'item_type':
            new_id = self.id_gen()
            self.auto_update_dependents(new_id)
            self.id = new_id
        
        elif field_name == 'id':
            self.auto_update_dependents(new_value)

        setattr(self, field_name, new_value)

        if field_name == 'data' or field_name == 'kcal':
            self.auto_update_dependents()

        ItemRegistry.register_item(self.to_registry_dict())
        return True        

    def auto_update_dependents(self, change = None):
        """
        Notify the registry to update all items (recipes/daylogs) that reference this item.
        """
        # changes the item's id in its depenents for future reference
        if change:
            dependents = ItemRegistry.get_items_using(self.id)
            registry = ItemRegistry.load_registry()
            updated = False

            if dependents:
                for dependent in dependents:
                    makeup = dependent.get("makeup")
                    makeup = [change if x == self.id else x for x in makeup]
                    # Update the matching row in the registry
                    for row in registry:
                        if row["id"] == dependent["id"]:
                            row["makeup"] = makeup
                            updated = True
                            break
            
            if updated:
                ItemRegistry.save_registry(registry)
        
        else:
            ItemRegistry.update_dependents(self.id)

    def __str__(self):
        return (f"{self.name.title()} [{self.item_type}/{self.sub_type}] - "
            f"{self.kcal} kcal - Brand: {self.brand.title()}")

    def __repr__(self):
        return (f"Item(name={self.name!r}, item_type={self.item_type!r}, "
            f"sub_type={self.sub_type!r}, kcal={self.kcal!r}, brand={self.brand!r})")

    def delete_tag(self, tag):
        if tag in self.tags:
            self.tags.remove()

            registry = ItemRegistry.load_registry()
            for row in registry:
                if row['id'] == self.id:
                    if tag in row["tags"]:
                        row["tags"].remove(tag)
                        ItemRegistry.save_registry(registry)
                    break

    def add_tag(self, tag):
        if not tag in self.tags:
            self.tags.append(tag)

            registry = ItemRegistry.load_registry()
            for row in registry:
                if row['id'] == self.id:
                    if not tag in row['tags']:
                        row["tags"].append(tag)
                        ItemRegistry.save_registry(registry)
                    break

    def __eq__(self, other):
        return isinstance(other, Item) and self.to_registry_dict() == other.to_registry_dict()