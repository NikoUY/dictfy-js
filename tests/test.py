"""
Tests for dictify-js parser.
"""

from dictify_js import parse_file

def test_simple_object():
    code = "const x = { a: 1, b: 2 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2}}


def test_nested_objects():
    code = "const x = { a: { b: { c: 1 } } }"
    result = parse_file(code)
    assert result == {"x": {"a": {"b": {"c": 1}}}}


def test_arrays():
    code = "const x = { nums: [1, 2, 3], nested: [[4, 5], [6]] }"
    result = parse_file(code)
    assert result == {"x": {"nums": [1, 2, 3], "nested": [[4, 5], [6]]}}


def test_literals():
    code = "const x = { t: true, f: false, n: null }"
    result = parse_file(code)
    assert result == {"x": {"t": True, "f": False, "n": None}}


def test_strings():
    code = """const x = { a: "hello", b: 'world', c: "with \\"quotes\\"" }"""
    result = parse_file(code)
    assert result == {"x": {"a": "hello", "b": "world", "c": 'with "quotes"'}}


def test_numbers():
    code = "const x = { dec: 42, float: 3.14, neg: -10, sci: 1e6, hex: 0xFF, bin: 0b1010, oct: 0o755 }"
    result = parse_file(code)
    assert result == {"x": {
        "dec": 42,
        "float": 3.14,
        "neg": -10,
        "sci": 1e6,
        "hex": 255,
        "bin": 10,
        "oct": 493
    }}


def test_empty_containers():
    code = "const x = { obj: {}, arr: [] }"
    result = parse_file(code)
    assert result == {"x": {"obj": {}, "arr": []}}


def test_multiple_named_objects():
    code = "const a = { a: 1 }; let b = { b: 2 }; var c = { c: 3 }"
    result = parse_file(code)
    assert result == {"a": {"a": 1}, "b": {"b": 2}, "c": {"c": 3}}


def test_ignores_unnamed_objects():
    code = "{ a: 1 } const x = { b: 2 } { c: 3 }"
    result = parse_file(code)
    assert result == {"x": {"b": 2}}


def test_drops_functions():
    code = """
    const x = {
        a: 1,
        fn1() {},
        fn2: () => {},
        fn3: function() {},
        b: 2
    }
    """
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2}}


def test_drops_spread():
    code = "const x = { a: 1, ...spread, b: 2 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2}}


def test_drops_computed_keys():
    code = "const x = { a: 1, [computed]: 2, b: 3 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 3}}


def test_drops_identifiers_as_values():
    code = "const x = { a: 1, b: SOME_CONST, c: 3 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "c": 3}}


def test_drops_function_calls():
    code = "const x = { a: 1, b: fn(), c: 3 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "c": 3}}


def test_drops_template_literals():
    code = "const x = { a: 1, b: `template`, c: 3 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "c": 3}}


def test_handles_comments():
    code = """
    const x = {
        // line comment
        a: 1,
        /* block comment */ b: 2,
        /*
         * multi-line
         */ c: 3
    }
    """
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2, "c": 3}}


def test_handles_trailing_commas():
    """Test that trailing commas in objects and arrays are handled."""
    code = "const x = { a: 1, b: 2, }; const y = { arr: [1, 2, 3,] }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2}, "y": {"arr": [1, 2, 3]}}


def test_handles_whitespace_variations():
    """Test various whitespace patterns."""
    code = "const x={a:1,b:2};   \n\n\t  const  y  =  {  c  :  3  }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2}, "y": {"c": 3}}


def test_quoted_property_names():
    """Test that quoted property names work."""
    code = """const x = { "key-with-dash": 1, 'another-key': 2, normalKey: 3 }"""
    result = parse_file(code)
    assert result == {"x": {"key-with-dash": 1, "another-key": 2, "normalKey": 3}}


def test_escaped_characters():
    """Test various escape sequences in strings."""
    code = r"""const x = { newline: "line1\nline2", tab: "a\tb", backslash: "c:\\path" }"""
    result = parse_file(code)
    assert result == {"x": {"newline": "line1\nline2", "tab": "a\tb", "backslash": "c:\\path"}}


def test_mixed_quote_types():
    """Test mixing single and double quotes."""
    code = """const x = { a: "double", b: 'single', c: "it's", d: 'say "hi"' }"""
    result = parse_file(code)
    assert result == {"x": {"a": "double", "b": "single", "c": "it's", "d": 'say "hi"'}}


def test_invalid_json_but_valid_js():
    """Test JS features that aren't valid JSON."""
    code = """const x = { 
        unquoted: 1,
        'singleQuoted': 2,
        trailingComma: 3,
    }"""
    result = parse_file(code)
    assert result == {"x": {"unquoted": 1, "singleQuoted": 2, "trailingComma": 3}}


def test_deeply_nested_structures():
    """Test very deep nesting."""
    code = "const x = { a: { b: { c: { d: { e: { f: 'deep' } } } } } }"
    result = parse_file(code)
    assert result == {"x": {"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}}


def test_large_numbers():
    """Test edge cases for numeric values."""
    code = "const x = { big: 999999999999, tiny: 0.000001, zero: 0, negZero: -0 }"
    result = parse_file(code)
    assert result["x"]["big"] == 999999999999
    assert result["x"]["tiny"] == 0.000001
    assert result["x"]["zero"] == 0


def test_shorthand_properties():
    """Test that shorthand properties are dropped (identifier values)."""
    code = "const x = { a: 1, myVar, b: 2 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2}}


def test_empty_input():
    """Test handling of empty or whitespace-only input."""
    assert parse_file("") == {}
    assert parse_file("   \n\t  ") == {}
    assert parse_file("// just a comment") == {}


def test_no_objects():
    """Test input with no extractable objects."""
    code = "const x = 5; function foo() { return [1, 2, 3]; }"
    result = parse_file(code)
    assert result == {}


def test_pathlib_path_input(tmp_path):
    """Test that Path objects work correctly."""
    test_file = tmp_path / "test.js"
    test_file.write_text("const x = { test: 'file', num: 42 }")
    
    result = parse_file(test_file)
    assert result == {"x": {"test": "file", "num": 42}}


def test_special_numeric_values():
    """Test handling of Infinity, -Infinity, NaN (should be dropped)."""
    code = "const x = { a: 1, inf: Infinity, ninf: -Infinity, nan: NaN, b: 2 }"
    result = parse_file(code)
    # These should be dropped as they're identifiers, not literals
    assert result == {"x": {"a": 1, "b": 2}}


def test_regex_literals():
    """Test that regex literals are dropped."""
    code = "const x = { a: 1, pattern: /test/, b: 2 }"
    result = parse_file(code)
    assert result == {"x": {"a": 1, "b": 2}}


def test_mixed_valid_invalid_array_elements():
    """Test arrays with mix of valid and invalid elements."""
    code = """const x = { 
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
    assert result == {"x": {"arr": [1, "valid", True, None, {"keep": 1}]}}


def test_number_keys():
    """Test numeric property keys."""
    code = "const x = { 0: 'zero', 1: 'one', 999: 'many' }"
    result = parse_file(code)
    assert result == {"x": {0: "zero", 1: "one", 999: "many"}}


def test_mixed_key_types():
    """Test mixing different key types."""
    code = """const x = { 
        normalKey: 1,
        "quoted-key": 2,
        'single-quoted': 3,
        123: 4
    }"""
    result = parse_file(code)
    assert result == {"x": {
        "normalKey": 1,
        "quoted-key": 2,
        "single-quoted": 3,
        123: 4
    }}


def test_let_and_var():
    """Test that let and var work in addition to const."""
    code = """
    let letObj = { a: 1 };
    var varObj = { b: 2 };
    const constObj = { c: 3 };
    """
    result = parse_file(code)
    assert result == {
        "letObj": {"a": 1},
        "varObj": {"b": 2},
        "constObj": {"c": 3}
    }


def test_comprehensive_example():
    code = """
    var config = {
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

    const standalone = {
        info: "ok",
        arr: [1, true, null, { q: 7, bad: foo() }]
    };

    [
        { ignored: true },
        { ignored2: false }
    ]

    let another = {
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

    assert result["config"]["version"] == 3
    assert result["config"]["name"] == "demo"
    assert result["config"]["flags"] == [True, False, None, "ok", -10.25, 1e6, 6699]
    assert result["config"]["nested"]["simple"] == {"a": 1, "b": 2}
    assert result["config"]["nested"]["deep"]["nums"] == [0, -1, 2.5, 493, 53]
    assert result["config"]["emptyList"] == []
    assert result["config"]["emptyObj"] == {}
    assert 'good' in result["config"]["badSpread"]
    assert "badValue" not in result["config"]
    assert "badCall" not in result["config"]
    assert result["config"]['work'] == 'yes'
    assert result["config"][1234] == 'numberKeys'
    
    assert result["standalone"]["info"] == "ok"
    assert result["standalone"]["arr"] == [1, True, None, {"q": 7}]

    assert result["another"]["mixed"] == [1, "str", None, {"keep": "yes"}, [{"deep": 1}, [{"deeper": 2}]]]
    assert result["another"]["meta"]["hex"] == 171
    assert result["another"]["meta"]["sci"] == -3.2e-4
    assert result["another"]["meta"]["nested"] == {"a": {"b": {"c": [1, 2, 3]}}}


if __name__ == "__main__":
    test_simple_object()
    test_nested_objects()
    test_arrays()
    test_literals()
    test_strings()
    test_numbers()
    test_empty_containers()
    test_multiple_named_objects()
    test_ignores_unnamed_objects()
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
    test_let_and_var()
    test_comprehensive_example()
    
    print("✓ All tests passed!")