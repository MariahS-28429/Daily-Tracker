class Index():
    """
    Provides a lightweight reference index of all item Ids and names.
    """
    # Why:
        # Allows quick ID <-> name lookups without reading entire registry.
    
    # Interactions:
        # Called by Registry and AdvancedSearch
    
    headers = ['id', 'name', 'brand']
    index_file = 'summary_index.csv'

    @classmethod
    def load_index(cls):
        """
        Return a list (or dictionary) of all items currently tracked in the summary index, likely read from a CSV file (which stores rows where each entry is a JSON string).
        """
        # cls.save_index()

        index = []
        
        with open (cls.index_file, 'r', newline='', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                index.append(row)

        return index
    
    @classmethod
    def save_index(cls):
        summary_data = []

        registry = ItemRegistry.load_registry()

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
    
    def update_entry(item):
        pass
    
    def delete_entry(item_id):
        pass
    
    @classmethod
    def search_name(cls, query):
       query = query.lower().strip()
       summary = cls.load_index()
       return [item for item in summary if query in item['name'].lower()]
