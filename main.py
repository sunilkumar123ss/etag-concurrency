"""Atomic compare-and-replace for a JSON document using a versioned strong ETag."""
import argparse
import hashlib
import json
import threading


class PreconditionRequired(ValueError):
    pass


class PreconditionFailed(ValueError):
    pass


def encode_document(value):
    def validate(item):
        if item is None or type(item) in (str, int, float, bool):
            return
        if type(item) is list:
            for element in item:
                validate(element)
            return
        if type(item) is dict and all(type(key) is str for key in item):
            for element in item.values():
                validate(element)
            return
        raise ValueError("document must contain only JSON values and string object keys")
    validate(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
