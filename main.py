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


class VersionedDocument:
    def __init__(self, value):
        self._body = encode_document(value)
        self._version = 1
        self._lock = threading.Lock()

    def _etag(self):
        payload = str(self._version).encode("ascii") + b":" + self._body
        return '"' + hashlib.sha256(payload).hexdigest() + '"'

    def get(self):
        with self._lock:
            return json.loads(self._body), self._etag()

    def replace(self, value, if_match):
        if if_match is None:
            raise PreconditionRequired("an ETag from get() is required")
        if not isinstance(if_match, str):
            raise PreconditionFailed("if_match must be a single strong ETag")
        encoded = encode_document(value)
        with self._lock:
            if if_match != self._etag():
                raise PreconditionFailed("document changed since the supplied ETag")
            self._body = encoded
            self._version += 1
            return self._etag()


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    document = VersionedDocument({"title": "Synthetic draft", "published": False})
    initial, etag = document.get()
    updated_etag = document.replace({"title": "Synthetic draft", "published": True}, etag)
    try:
        document.replace({"title": "Stale edit"}, etag)
    except PreconditionFailed:
        stale_outcome = "rejected"
    current, _ = document.get()
    print(json.dumps({"initial": initial, "updated": current, "etag_changed": etag != updated_etag,
                      "stale_update": stale_outcome}, indent=2))


if __name__ == "__main__":
    main()
