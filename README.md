# dictify-js

`dictify-js` is a tiny pure-Python utility intended for scraping: it scans JavaScript/TypeScript source and extracts only the object/array literals that can be converted safely into Python data structures. Invalid JS constructs (functions, computed keys, spreads, identifier values, template literals, etc.) are skipped, so the results stay clean and predictable.

> ⚠️ This project is provided as-is for my personal use and won’t be actively maintained beyond that scope. However, I welcome PRs that include concrete tests to demonstrate the proposed behavior changes.

## Features

- Parses raw JS/TS source or files and collects every top-level object literal (arrays are ignored unless nested inside an object).
- Supports nested structures, arrays, primitives, quoted keys, numeric keys, escapes in strings, and hex/bin/oct literals.
- Gracefully handles comments, trailing commas, and whitespace.
- Drops anything that isn’t safely convertible: functions, spreads, computed or identifier keys/values, template literals, regexes, and calls.

## Installation

Since the package is not published to PyPI, install it directly from the source:

```bash
# Outside a virtual environment (system-wide install)
pip install /path/to/dictify-js

# Inside a virtual environment
python -m venv .venv
source .venv/bin/activate
pip install /path/to/dictify-js
```

Replace `/path/to/dictify-js` with the path to the project root on your machine.

## Example
Assume you have a file (`scenario.ts`):

```ts
const storyWorld = {
    hero: {
        name: "Nova Flux",
        gadgets: ["mag-pen", "plasma compass"],
        status: "active",
    },
    journal: [
        { day: 1, entry: "Drift Tower scanned", coords: [12.5, -4.2] },
        { day: 2, entry: "Met courier AI", coords: [13, -3], mood: "curious" },
    ],
    vault: {
        items: [
            { label: "antique map", value: null, borrowed: true },
            { label: "quantum pebble", value: 42, ownerFn() {} },
        ],
        "priority-list": ["starcore", "aurora key"],
    },
    [`computed-${3}`]: "dropped",
    engage() {
        return this.hero.name;
    },
};
```

Everything that can be expressed as literals is preserved otherwise it will be dropped.

```python
from dictify_js import parse_file

result = parse_file("scenario.ts")
print(result)
```

```python
{
    "storyWorld": {
        "hero": {
            "gadgets": ["mag-pen", "plasma compass"],
            "name": "Nova Flux",
            "status": "active",
        },
        "journal": [
            {"coords": [12.5, -4.2], "day": 1, "entry": "Drift Tower scanned"},
            {
                "coords": [13, -3],
                "day": 2,
                "entry": "Met courier AI",
                "mood": "curious",
            },
        ],
        "vault": {
            "items": [
                {"borrowed": True, "label": "antique map", "value": None},
                {"label": "quantum pebble", "value": 42},
            ],
            "priority-list": ["starcore", "aurora key"],
        },
    }
}

```

## License

MIT License
