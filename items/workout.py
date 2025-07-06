from items import Item

class Workout(Item):
    """
    A workout session, which may consist of multiple steps.
    Steps are referenced by ID if available.
    """

    # Why:
        # Complex structre, may invovle substeps.
        # Needs support for calorie estimation if only summary info is available.

    # Interactions:
        # Calls NutritionalCalculator for calorie estimates.
        # Registry might help aggregate step data.

    def __init__(self, item_name, item_type, sub_type, kcal, tags, brand):
        super().__init__(item_name, item_type, sub_type, kcal, tags, brand)
    
    def add_steps(steps_ids):
        """
        Add smaller exercise steps to this workout.
        """
        pass
    
    def estimate_step_kcal():
        """
        Distribute known total kcal across steps proportionally.
        """
        pass
    
    def update_on_step_change():
        """
        Recalculate estimates if any step has changed in registry.
        """
        pass
    
    def recalculate():
        pass

    def from_dict():
        pass

    def summary():
        pass