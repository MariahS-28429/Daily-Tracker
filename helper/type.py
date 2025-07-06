import inspect

class CheckType:
    """
    Helper class for validating input types.
    Raises ValueError if validation fails.
    """

    @staticmethod
    def _get_caller_name():
        # Inspect stack and get the caller of the function that called this one
        stack = inspect.stack()
        if len(stack) >= 3:
            return stack[2].function
        return "Unknown"

    @staticmethod
    def is_string(value: str) -> str:
        """Ensures the value is a non-empty string."""
        if isinstance(value, str) and value.strip():
            return value
        caller = CheckType._get_caller_name()
        raise ValueError(f"'{value}' is not a valid non-empty string. (Called from: {caller})")

    @staticmethod
    def is_float(value) -> float:
        """Ensures the value can be converted to a float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            caller = CheckType._get_caller_name()
            raise ValueError(f"'{value}' is not a valid number. (Called from: {caller})")

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
            return [item.strip() for item in value.split(',') if item.strip()]
        else:
            caller = CheckType._get_caller_name()
            raise ValueError(f"'{value}' is not a valid list or string representing a list. (Called from: {caller})")