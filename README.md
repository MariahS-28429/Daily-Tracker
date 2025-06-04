# Daily-Tracker
A customizable meal planner app with food, recipe, and workout tracking in Python.

## Information:
 - Use a .to_...() method to help save to a document
 - Use a .from_...() method to recreate an item
 - Use a .get_...() method to return a string
 - Use json.dumps() to save lists to csv
 - Use json.loads() to decode lists back

 - **kwargs allows the method to be flexible

## Utiltiy:
 - .to_dict()
 - .from_csv()
 - .from_dict()
 - .to_summary_dict()
 - .get_summary_row()
 - .matches_filters(**kwargs)

## Classes: 
### AdvancedSearch
    Find, Sort, Filter Class
        Time, high in specific nutrients, flexible, in a recipe, all food items, ingredient or not, high ingreident, type, equiptment, stretch vs exercise, flexible
    
### NutritionCalculator
    Uses the ids provided to calcute the nutrition and kcals.

### ItemRegistry
    Document of all children items (Full metadata)  ^ type (ingredient or not)
        Real-time updates

### SummaryIndex
    Document of a summary of all children items (Specifically for finding ID's for better searching in the full metadata document) ^ID, name, type, kcal
        Regenerate by parsing the master document

### Item (Parent)
    sends items to registry and summary

    - Food (Child)

    - Recipe (Child)
        Compute nutrition data from food IDs
        Add code to help scale ingridents to recipes

    - Workout (Child)
    
    - Supplement (Child)

### DayLog
    Document of each day as it is updated

    Document of a planned day
        Average kcal burned on previous days of the week to help with planning

    Supplements are automatically added, but can be removed if needed
    Can make a 'usual' items that can be brought in at once (pineapple juice, fiber one, etc.).
"""