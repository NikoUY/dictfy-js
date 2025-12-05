"""
Tests for dictify-js parser.
"""

from dictify_js import parse_file

def test_simple_object():
    code = "{ a: 1, b: 2 }"
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2}]


def test_nested_objects():
    code = "{ a: { b: { c: 1 } } }"
    result = parse_file(code)
    assert result == [{"a": {"b": {"c": 1}}}]


def test_arrays():
    code = "{ nums: [1, 2, 3], nested: [[4, 5], [6]] }"
    result = parse_file(code)
    assert result == [{"nums": [1, 2, 3], "nested": [[4, 5], [6]]}]


def test_literals():
    code = "{ t: true, f: false, n: null }"
    result = parse_file(code)
    assert result == [{"t": True, "f": False, "n": None}]


def test_strings():
    code = """{ a: "hello", b: 'world', c: "with \\"quotes\\"" }"""
    result = parse_file(code)
    assert result == [{"a": "hello", "b": "world", "c": 'with "quotes"'}]


def test_numbers():
    code = "{ dec: 42, float: 3.14, neg: -10, sci: 1e6, hex: 0xFF, bin: 0b1010, oct: 0o755 }"
    result = parse_file(code)
    assert result == [{
        "dec": 42,
        "float": 3.14,
        "neg": -10,
        "sci": 1e6,
        "hex": 255,
        "bin": 10,
        "oct": 493
    }]


def test_empty_containers():
    code = "{ obj: {}, arr: [] }"
    result = parse_file(code)
    assert result == [{"obj": {}, "arr": []}]


def test_multiple_top_level_objects():
    code = "{ a: 1 } { b: 2 } { c: 3 }"
    result = parse_file(code)
    assert result == [{"a": 1}, {"b": 2}, {"c": 3}]


def test_ignores_top_level_arrays():
    code = "[1, 2, 3] { a: 1 } [4, 5]"
    result = parse_file(code)
    assert result == [{"a": 1}]


def test_drops_functions():
    code = """
    {
        a: 1,
        fn1() {},
        fn2: () => {},
        fn3: function() {},
        b: 2
    }
    """
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2}]


def test_drops_spread():
    code = "{ a: 1, ...spread, b: 2 }"
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2}]


def test_drops_computed_keys():
    code = "{ a: 1, [computed]: 2, b: 3 }"
    result = parse_file(code)
    assert result == [{"a": 1, "b": 3}]


def test_drops_identifiers_as_values():
    code = "{ a: 1, b: SOME_CONST, c: 3 }"
    result = parse_file(code)
    assert result == [{"a": 1, "c": 3}]


def test_drops_function_calls():
    code = "{ a: 1, b: fn(), c: 3 }"
    result = parse_file(code)
    assert result == [{"a": 1, "c": 3}]


def test_drops_template_literals():
    code = "{ a: 1, b: `template`, c: 3 }"
    result = parse_file(code)
    assert result == [{"a": 1, "c": 3}]


def test_handles_comments():
    code = """
    {
        // line comment
        a: 1,
        /* block comment */ b: 2,
        /*
         * multi-line
         */ c: 3
    }
    """
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2, "c": 3}]


def test_handles_trailing_commas():
    """Test that trailing commas in objects and arrays are handled."""
    code = "{ a: 1, b: 2, } { arr: [1, 2, 3,] }"
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2}, {"arr": [1, 2, 3]}]


def test_handles_whitespace_variations():
    """Test various whitespace patterns."""
    code = "{a:1,b:2}   \n\n\t  {  c  :  3  }"
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2}, {"c": 3}]


def test_quoted_property_names():
    """Test that quoted property names work."""
    code = """{ "key-with-dash": 1, 'another-key': 2, normalKey: 3 }"""
    result = parse_file(code)
    assert result == [{"key-with-dash": 1, "another-key": 2, "normalKey": 3}]


def test_escaped_characters():
    """Test various escape sequences in strings."""
    code = r"""{ newline: "line1\nline2", tab: "a\tb", backslash: "c:\\path" }"""
    result = parse_file(code)
    assert result == [{"newline": "line1\nline2", "tab": "a\tb", "backslash": "c:\\path"}]


def test_mixed_quote_types():
    """Test mixing single and double quotes."""
    code = """{ a: "double", b: 'single', c: "it's", d: 'say "hi"' }"""
    result = parse_file(code)
    assert result == [{"a": "double", "b": "single", "c": "it's", "d": 'say "hi"'}]


def test_invalid_json_but_valid_js():
    """Test JS features that aren't valid JSON."""
    code = """{ 
        unquoted: 1,
        'singleQuoted': 2,
        trailingComma: 3,
    }"""
    result = parse_file(code)
    assert result == [{"unquoted": 1, "singleQuoted": 2, "trailingComma": 3}]


def test_deeply_nested_structures():
    """Test very deep nesting."""
    code = "{ a: { b: { c: { d: { e: { f: 'deep' } } } } } }"
    result = parse_file(code)
    assert result == [{"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}]


def test_large_numbers():
    """Test edge cases for numeric values."""
    code = "{ big: 999999999999, tiny: 0.000001, zero: 0, negZero: -0 }"
    result = parse_file(code)
    assert result[0]["big"] == 999999999999
    assert result[0]["tiny"] == 0.000001
    assert result[0]["zero"] == 0


def test_shorthand_properties():
    """Test that shorthand properties are dropped (identifier values)."""
    code = "{ a: 1, myVar, b: 2 }"
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2}]


def test_empty_input():
    """Test handling of empty or whitespace-only input."""
    assert parse_file("") == []
    assert parse_file("   \n\t  ") == []
    assert parse_file("// just a comment") == []


def test_no_objects():
    """Test input with no extractable objects."""
    code = "const x = 5; function foo() { return [1, 2, 3]; }"
    result = parse_file(code)
    assert result == []


def test_pathlib_path_input(tmp_path):
    """Test that Path objects work correctly."""
    test_file = tmp_path / "test.js"
    test_file.write_text("{ test: 'file', num: 42 }")
    
    result = parse_file(test_file)
    assert result == [{"test": "file", "num": 42}]


def test_special_numeric_values():
    """Test handling of Infinity, -Infinity, NaN (should be dropped)."""
    code = "{ a: 1, inf: Infinity, ninf: -Infinity, nan: NaN, b: 2 }"
    result = parse_file(code)
    # These should be dropped as they're identifiers, not literals
    assert result == [{"a": 1, "b": 2}]


def test_regex_literals():
    """Test that regex literals are dropped."""
    code = "{ a: 1, pattern: /test/, b: 2 }"
    result = parse_file(code)
    assert result == [{"a": 1, "b": 2}]


def test_mixed_valid_invalid_array_elements():
    """Test arrays with mix of valid and invalid elements."""
    code = """{ 
        arr: [
            1, 
            "valid", 
            someVar, 
            true, 
            fn(), 
            null,
            { keep: 1, drop: variable }
        ] 
    }"""
    result = parse_file(code)
    assert result == [{"arr": [1, "valid", True, None, {"keep": 1}]}]


def test_number_keys():
    """Test numeric property keys."""
    code = "{ 0: 'zero', 1: 'one', 999: 'many' }"
    result = parse_file(code)
    assert result == [{0: "zero", 1: "one", 999: "many"}]


def test_mixed_key_types():
    """Test mixing different key types."""
    code = """{ 
        normalKey: 1,
        "quoted-key": 2,
        'single-quoted': 3,
        123: 4
    }"""
    result = parse_file(code)
    assert result == [{
        "normalKey": 1,
        "quoted-key": 2,
        "single-quoted": 3,
        123: 4
    }]

def test_comprehensive_example():
    code = """
    const config = {
        version: 3,
        name: "demo",
        flags: [true, false, null, "ok", -10.25, 1e6, 0x1A2B],
        nested: {
            simple: { a: 1, b: 2 },
            deep: {
                nums: [0, -1, 2.5, 0o755, 0b110101],
                more: [
                    { w: true },
                    { x: null, y: [ { z: "end" }, [] ] }
                ]
            }
        },
        emptyList: [],
        emptyObj: {},
        badSpread: { ...x, 'good': 1},
        badValue: DO_NOT_KEEP,
        badCall: someFn(42),
        badFunc1() {},
        badFunc2: () => 123,
        badFunc3: function(x){},
        [`computedKey`]: 99,
        exprValue: a + b,
        templateLiteral: `hello ${world}`,
        work: 'yes',
        1234: 'numberKeys',
    };

    {
        info: "ok",
        arr: [1, true, null, { q: 7, bad: foo() }]
    }

    [
        { ignored: true },
        { ignored2: false }
    ]

    {
        mixed: [
            1,
            "str",
            null,
            { keep: "yes", drop: SOME_CONST },
            [{ deep: 1 }, [{ deeper: 2 }]],
            () => "no",
            fnCall()
        ],
        meta: {
            hex: 0xAB,
            sci: -3.2e-4,
            nested: { a: { b: { c: [1,2,3] } } }
        }
    }
    """

    result = parse_file(code)

    assert result[0]["version"] == 3
    assert result[0]["name"] == "demo"
    assert result[0]["flags"] == [True, False, None, "ok", -10.25, 1e6, 6699]
    assert result[0]["nested"]["simple"] == {"a": 1, "b": 2}
    assert result[0]["nested"]["deep"]["nums"] == [0, -1, 2.5, 493, 53]
    assert result[0]["emptyList"] == []
    assert result[0]["emptyObj"] == {}
    assert 'good' in result[0]["badSpread"]
    assert "badValue" not in result[0]
    assert "badCall" not in result[0]
    assert result[0]['work'] == 'yes'
    assert result[0][1234] == 'numberKeys'
    
    assert result[1]["info"] == "ok"
    assert result[1]["arr"] == [1, True, None, {"q": 7}]

    assert result[2]["mixed"] == [1, "str", None, {"keep": "yes"}, [{"deep": 1}, [{"deeper": 2}]]]
    assert result[2]["meta"]["hex"] == 171
    assert result[2]["meta"]["sci"] == -3.2e-4
    assert result[2]["meta"]["nested"] == {"a": {"b": {"c": [1, 2, 3]}}}


if __name__ == "__main__":
    test_simple_object()
    test_nested_objects()
    test_arrays()
    test_literals()
    test_strings()
    test_numbers()
    test_empty_containers()
    test_multiple_top_level_objects()
    test_ignores_top_level_arrays()
    test_drops_functions()
    test_drops_spread()
    test_drops_computed_keys()
    test_drops_identifiers_as_values()
    test_drops_template_literals()
    test_handles_comments()
    test_handles_trailing_commas()
    test_handles_whitespace_variations()
    test_quoted_property_names()
    test_escaped_characters()
    test_mixed_quote_types()
    test_invalid_json_but_valid_js()
    test_deeply_nested_structures()
    test_large_numbers()
    test_shorthand_properties()
    test_empty_input()
    test_no_objects()
    test_special_numeric_values()
    test_regex_literals()
    test_mixed_valid_invalid_array_elements()
    test_number_keys()
    test_mixed_key_types()
    test_comprehensive_example()
    
    print("✓ All tests passed!")