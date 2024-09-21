from datetime import datetime
from uuid import UUID

def serialize_dict(data: dict) -> dict:
    """
    Recursively serialize a dictionary, converting datetime objects to ISO format strings
    and UUID objects to strings.
    """
    serialized = {}
    for key, value in data.items():
        if isinstance(value, (datetime, UUID)):
            serialized[key] = str(value)
        elif isinstance(value, dict):
            serialized[key] = serialize_dict(value)
        elif isinstance(value, list):
            serialized[key] = [serialize_dict(item) if isinstance(item, dict) else str(item) if isinstance(item, (datetime, UUID)) else item for item in value]
        else:
            serialized[key] = value
    return serialized