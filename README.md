# ETag Concurrency

Prevent stale JSON updates with atomic compare-and-replace.

All bundled examples use synthetic data.

## Run

Requires Python 3.9 or later; no third-party packages or network access are needed.

```sh
python3 main.py
python3 main.py --help
python3 -m unittest -v
```

Run these commands from this repository's directory. The demo can also be launched from any directory by passing the absolute path to `main.py`.

## How it works

The document stores a deterministic JSON encoding and a monotonically increasing local version. Its quoted ETag is a SHA-256 digest over both. `get()` returns a detached JSON snapshot and its ETag. `replace()` performs the comparison and update under one lock; only a matching tag can write.

Including the version means an A → B → A sequence does not revive an old tag. Even replacing a document with equal content creates a new version. Serialization and hashing are O(document size).

## Reuse

```python
from main import VersionedDocument, PreconditionFailed

document = VersionedDocument({"count": 1})
value, tag = document.get()
new_tag = document.replace({"count": 2}, if_match=tag)
assert new_tag != tag
try:
    document.replace({"count": 3}, if_match=tag)
except PreconditionFailed:
    pass
assert document.get()[0] == {"count": 2}
```

## Demo behavior

The default demo accepts one update and rejects an edit based on the stale initial tag. The tests also coordinate two writers and verify exactly one succeeds.

## Boundaries

This is a local document abstraction, not an HTTP server or a complete `If-Match` header parser. It accepts one exact strong tag, without wildcards or tag lists. Versions reset when an object is recreated and are not persisted or shared across processes. JSON-only types, finite numbers, and string object keys are required. Application authorization is outside this example.

## Verification

`test_main.py` exercises boundary conditions, invalid inputs, and meaningful behavior specific to this implementation. The default demo is deterministic and completes without external services. See the collection's verification report for the recorded run; run the commands above to verify this repository independently.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
