class CheckType:
    """
    Helper class for validating input types.
    Raises ValueError if validation fails.
    """

    @staticmethod
    def is_string(value: str) -> str:
        """Ensures the value is a non-empty string."""
        if isinstance(value, str) and value.strip():
            return value
        raise ValueError(f"'{value}' is not a valid non-empty string.")

    @staticmethod
    def is_float(value) -> float:
        """Ensures the value can be converted to a float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"'{value}' is not a valid number.")

    @staticmethod
    def is_list(value) -> list:
        """
        Ensures the value is a list.
        If a string is provided, attempts to split by comma.
        Raises ValueError if invalid.
        """
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            # Split by commas and strip whitespace
            return [item.strip() for item in value.split(',') if item.strip()]
        else:
            raise ValueError(f"'{value}' is not a valid list or string representing a list.")