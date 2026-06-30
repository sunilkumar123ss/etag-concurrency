# Recorded verification

Checked on 24 October 2026 with Python 3.9.6.

- 7 isolated unit tests passed.
- Default demo exited successfully from a separate temporary working directory.
- Repeated demo output was identical.
- `--help` exited successfully and printed usage.
- README Python example executed successfully.
- Source parsed with the Python 3.9 grammar.

Reproduce from this repository using `python3 -m unittest -v`, `python3 main.py`, and `python3 main.py --help`. The recorded interpreter version is the runtime actually tested; the syntax check alone is not a cross-version runtime matrix.
