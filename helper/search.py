class AdvancedSearch():
    """
    Search and filter functionality for all items in the registry.
    """

    # Why:
        # Powerful, felxible searching and sorting across tiem attributes.

    # Interactions:
        # Accesses ItemRegistry.items directly.
    
    def search_by_name(name):
        pass
    
    def search_by_tag(tag):
        pass
    
    def search_by_kcal(min, max):
        pass
    
    def search_by_type(item_type):
        pass
    
    def reverse_search(tag = None, brand = None):
        """Find items missing data"""
        pass
    
    def sort_results(results, key, reverse = False):
        pass
    
    def filter_items(predicate_fuction):
        """Allows custom filter logic"""
        pass

    def is_high_protein():
        pass

    def matches_query():
        pass