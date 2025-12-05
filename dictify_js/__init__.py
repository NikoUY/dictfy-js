"""
dictify-js — Extract Python dictionaries from JS/TS object literals.

A small pure-Python library that extracts Python dictionaries from JS/TS
object literals. It traverses the input recursively and keeps only structures
that can be safely converted. Everything else is intentionally dropped.
"""


from pathlib import Path
from typing import Union
from .parser import Parser


def parse_file(source: Union[str, Path]) -> list[dict]:
    """
    Parse JS/TS file or code and extract all top-level object literals.

    Args:
        source: File path (str or Path) or raw JS/TS code string

    Returns:
        List of Python dicts extracted from top-level object literals.
        Top-level arrays are ignored.

    Example:
        >>> parse_file(Path("config.js"))
        [{'version': 3, 'name': 'demo'}]

        >>> parse_file("const x = { a: 1 }; { b: 2 }")
        [{'a': 1}, {'b': 2}]
    """

    # Determine if source is a file path or raw code
    if isinstance(source, Path):
        # Likely a file path
        if source.exists() and source.is_file():
            text = source.read_text(encoding="utf-8")
        else:
            raise FileExistsError("File does not exist.")
    else:
        text = source

    # Create traverser
    parser = Parser(text)
    results = []

    # Scan for top-level { characters
    while parser.index < parser.length:
        parser.skip_to_valid()

        if parser.current in ["{", "["]:
            obj = parser.parse_structure()
            if isinstance(obj, dict) and len(obj) > 0: # For now we only care about non empty dicts
                results.append(obj)
        else:
            parser.advance()

    return results