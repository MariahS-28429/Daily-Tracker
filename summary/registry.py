class Registry():
    """
    Stores and manages all registered items.
    Automatically updates index and dependents when items change.
    """

    headers = ['id', 'name', 'item_type', 'sub_type', 'brand', 'kcal',
                  'time', 'data', 'makeup', 'tags']
    registry_file = "item_registry.csv"

    @classmethod
    def register_item(cls, row):
        registry = cls.load_registry()

        registry.append(row)

        cls.save_registry(registry)
    
    @classmethod
    def load_registry(cls) -> List[dict]:
        """
        Returns a list of all items and their attributes in the registry with each item row being a dictionary 
        with python objects for certian attributes.

        Output: [{'id': 't001', 'name': 'testing', 'item_type': 'testing', 'sub_type': '1', 'brand': '3', 'kcal': 2.0, 'time': 0.0, 'data': {}, 'makeup': [], 'tags': []}]
        """

        # Easily called to gain all information and parse through everything for any method that needs it.

        registry = []

        with open(cls.registry_file, 'r', newline='', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                cleaned = {}

                for key, value in row.items():
                    value = value.strip()

                    # takes the list and dictionary attributes and codes them back into python objects
                    if key in ['data', 'makeup', 'tags']:
                        try:
                            cleaned[key] = json.loads(value) if value else {} if key == 'data' else []
                        except json.JSONDecodeError:
                            cleaned[key] = {} if key == 'data' else []

                    # takes the float attributes and codes them back into python objects
                    elif key in ['kcal', 'time']:
                        try:
                            cleaned[key] = float(value)
                        except ValueError:
                            cleaned[key] = 0.0

                    # everything else is just added back on, as is.
                    else:
                        cleaned[key] = value

                registry.append(cleaned)

        return registry
    
    @classmethod
    def save_registry(cls, registry: List[dict]):
        """
        Updates / saves the registry with the new and updated registry given to it. 
        Codes items with json so they can be converted back to python objects.

        Input: [{'id': 't001', 'name': 'testing', 'item_type': 'testing', 'sub_type': '1', 'brand': '3', 'kcal': 2.0, 'time': 0.0, 'data': {}, 'makeup': [], 'tags': []}, 
        {'id': 't002', 'name': 'testing', 'item_type': 'testing', 'sub_type': '1', 'brand': '3', 'kcal': 2.0, 'time': 0.0, 'data': {}, 'makeup': [], 'tags': []}]
        """

        with open(cls.registry_file, 'w', newline='', encoding='utf-8') as f_out:
            
            # if the registry is empty, don't save it.
            if not registry:
                return
            
            writer = csv.DictWriter(f_out, fieldnames=cls.headers)
            writer.writeheader()

            # codes some attributes to json for later conversions
            for item in registry:
                row = item.copy()
                for field in ['data', 'makeup', 'tags']:
                    row[field] = json.dumps(row.get(field, {} if field == 'data' else []))
                writer.writerow(row)
        
        SummaryIndex.save_index()    
    
        pass
    
    @classmethod
    def resolve_id_by_name(cls, name: str) -> str | None:
        """
        Find the item ID based on a (possibly non-unique) item name.
        Returns the selected item ID, or None if not found/aborted.
        """

        matches = SummaryIndex.search_name(name)

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
    
    @classmethod
    def delete_item(cls, item_name: str) -> bool:
        """
        Delete the item with the given ID from the registry.

        Returns True if an item was deleted, False if not found.

        Input: 't003', 'q200'
        Output: True, False
        """

        # checks the summary index for any matches to the item name given
        id = cls.resolve_id_by_name(item_name)
        if not id:
            return False
        
        registry = cls.load_registry()
        original_len = len(registry)

        # Finds the item row based on id
        item = cls.get_item(id)
        if not item:
            return False
        
        # Validates deletion with the user
        print(f"\nYou are about to delete the following item:")
        for key, value in item.items():
            print(f"  {key}: {value}")
        confirm = input("Are you sure you want to delete this item? (y/n): ").strip().lower()

        if confirm not in ('y', 'yes'):
            print("Deletion cancelled.")
            return False
        
        # Updates the registry by adding every row but the one with the chosen id
        updated_registry = [i for i in registry if i['id'] != id]    
        if len(updated_registry) == original_len:
            print(f"No item found with ID '{id}'.")
            return False
        cls.save_registry(updated_registry)
  
    @classmethod
    def update_field(cls, item_name: str, field_name: str, new_value) -> bool:
        """
        Let's a user change fields for items that already exist in the registry file.

        Returns True if a change was made, False if not.

        Input: ('testing', 'name', 'test')
        Output: True
        """
        return cls.call_method(item_name, Item, "update_field", field_name, new_value)

    @classmethod
    def get_item(cls, id):
        registry = cls.load_registry()
        return next((item for item in registry if item['id'] == id), None)
    
    @classmethod
    def instantiate_item(cls, item_dict):
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
    def call_method(cls, name: str, method_class: type, method: str, *args):
        item_id = cls.resolve_id_by_name(name)
        registry = cls.load_registry()

        found = False
        for row in registry:
            if row["id"] == item_id:
                item = cls.instantiate_item(row)
                found = True
                break
        
        if found == False:
            raise ValueError(f"Item with name '{name}' not found in registry.")
        
        method_func = getattr(method_class, method)
        return method_func(item, *args)
    
    @classmethod
    def update_dependents(cls, item_id):
        """
        Recalculates and updates any items that include this item_id in their makeup.
        """
        dependents = cls.get_items_using(item_id)
        if not dependents:
            return

        registry = cls.load_registry()
        updated = False

        for dependent in dependents:
            # Find the dependent row in registry by id
            for row in registry:
                if row['id'] == dependent['id']:
                    obj = cls.instantiate_item(row)
                    obj.recalculate()
                    row.update(obj.to_registry_dict())
                    updated = True
                    break

        if updated:
            cls.save_registry(registry)
      
    @classmethod
    def get_all_by_type(cls, item_type: str) -> List[dict]:
        """
        Purpose:
            Retrieve all items of a specific type, like all foods, all recipes, all workouts, or all supplements.
            Useful if you want to list or filter items by type for display, editing, or calculations.

        Why you need it:
            Imagine you want to show the user all “recipes” in the app or all “workouts” in a given view.
            It helps isolate subsets of items quickly without loading or filtering everything manually.
            Also useful in logic that applies differently depending on item type.
        """
        
        registry = cls.load_registry()
        item_type = item_type.lower()

        return [item for item in registry if item.get('item_type', '') == item_type]
 
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
        registry = cls.load_registry()
        tags = set()

        for item in registry:
            tags.update(item["tags"])
        
        return tags
    
    @classmethod
    def call_subtype(cls) -> set:
        registry = cls.load_registry()
        subtypes = set()

        for item in registry:
            subtypes.update(item["subtype"])
        
        return subtypes