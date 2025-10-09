from datetime import datetime
from pydantic import HttpUrl


def serialize_for_json(obj):
    """Рекурсивная сериализация вложенных объектов."""
    if isinstance(obj, HttpUrl):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [serialize_for_json(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif hasattr(obj, 'dict'):
        return serialize_for_json(obj.dict())
    return obj
