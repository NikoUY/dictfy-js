class Parser:
    """
    Parser that walks through JS/TS text and extracts
    convertible structures.
    """

    # Sentinel to distinguish "parsed null" from "failed to parse"
    _NULL_VALUE = object()

    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.length = len(text)
        self.brace_depth = 0
        self.bracket_depth = 0

    @property
    def current(self) -> str:
        """Get current character or empty string if at end."""
        return self.text[self.index] if self.index < self.length else ""
    
    @property
    def end_of_file(self) -> bool:
        return self.index >= self.length

    def peek(self, n: int = 1) -> str:
        """Peek ahead n characters."""
        end = min(self.index + n, self.length)
        return self.text[self.index:end]

    def startswith(self, token: str) -> bool:
        """Check if current position starts with token."""
        return self.text[self.index:].startswith(token)

    def advance(self, number: int = 1):
        self.index += number

    def skip_to_valid(self):
        """Skip whitespace and comments (// and /* */)."""
        while not self.end_of_file:
            # Skip whitespace
            if self.current in " \t\n\r":
                self.advance()
                continue

            # Skip // comments
            if self.startswith("//"):
                self.advance(2)
                while not self.end_of_file and self.current != "\n":
                    self.advance()
                continue

            # Skip /* */ comments
            if self.startswith("/*"):
                self.advance(2)
                while self.index < self.length - 1:
                    if self.startswith("*/"):
                        self.advance(2)
                        break
                    self.advance()
                continue

            break

    def skip_invalid(self, stop_chars: str, container_end: str | None = None) -> str | None:
        """Skip unsupported constructs until we hit a stop character."""
        depth = 0
        current_quote = None

        # Track the depth we started at for this container
        starting_brace_depth = self.brace_depth if container_end == "}" else None
        starting_bracket_depth = self.bracket_depth if container_end == "]" else None

        while not self.end_of_file:
            character = self.current

            if character == "\\":
                self.advance(2)
                continue

            if current_quote:
                if character == current_quote:
                    current_quote = None
                self.advance()
                continue

            if character in "\"'`":
                current_quote = character
                self.advance()
                continue

            if character in "{[(":
                depth += 1
                if character == "{":
                    self.brace_depth += 1
                elif character == "[":
                    self.bracket_depth += 1
                self.advance()
                continue

            if character in "}])":
                # Update global depth tracking
                if character == "}":
                    self.brace_depth = max(0, self.brace_depth - 1)
                elif character == "]":
                    self.bracket_depth = max(0, self.bracket_depth - 1)

                if depth > 0:
                    depth -= 1
                    self.advance()
                    continue

                # Check if we've exited the container we're trying to stay within
                is_container_close = False
                if character == container_end:
                    if character == "}" and starting_brace_depth is not None:
                        is_container_close = self.brace_depth < starting_brace_depth
                    elif character == "]" and starting_bracket_depth is not None:
                        is_container_close = self.bracket_depth < starting_bracket_depth

                if character in stop_chars:
                    if character == container_end and not is_container_close:
                        self.advance()
                        continue
                    self.advance()
                    return character

                self.advance()
                continue

            if depth == 0 and character in stop_chars:
                self.advance()
                return character

            self.advance()

        return None

    def read_identifier(self) -> str | None:
        """Read a JavaScript identifier."""
        self.skip_to_valid()
        
        character = self.current
        if not (character.isalpha() or character in "_$"):
            return None
            
        start = self.index
        while not self.end_of_file:
            character = self.current
            if character.isalnum() or character in "_$":
                self.advance()
            else:
                break
        return self.text[start:self.index]

    def try_parse_assignment(self) -> tuple[str, dict | list] | None:
        """
        Try to parse a variable assignment like:
        const name = { ... }
        let name = { ... }
        var name = { ... }
        
        Returns (variable_name, parsed_structure) or None
        """
        saved_index = self.index
        self.skip_to_valid()
        
        # Check for const/let/var
        if self.startswith("const"):
            self.advance(5)
        elif self.startswith("let"):
            self.advance(3)
        elif self.startswith("var"):
            self.advance(3)
        else:
            self.index = saved_index
            return None
        
        # Must be followed by whitespace
        if not self.end_of_file and self.current not in " \t\n\r":
            self.index = saved_index
            return None
        
        # Read variable name
        var_name = self.read_identifier()
        if not var_name:
            self.index = saved_index
            return None
        
        self.skip_to_valid()
        
         # Skip TypeScript type annotation before the "="
        if self.current == ":":
            self.skip_invalid("=")
            self.index -= 1 # Return to = for the next step

        # Must have = sign
        if self.current != "=":
            self.index = saved_index
            return None
        
        self.advance()  # Skip =
        self.skip_to_valid()
        
        # Parse the structure
        if self.current not in "{[":
            self.index = saved_index
            return None
        
        structure = self.parse_structure()
        if structure is None:
            self.index = saved_index
            return None
        
        return (var_name, structure)

    def read_string(self) -> str | None:
        """Read a string literal ('...' or \"...\")."""
        quote = self.current
        if quote not in "\"'":
            return None

        self.advance()
        characters_list = []
        escape = False

        while not self.end_of_file:
            character = self.current

            if escape:
                # Basic escape handling
                escape_map = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    '"': '"',
                    "'": "'",
                }
                characters_list.append(escape_map.get(character, character))
                escape = False
                self.advance()
                continue

            if character == "\\":
                escape = True
                self.advance()
                continue

            if character == quote:
                self.advance()
                return "".join(characters_list)

            characters_list.append(character)
            self.advance()

        return None  # Unterminated string

    def read_number(self) -> int | float | None:
        """Read a number (decimal, float, hex, binary, octal, scientific)."""
        start = self.index
        
        # Handle negative sign
        if self.current == "-":
            self.advance()
            # Ensure there's a digit after the minus sign
            if self.end_of_file or not (self.current.isdigit() or self.current == "."):
                self.index = start
                return None

        # Hex: 0x...
        if self.startswith("0x") or self.startswith("0X"):
            self.advance(2)
            hex_start = self.index
            while not self.end_of_file and self.current in "0123456789abcdefABCDEF":
                self.advance()
            if self.index > hex_start:
                return int(self.text[start:self.index], 16)
            return None

        # Binary: 0b...
        if self.startswith("0b") or self.startswith("0B"):
            self.advance(2)
            bin_start = self.index
            while not self.end_of_file and self.current in "01":
                self.advance()
            if self.index > bin_start:
                return int(self.text[start:self.index], 2)
            return None

        # Octal: 0o...
        if self.startswith("0o") or self.startswith("0O"):
            self.advance(2)
            oct_start = self.index
            while not self.end_of_file and self.current in "01234567":
                self.advance()
            if self.index > oct_start:
                return int(self.text[start:self.index], 8)
            return None

        # Decimal/float/scientific
        has_digit = False
        has_dot = False

        while not self.end_of_file and self.current.isdigit():
            has_digit = True
            self.advance()

        if self.current == ".":
            has_dot = True
            self.advance()
            while not self.end_of_file and self.current.isdigit():
                has_digit = True
                self.advance()

        # Scientific notation
        if self.current in "eE":
            self.index += 1
            if self.current in "+-":
                self.index += 1
            exp_start = self.index
            while self.index < self.length and self.current.isdigit():
                self.index += 1
            if self.index == exp_start:  # No digits after e
                self.index = start
                return None

        if not has_digit:
            self.index = start
            return None

        num_str = self.text[start:self.index]
        try:
            return float(num_str) if (has_dot or "e" in num_str or "E" in num_str) else int(num_str)
        except ValueError:
            self.index = start
            return None

    def read_key(self) -> str | int | None:
        """Read object key (quoted string or identifier or numeric)."""
        self.skip_to_valid()

        # Quoted key
        if self.current in "\"'":
            return self.read_string()

        # Computed key - reject
        if self.current == "[":
            return None

        # Support numeric keys like { 0: "value", 123: "item" }
        if self.current.isdigit():
            num = self.read_number()
            return num if num is not None else None

        # Identifier key
        character = self.current
        if character.isalpha() or character in "_$":
            start = self.index
            while not self.end_of_file:
                character = self.current
                if character.isalnum() or character in "_$":
                    self.advance()
                else:
                    break
            return self.text[start:self.index]

        return None

    def read_value(self) -> str | int | float | bool | dict | list | None | object:
        """Read a value (string, number, bool, null, object, array)."""
        self.skip_to_valid()

        character = self.current

        # String
        if character in "\"'":
            return self.read_string()

        # Template literal - unsupported
        if character == "`":
            return None

        # Number
        if character.isdigit() or character == "-":
            return self.read_number()

        # Boolean/null literals
        if self.startswith("true"):
            self.advance(4)
            return True
        if self.startswith("false"):
            self.advance(5)
            return False
        if self.startswith("null"):
            self.advance(4)
            return Parser._NULL_VALUE

        # Object
        if character == "{":
            return self.parse_structure()

        # Array
        if character == "[":
            return self.parse_structure()

        # Everything else is unsupported
        return None

    def parse_structure(self) -> dict | list | None:
        """Parse object literal or array."""
        self.skip_to_valid()

        open_character = self.current
        if open_character not in "{[":
            return None

        is_dict = open_character == "{"
        end_character = "}" if is_dict else "]"

        self.advance()
        if is_dict:
            self.brace_depth += 1
            result = {}
        else:
            self.bracket_depth += 1
            result = []

        try:
            while True:
                self.skip_to_valid()

                if self.current == end_character:
                    self.advance()
                    return result

                if self.end_of_file:
                    return None

                if is_dict:
                    key = self.read_key()
                    if key is None:
                        stop_char = self.skip_invalid(",}", container_end=end_character)
                        if stop_char == end_character:
                            return result
                        if stop_char is None:
                            return None
                        continue

                    self.skip_to_valid()

                    if self.current != ":":
                        stop_char = self.skip_invalid(",}", container_end=end_character)
                        if stop_char == end_character:
                            return result
                        if stop_char is None:
                            return None
                        continue

                    self.advance()  # Skip Colon
                    value = self.read_value()

                    # Handle explicit null vs parse failure
                    if value is Parser._NULL_VALUE:
                        result[key] = None
                    elif value is not None:
                        result[key] = value
                    else:
                        # Parse failure - skip to next item
                        stop_char = self.skip_invalid(",}", container_end=end_character)
                        if stop_char == end_character:
                            return result
                        if stop_char is None:
                            return None
                        continue
                else:
                    value = self.read_value()
                    
                    # Handle explicit null vs parse failure
                    if value is Parser._NULL_VALUE:
                        result.append(None)
                    elif value is not None:
                        result.append(value)
                    else:
                        # Parse failure - skip to next item
                        stop_char = self.skip_invalid(",]", container_end=end_character)
                        if stop_char == end_character:
                            return result
                        if stop_char is None:
                            return None
                        continue

                self.skip_to_valid()

                if self.current == ",":
                    self.advance()
                    continue

                if self.current == end_character:
                    self.advance()
                    return result

                stop_char = self.skip_invalid(",}" if is_dict else ",]", container_end=end_character)
                if stop_char == end_character:
                    return result
                if stop_char is None:
                    return None

        finally:
            if is_dict:
                self.brace_depth = max(0, self.brace_depth - 1)
            else:
                self.bracket_depth = max(0, self.bracket_depth - 1)
