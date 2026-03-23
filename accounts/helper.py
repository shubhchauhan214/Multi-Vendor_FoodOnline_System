def str_to_bool(value):
    """
    Converts a string value to a boolean.
    Recognizes 'true', '1', 'yes', 'y' as True.
    Recognizes 'false', '0', 'no', 'n' as False.
    Case insensitive.
    """
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'y']
    return bool(value)

