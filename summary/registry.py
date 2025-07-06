from typing import List, TYPE_CHECKING, Optional
import csv, json

if TYPE_CHECKING:
    from items import Item, Food, Recipe, Workout, Supplement

from .constants import REGISTRY_HEADERS, INDEX_HEADERS

class Registry():
    """
    Stores and manages all registered items.
    Automatically updates index and dependents when items change.
    """

    headers = REGISTRY_HEADERS
    registry_file = "item_registry.csv"
    _cache = None

    @classmethod
    def register_item(cls, row) -> bool:
        registry = cls.load_registry()

        registry.append(row)

        return cls.save_registry(registry)
    
    @classmethod
    def load_registry(cls) -> List[dict]:
        if cls._cache is not None:
            return cls._cache
        
        registry = []
        with open(cls.registry_file, 'r', newline='', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                cleaned = cls._clean_row(row)
                registry.append(cleaned)
        
        cls._cache = registry
        return registry
    
    @classmethod
    def save_registry(cls, registry: List[dict]) -> bool:
        """
        Updates / saves the registry with the new and updated registry given to it. 
        Codes items with json so they can be converted back to python objects.

        Input: [{'id': 't001', 'name': 'testing', 'item_type': 'testing', 'sub_type': '1', 'brand': '3', 'kcal': 2.0, 'time': 0.0, 'data': {}, 'makeup': [], 'tags': []}, 
        {'id': 't002', 'name': 'testing', 'item_type': 'testing', 'sub_type': '1', 'brand': '3', 'kcal': 2.0, 'time': 0.0, 'data': {}, 'makeup': [], 'tags': []}]
        """

        with open(cls.registry_file, 'w', newline='', encoding='utf-8') as f_out:
            
            # if the registry is empty, don't save it.
            if not registry:
                return False
            
            writer = csv.DictWriter(f_out, fieldnames=cls.headers)
            writer.writeheader()

            # codes some attributes to json for later conversions
            for item in registry:
                row = item.copy()
                for field in ['data', 'makeup', 'tags']:
                    row[field] = json.dumps(row.get(field, {} if field == 'data' else []))
                writer.writerow(row)
        
        cls._cache = None
        Index.save_index()    

        return True
    
    @classmethod
    def get_item_object(cls, id_or_name) -> Optional['Item']:
        item_id = cls.resolve_id(id_or_name)
        if not item_id:
            return None
        
        item_dict = cls.get_item_dict(item_id)
        if not item_dict:
            return None

        return cls.from_dict(item_dict)
    
    @classmethod
    def resolve_id_by_name(cls, name: str) -> str | None:
        """
        Find the item ID based on a (possibly non-unique) item name.
        Returns the selected item ID, or None if not found/aborted.
        """

        matches = Index.search_name(name)

        if not matches:
            print(f"No items found with name matching '{name}'.")
            return None

        if len(matches) == 1:
            return matches[0]['id']

        print(f"\nMultiple items found matching '{name}':")
        for i, item in enumerate(matches, 1):
            print(f"{i}. [{item['id']}] {item['brand']} {item['name']}")

        try:
            choice = int(input("Enter the number of the item: "))
            if 1 <= choice <= len(matches):
                return matches[choice - 1]['id']
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

        return None
    
    @staticmethod
    def confirm_deletion(item_summary: str) -> bool:
        print(f"\nYou are about to delete the following item:")
        print(item_summary)
        confirm = input("Are you sure you want to delete this item? (y/n): ").strip().lower()
        return confirm in ('y', 'yes')

    @classmethod
    def delete_item(cls, item_name: str) -> bool:
        id = cls.resolve_id_by_name(item_name)
        if not id:
            return False
        item_dict = cls.get_item_dict(id)
        if not item_dict:
            return False
        item = cls.from_dict(item_dict)

        if not cls.confirm_deletion(item.summary()):
            print("Deletion cancelled.")
            return False

        registry = cls.load_registry()
        updated_registry = [i for i in registry if i['id'] != id]
        if len(updated_registry) == len(registry):
            print(f"No item found with ID '{id}'.")
            return False

        cls.save_registry(updated_registry)
        return True
  
    @classmethod
    def update_field(cls, item_name: str, field_name: str, new_value) -> bool:
        """
        Let's a user change fields for items that already exist in the registry file.

        Returns True if a change was made, False if not.

        Input: ('testing', 'name', 'test')
        Output: True
        """
        return cls.call_method(item_name, 'Item', "update_field", field_name, new_value)
    
    @classmethod
    def from_dict(cls, item_dict) -> 'Item':
        item_type = item_dict.get("item_type")

        item_classes = {
            "food": Food,
            "recipe": Recipe,
            "workout": Workout,
            "supplement": Supplement
        }

        klass = item_classes.get(item_type.lower())
        if not klass:
            raise ValueError(f"Unknown item type: {item_type}")

        return klass.from_dict(item_dict)
    
    @classmethod
    def call_method(cls, name: str, method_class: type, method: str, *args) -> any:
        item_id = cls.resolve_id_by_name(name)
        registry = cls.load_registry()

        for row in registry:
            if row["id"] == item_id:
                item = cls.instantiate_item(row)
                result = getattr(method_class, method)(item, *args)
                cls.update_item_by_id(item.id, item.to_registry_dict())  # <-- add this
                return result

        raise ValueError(f"Item with name '{name}' not found in registry.")

    @classmethod
    def update_dependents(cls, item_id) -> bool:
        """
        Recalculates and updates any items that include this item_id in their makeup.
        """

        dependents = cls.get_items_using(item_id)
        if not dependents:
            return False

        for dependent in dependents:
            obj = cls.instantiate_item(dependent)
            obj.recalculate()
            cls.update_item_by_id(obj.id, obj.to_registry_dict())
        
        return True
 
    @classmethod
    def get_items_using(cls, item_id: str) -> List[dict]:
        """
        Returns a list of all items that include the given item_id in their makeup.

        Input: item_id like 'f001', 'r002', etc.
        Output: List of item dicts that reference this item in their makeup.
        """

        registry = cls.load_registry()
        items_using = []

        for item in registry:
            makeup = item.get('makeup', [])
            # Check if makeup is a list and if any part has matching 'id'
            if isinstance(makeup, list) and any(part.get('id') == item_id for part in makeup):
                items_using.append(item)

        return items_using
    
    @classmethod
    def call_tags(cls) -> set:
        return cls.collect_unique_field_values("tags")
    
    @classmethod
    def call_subtype(cls) -> set:
        return cls.collect_unique_field_values("subtype")

    @classmethod
    def update_item_by_id(cls, item_id: str, new_dict: dict) -> bool:
        """
        Replaces the registry row with the given ID using new_dict.

        Returns True if updated successfully, False if item not found.
        """
        registry = cls.load_registry()
        updated = False

        for i, row in enumerate(registry):
            if row['id'] == item_id:
                registry[i] = new_dict
                updated = True
                break

        if updated:
            cls.save_registry(registry)
        return updated

    @classmethod
    def add_to_makeup(cls, target_item_name: str, component_item_name: str) -> bool:
        """
        Adds a component item to the makeup of a target item.

        Args:
            target_item_name (str): The name or ID of the item being modified.
            component_item_name (str): The name or ID of the item to add to its makeup.

        Returns:
            bool: True if added, False otherwise.
        """
        # Step 1: Get target item object (like a recipe or workout)
        target_obj = cls.get_item_object(target_item_name)
        if target_obj is None:
            print(f"Could not find target item '{target_item_name}'.")
            return False

        # Step 2: Get component ID (by name or ID)
        component_id = cls.resolve_id(component_item_name)
        if component_id is None:
            print(f"Could not find component item '{component_item_name}'.")
            return False

        # Step 3: Add to target’s makeup
        return target_obj.add_to_makeup(component_id)

    @classmethod
    def collect_unique_field_values(cls, field_name: str) -> set:
        registry = cls.load_registry()
        values = set()
        for item in registry:
            value = item.get(field_name)
            if isinstance(value, list):
                values.update(value)
            elif value is not None:
                values.add(value)
        return values

    @staticmethod
    def _clean_row(row: dict) -> dict:
        cleaned = {}
        for key, value in row.items():
            value = value.strip()
            if key in ['data', 'makeup', 'tags']:
                try:
                    cleaned[key] = json.loads(value) if value else ({} if key == 'data' else [])
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse JSON for key '{key}' in row: {row}")
                    cleaned[key] = {} if key == 'data' else []
            elif key in ['kcal', 'time']:
                try:
                    cleaned[key] = float(value)
                except ValueError:
                    cleaned[key] = 0.0
            else:
                cleaned[key] = value
        return cleaned

    @classmethod
    def filter_registry(cls, filter_func) -> List[dict]:
        registry = cls.load_registry()
        return [item for item in registry if filter_func(item)]

    @classmethod
    def get_item_dict(cls, id) -> Optional[List[dict]]:
        filtered = cls.filter_registry(lambda item: item['id'] == id)
        if filtered:
            return filtered[0]
        print(f"Warning: No item found in registry with id '{id}'")
        return None

    @classmethod
    def get_all_by_type(cls, item_type: str) -> List[dict]:
        item_type = item_type.lower()
        return cls.filter_registry(lambda item: item.get('item_type', '').lower() == item_type)

    @classmethod
    def resolve_id(cls, id_or_name: str) -> Optional[str]:
        if id_or_name.isalpha():
            return cls.resolve_id_by_name(id_or_name)
        if Index.id_exists(id_or_name):
            return id_or_name
        return None

    @classmethod
    def clear_all_items(cls) -> None:
        """
        Removes all items from the registry and index files while preserving the headers.
        Also resets internal caches.
        """
        y_or_n_r = input('Are you sure you want to clear the registry? (y/n) ')
        if y_or_n_r.lower() == 'yes':
            # Clear the registry file
            with open(cls.registry_file, 'w', newline='', encoding='utf-8') as f_reg:
                writer = csv.DictWriter(f_reg, fieldnames=cls.headers)
                writer.writeheader()
            cls._cache = None
        
        y_or_n_i = input('Are you sure you want to clear the index? (y/n)')
        if y_or_n_i.lower() == 'yes':
            # Clear the index file
            with open(Index.index_file, 'w', newline='', encoding='utf-8') as f_idx:
                writer = csv.DictWriter(f_idx, fieldnames=Index.headers)
                writer.writeheader()
            Index._cache = None

class Index():
    """
    Provides a lightweight reference index of all item Ids and names.
    """
    # Why:
        # Allows quick ID <-> name lookups without reading entire registry.
    
    # Interactions:
        # Called by Registry and AdvancedSearch
    
    headers = INDEX_HEADERS
    index_file = 'summary/Index.csv'
    _cache = None

    @classmethod
    def load_index(cls) -> List[dict]:
        if cls._cache is not None:
            return cls._cache
        
        index = []
        with open(cls.index_file, 'r', newline='', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            index = list(reader)

        cls._cache = index
        return index
    
    @classmethod
    def save_index(cls) -> bool:
        summary_data = []

        registry = Registry.load_registry()

        for row in registry:
            summary_data.append({
                'id': row.get('id', ''),
                'name': row.get('name', ''),
                'brand': row.get('brand', '')
            })

        with open (cls.index_file, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=cls.headers)
            writer.writeheader()
            writer.writerows(summary_data)

        cls._cache = None
        return True
    
    @classmethod
    def search_name(cls, query) -> dict:
       query = query.lower().strip()
       summary = cls.load_index()
       return [item for item in summary if query in item['name'].lower()]
    
    @classmethod
    def id_exists(cls, item_id: str) -> bool:
        summary = cls.load_index()
        return any(row['id'] == item_id for row in summary)