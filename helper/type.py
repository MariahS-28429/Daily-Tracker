class CheckType():
    """
    Helper class for validating and prompting correct user input types.
    """

    # Why:
        # Keeps validation logit out of other classses.

    # Interactions:
        # Used by any class prompting user input.

    @staticmethod
    def is_string(value: str) -> str:
        """Ensures the value is a non-empty string. Prompts until valid."""
        while True:
            if isinstance(value, str) and value.strip():
                return value
            value = input(f"'{value}' is not a valid non-empty string. Please try again: ")

    @staticmethod
    def is_float(value) -> float:
        """Ensures the value is a float. Prompts until valid."""
        while True:
            try:
                return float(value)
            except ValueError:
                value = input(f"'{value}' is not a valid number. Please try again: ")
        
    @staticmethod
    def is_list(value) -> list:
        while not isinstance(value, list):
            try:
                return value.split(',')
            except:
                value = input(f"'{value}' is not a valid list. Please try again: ")
        return value            