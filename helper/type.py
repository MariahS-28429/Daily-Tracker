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
        
    @staticmethod
    def is_dict(value: dict, allow_empty: bool = True) -> dict:
        """
        Ensures the value is a dictionary.
        
        Parameters:
            value: The value to check.
            allow_empty: Whether to allow an empty dictionary (default True).
        
        Returns:
            The dictionary if valid.
        
        Raises:
            ValueError if the value is not a dict or is empty when not allowed.
        """
        if isinstance(value, dict):
            if not allow_empty and not value:
                caller = CheckType._get_caller_name()
                raise ValueError(f"Empty dictionary is not allowed. (Called from: {caller})")
            return value
        caller = CheckType._get_caller_name()
        raise ValueError(f"'{value}' is not a valid dictionary. (Called from: {caller})")
    
    @staticmethod
    def is_bool(value, allow_string: bool = True) -> bool:
        """
        Ensures the value is a boolean. Optionally allows string representations.
        
        Parameters:
            value: The value to check or convert.
            allow_string: If True, accepts 'true', 'false', 'yes', 'no', '1', '0' (case-insensitive).
        
        Returns:
            A boolean value.
        
        Raises:
            ValueError if the value is not a valid boolean or recognizable string.
        """
        if isinstance(value, bool):
            return value

        if allow_string and isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "1"}:
                return True
            elif lowered in {"false", "no", "0"}:
                return False

        caller = CheckType._get_caller_name()
        raise ValueError(f"'{value}' is not a valid boolean. (Called from: {caller})")