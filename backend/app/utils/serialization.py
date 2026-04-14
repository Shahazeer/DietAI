"""Shared MongoDB document serialization utilities."""

from bson import ObjectId
from datetime import datetime

# Fields that must never be exposed to API clients
HIDDEN_FIELDS = frozenset({"file_path", "file_hash", "hashed_password"})


def serialize_doc(doc: dict | None) -> dict | None:
    """
    Recursively convert a MongoDB document to a JSON-safe dict.
    Strips hidden fields and converts ObjectId / datetime values.
    """
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if key in HIDDEN_FIELDS:
            continue
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(i) if isinstance(i, dict) else i for i in value]
        else:
            result[key] = value
    return result
