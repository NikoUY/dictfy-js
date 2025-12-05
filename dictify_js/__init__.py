"""
dictify-js — Extract Python dictionaries from JS/TS object literals.

A small pure-Python library that extracts Python dictionaries from JS/TS
object literals. It traverses the input recursively and keeps only structures
that can be safely converted. Everything else is intentionally dropped.
"""


from pathlib import Path
from typing import Union
from .parser import Parser


def parse_file(source: Union[str, Path]) -> dict[str, dict]:
    """
    Parse JS/TS file or code and extract named object literals.

    Args:
        source: File path (str or Path) or raw JS/TS code string

    Returns:
        Dict mapping variable names to their parsed object literals.
        Only extracts from const/let/var declarations.

    Example:
        >>> parse_file("const x = { a: 1 }; const y = { b: 2 }")
        {'x': {'a': 1}, 'y': {'b': 2}}
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
    results = {}

     # Scan for variable assignments
    while parser.index < parser.length:
        parser.skip_to_valid()
        
        # Try to parse assignment
        assignment = parser.try_parse_assignment()
        if assignment:
            var_name, structure = assignment
            if isinstance(structure, dict) and len(structure) > 0:
                results[var_name] = structure
        else:
            parser.advance()

    return results