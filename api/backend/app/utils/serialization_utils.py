from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Type
from pydantic import BaseModel


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
            serialized[key] = [
                serialize_dict(item) if isinstance(item, dict) else str(item) if isinstance(item, (datetime, UUID)) else item
                for item in value
            ]
        else:
            serialized[key] = value
    return serialized


def align_dict_with_model(data: Dict[str, Any], model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Aligns a dictionary with a Pydantic model by:
    - Including only the fields present in the model.
    - Dropping any fields not present in the model, including nested relations.

    Args:
        data (Dict[str, Any]): The input data dictionary.
        model (Type[BaseModel]): The Pydantic model to align with.

    Returns:
        Dict[str, Any]: The aligned and validated data dictionary.
    """
    print('*' * 20)
    print(f"Input data fields: {list(data.keys())}")
    print(f"Pydantic model fields: {list(model.__fields__.keys())}")

    partial_data = {}
    for key, value in data.items():
        if key not in model.__fields__:
            continue  # Skip fields not in the model

        if isinstance(value, dict):
            continue  # Drop nested dictionaries like 'users'
        else:
            partial_data[key] = value

    print(f"Filtered data fields: {list(partial_data.keys())}")

    try:
        validated_data = model(**partial_data).model_dump(exclude_unset=True)
        print(f"Validated data fields: {list(validated_data.keys())}")
    except Exception as e:
        print(f"Validation error: {str(e)}")
        raise

    # Transform UUID fields to strings if the Pydantic model uses strings
    for field_name, field_value in validated_data.items():
        if isinstance(field_value, UUID) and model.__annotations__.get(field_name) == str:
            validated_data[field_name] = str(field_value)
    print('*' * 20)
    return validated_data