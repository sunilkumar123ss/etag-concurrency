"""Atomic compare-and-replace for a JSON document using a versioned strong ETag."""
import argparse
import hashlib
import json
import threading


class PreconditionRequired(ValueError):
    pass


class PreconditionFailed(ValueError):
    pass
