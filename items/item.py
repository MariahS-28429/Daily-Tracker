from typing import List, Dict

from helper.type import CheckType
from summary import Index, Registry

class Item():
    """
    Abstract base class for all items in the day log.

    Represents a generalized data structure for nutrition-related entities like foods,
    recipes, workouts, and supplements.

    Attributes:
        name (str): Normalized lowercase name of the item.
        item_type (str): Category ('food', 'recipe', etc.).
        sub_type (str): Subcategory ('ingredient', 'meal', etc.).
        brand (str): Brand name in lowercase.
        id (str): Unique ID generated using item_type.
        kcal (float): Caloric value, default is 0.0 unless overridden.
        tags (list): List of lowercase tag strings.
        time (float): Optional time value, such as cooking or workout time.
        data (dict): Optional metadata dictionary.
        makeup (list): Used by composite items (like recipes) to store sub-item IDs.
    """
    
    # --- Initialization and ID Management ---

    def __init__(self, item_name: str, item_type: str, sub_type: str, kcal: float, tags: List[str], brand: str):
        """
        Initialize all attributes for an item. Autosaves the item to the registry upon initialization.

        Args:
            item_name (str): Name of the item.
            item_type (str): Type/category of the item.
            sub_type (str): Subcategory of the item.
            kcal (float): Calorie count.
            tags (List[str]): List of tags associated with the item.
            brand (str): Brand name.
        """

        # Attributes that are brought in. Will always be defined in every child class
        self.name = CheckType.is_string(item_name).lower()
        self.item_type = CheckType.is_string(item_type).lower()
        self.sub_type = CheckType.is_string(sub_type).lower()
        self.brand = CheckType.is_string(brand).lower()
        self.id = self.id_gen()
        self.tags = CheckType.is_list(tags)
        self.kcal = kcal
        
        # Attributes are aren't brought in. Only used in some child classes
        self.time = 0.0
        self.data = {}
        self.makeup = []

    def id_gen(self) -> str:
        """
        Generate the lowest available unique ID for this item based on its type prefix.

        Returns:
            str: A unique ID string like 'f001', 'r002', etc.
        """

        prefix = self.item_type[0]
        summary = Index.load_index()
        
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
    
    # --- Serialization ---

    def to_registry_dict(self) -> Dict:
        """
        Serialize the item into a dictionary for registry storage.

        Returns:
            dict: Dictionary representation of the item.
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

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """
        Basic fallback method to create an Item instance from a dictionary.

        Child classes should override this method to handle their specific fields.

        Args:
            data (dict): Dictionary containing item data.

        Returns:
            Item: An instance of Item with available basic fields set.
        """
        item_name = data.get("name", "unknown")
        item_type = data.get("item_type", "unknown")
        sub_type = data.get("sub_type", "unknown")
        tags = data.get("tags", [])
        brand = data.get("brand", "unknown")
        kcal = data.get("kcal", 0.0)

        # Create an instance with minimal data, ignoring extra fields.
        # This won't include specialized attributes in child classes.
        return cls(
            item_name=item_name,
            item_type=item_type,
            sub_type=sub_type,
            kcal=kcal,
            tags=tags,
            brand=brand
        )
    
    # --- Field Updates and Dependent Updates ---
    
    def update_field(self, field_name: str, new_value) -> bool:
        """
        Update an attribute of the item and notify dependents if necessary.

        Args:
            field_name (str): The name of the field to update.
            new_value: The new value to assign.

        Returns:
            bool: True if updated successfully, False if invalid field.
        """

        if field_name not in vars(self):
            print(f"'{field_name}' is not a valid field name.")
            return False

        new_value = new_value.lower() if isinstance(new_value, str) else new_value

        if field_name == 'item_type':
            self.item_type = new_value
            new_id = self.id_gen()
            self.auto_update_dependents(new_id)
            self.id = new_id

        elif field_name == 'id':
            self.auto_update_dependents(new_value)
            self.id = new_value

        else:
            setattr(self, field_name, new_value)
            if field_name in {'data', 'kcal'}:
                self.auto_update_dependents()

        Registry.register_item(self.to_registry_dict())
        return True

    def auto_update_dependents(self, change: str = None) -> bool:
        """
        Notify the Registry to update all items (recipes, daylogs, etc.) that reference this item.

        Args:
            change (str, optional): New ID if this item’s ID has changed.
        """

        # changes the item's id in its depenents for future reference
        if change:
            dependents = Registry.get_items_using(self.id)
            registry = Registry.load_registry()
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
                Registry.save_registry(registry)
                return True
            
            return False
        
        else:
            Registry.update_dependents(self.id)
            return True

    # --- Tag Management ---
    
    def add_tag(self, tag) -> bool:
        """
        Add a tag to this item and update the registry if changed.

        Args:
            tag (str): Tag to add.
        """

        if not tag in self.tags:
            self.tags.append(tag)

            registry = Registry.load_registry()
            for row in registry:
                if row['id'] == self.id:
                    if not tag in row['tags']:
                        row["tags"].append(tag)
                        Registry.save_registry(registry)
                        return True
                    break
        
        return False

    def delete_tag(self, tag) -> bool:
        """
        Remove a tag from this item and update the registry if changed.

        Args:
            tag (str): Tag to remove.
        """
        
        if tag in self.tags:
            self.tags.remove(tag)

            registry = Registry.load_registry()
            for row in registry:
                if row['id'] == self.id:
                    if tag in row["tags"]:
                        row["tags"].remove(tag)
                        Registry.save_registry(registry)
                        return True
                    break
        
        return False
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the item has a specific tag.

        Args:
            tag (str): Tag to check for.

        Returns:
            bool: True if tag exists, False otherwise.
        """

        return tag.lower() in self.tags
    
    # --- Display and Reporting ---

    def summary(self) -> str:
        """
        Fallback summary method for base Item class.
        Child classes should override this for specific formats.

        Returns:
            str: Basic summary string.
        """

        return (
            f"{self.name.title()} ({self.item_type}/{self.sub_type}) | "
            f"Brand: {self.brand.title()} | "
            f"{self.kcal} kcal | Tags: {', '.join(self.tags) if self.tags else 'No tags'}"
        )
    
    # --- Magic Methods ---
    
    def __str__(self) -> str:
        """
        String representation for user-friendly display.
        """
        
        return (f"{self.name.title()} [{self.item_type}/{self.sub_type}] - "
            f"{self.kcal} kcal - Brand: {self.brand.title()}")

    def __repr__(self) -> str:
        """
        Official string representation useful for debugging.
        """
        
        return (f"Item(name={self.name!r}, item_type={self.item_type!r}, "
            f"sub_type={self.sub_type!r}, kcal={self.kcal!r}, brand={self.brand!r})")
 
    def __eq__(self, other) -> bool:
        """
        Equality check based on core attributes.

        Args:
            other (Item): Another item to compare.

        Returns:
            bool: True if equivalent, False otherwise.
        """
        
        if not isinstance(other, Item):
            return False
        return (
            self.name == other.name and
            self.item_type == other.item_type and
            self.sub_type == other.sub_type and
            self.kcal == other.kcal and
            self.brand == other.brand and
            self.tags == other.tags
        )

if __name__ == "__main__":
    pass