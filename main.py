"""Analizador léxico y sintáctico simple para un subconjunto de Python."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


@dataclass
class Token:
    """Representa un token generado por el analizador léxico."""

    type: str
    lexeme: str
    line: int
    column: int

    def __repr__(self) -> str:  # pragma: no cover - útil para depuración manual
        return f"Token(type={self.type!r}, lexeme={self.lexeme!r}, line={self.line}, column={self.column})"


class LexerError(Exception):
    """Excepción para errores léxicos relacionados con la indentación."""

    def __init__(self, line: int, column: int, message: str) -> None:
        super().__init__(message)
        self.line = line
        self.column = column
        self.message = message


class ParserSyntaxError(Exception):
    """Error sintáctico con información detallada."""

    def __init__(self, line: int, column: int, found: str, expected: Sequence[str]) -> None:
        super().__init__(found)
        self.line = line
        self.column = column
        self.found = found
        self.expected = list(expected)


class Lexer:
    """Generador de tokens para un subconjunto de Python."""

    KEYWORDS = {
        "def",
        "if",
        "elif",
        "else",
        "while",
        "for",
        "in",
        "return",
        "pass",
        "break",
        "continue",
        "True",
        "False",
        "None",
        "and",
        "or",
        "not",
    }

    OPERATORS = {
        "==",
        "!=",
        "<=",
        ">=",
        "->",
        "+=",
        "-=",
        "*=",
        "/=",
        "//=",
        "%=",
        "**=",
        "**",
        "//",
        "<<",
        ">>",
        "<<=",
        ">>=",
        "&=",
        "|=",
        "^=",
    }

    SIMPLE_SIGNS = set("+-*/%()[]{}:,.;@=<>|&^~")

    def __init__(self, text: str) -> None:
        self.text = text
        self.length = len(text)
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indents: List[int] = [0]
        self.tokens: List[Token] = []
        self.paren_level = 0
        self.line_start = True

    def tokenize(self) -> List[Token]:
        """Tokeniza el texto fuente."""

        while self.pos < self.length:
            if self.line_start:
                if not self._handle_indentation():
                    continue

            ch = self._peek()

            if ch in " \f\r\t":
                self._advance()
                continue

            if ch == "#":
                self._consume_comment()
                continue

            if ch == "\n":
                self._emit_newline()
                continue

            if ch in "'\"":
                self._tokenize_string()
                continue

            if ch.isdigit():
                self._tokenize_number()
                continue

            if ch == "_" or ch.isalpha():
                self._tokenize_identifier()
                continue

            op = self._match_operator()
            if op:
                self._emit_token(op, op)
                if op in {"(", "[", "{"}:
                    self.paren_level += 1
                elif op in {")","]","}"}:
                    self.paren_level = max(0, self.paren_level - 1)
                continue

            raise LexerError(self.line, self.column, "caracter inesperado")

        self._finalize_indents()
        self.tokens.append(Token("EOF", "EOF", self.line, self.column))
        return self.tokens

    def _handle_indentation(self) -> bool:
        """Gestiona INDENT/DEDENT cuando se está al inicio de una línea."""

        temp_pos = self.pos
        temp_col = self.column
        indent_count = 0
        while temp_pos < self.length:
            ch = self.text[temp_pos]
            if ch == " ":
                temp_pos += 1
                temp_col += 1
                indent_count += 1
            elif ch == "\t":
                temp_pos += 1
                indent_count += 8 - (indent_count % 8)
                temp_col += 1
            elif ch == "\f":
                temp_pos += 1
                temp_col += 1
            else:
                break

        if temp_pos >= self.length:
            self.pos = temp_pos
            self.column = temp_col
            return True

        ch = self.text[temp_pos]
        if ch == "\n":
            # línea en blanco
            self.pos = temp_pos
            self.column = temp_col
            self.line_start = False
            return True

        if ch == "#":
            self.pos = temp_pos
            self.column = temp_col
            self.line_start = False
            return True

        self.pos = temp_pos
        self.column = temp_col
        self.line_start = False

        if self.paren_level > 0:
            return True

        current_indent = self.indents[-1]
        if indent_count > current_indent:
            self.indents.append(indent_count)
            self.tokens.append(Token("INDENT", "INDENT", self.line, 1))
        elif indent_count < current_indent:
            while self.indents and indent_count < self.indents[-1]:
                self.indents.pop()
                self.tokens.append(Token("DEDENT", "DEDENT", self.line, 1))
            if indent_count != self.indents[-1]:
                raise LexerError(self.line, 1, "falla de indentacion")
        return True

    def _consume_comment(self) -> None:
        while self.pos < self.length and self.text[self.pos] != "\n":
            self._advance()

    def _emit_newline(self) -> None:
        self._advance()  # consume '\n'
        token = Token("NEWLINE", "\n", self.line - 1, 1)
        if self.paren_level == 0:
            self.tokens.append(token)
            self.line_start = True
        else:
            self.line_start = True

    def _tokenize_string(self) -> None:
        quote = self._advance()
        start_line = self.line
        start_col = self.column - 1
        start_pos = self.pos - 1

        is_triple = False
        if self._peek(0) == quote and self._peek(1) == quote:
            is_triple = True
            self._advance()
            self._advance()

        while True:
            if self.pos >= self.length:
                raise LexerError(start_line, start_col, "cadena sin cerrar")
            ch = self._advance()
            if ch == "\\":
                if self.pos >= self.length:
                    raise LexerError(start_line, start_col, "cadena sin cerrar")
                self._advance()
                continue
            if is_triple and ch == quote and self._peek(0) == quote and self._peek(1) == quote:
                self._advance()
                self._advance()
                break
            if not is_triple and ch == quote:
                break
        end_pos = self.pos
        lexeme = self.text[start_pos:end_pos]
        token = Token("STRING", lexeme, start_line, start_col)
        self.tokens.append(token)

    def _tokenize_number(self) -> None:
        start_line, start_col = self.line, self.column
        start_pos = self.pos
        has_dot = False
        while self.pos < self.length and self.text[self.pos].isdigit():
            self._advance()
        if self._peek() == "." and self._peek(1).isdigit():
            has_dot = True
            self._advance()
            while self.pos < self.length and self.text[self.pos].isdigit():
                self._advance()
        if self._peek() in {"e", "E"}:
            self._advance()
            if self._peek() in {"+", "-"}:
                self._advance()
            while self.pos < self.length and self.text[self.pos].isdigit():
                self._advance()
        lexeme = self.text[start_pos:self.pos]
        self.tokens.append(Token("NUMBER", lexeme, start_line, start_col))

    def _tokenize_identifier(self) -> None:
        start_line, start_col = self.line, self.column
        start_pos = self.pos
        while self.pos < self.length and (self.text[self.pos] == "_" or self.text[self.pos].isalnum()):
            self._advance()
        lexeme = self.text[start_pos:self.pos]
        token_type = lexeme if lexeme in self.KEYWORDS else "NAME"
        self.tokens.append(Token(token_type, lexeme, start_line, start_col))

    def _match_operator(self) -> Optional[str]:
        for size in (3, 2, 1):
            if self.pos + size <= self.length:
                candidate = self.text[self.pos:self.pos + size]
                if candidate in self.OPERATORS or (size == 1 and candidate in self.SIMPLE_SIGNS):
                    self.pos += size
                    self.column += size
                    return candidate
        return None

    def _emit_token(self, token_type: str, lexeme: str) -> None:
        column = self.column - len(lexeme)
        self.tokens.append(Token(token_type, lexeme, self.line, column))

    def _advance(self) -> str:
        ch = self.text[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _peek(self, offset: int = 0) -> str:
        index = self.pos + offset
        if index >= self.length:
            return "\0"
        return self.text[index]

    def _finalize_indents(self) -> None:
        if self.line_start and self.tokens and self.tokens[-1].type == "NEWLINE":
            pass
        while len(self.indents) > 1:
            self.indents.pop()
            self.tokens.append(Token("DEDENT", "DEDENT", self.line, 1))


class Parser:
    """Analizador sintáctico por descenso recursivo."""

    ASSIGNMENT_OPERATORS = {
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "//=",
        "%=",
        "**=",
    }

    COMPARISON_OPERATORS = {
        "<",
        ">",
        "<=",
        ">=",
        "==",
        "!=",
        "in",
    }

    def __init__(self, tokens: Sequence[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def match(self, *types: str) -> Optional[Token]:
        token = self.current()
        if token.type in types or token.lexeme in types:
            self.pos += 1
            return token
        return None

    def expect(self, *types: str) -> Token:
        token = self.current()
        if token.type in types or token.lexeme in types:
            self.pos += 1
            return token
        expected = [self._format_expected(t) for t in types]
        found = token.lexeme if token.type != "EOF" else "EOF"
        raise ParserSyntaxError(token.line, token.column, found, expected)

    def parse(self) -> None:
        self.parse_module()
        self.expect("EOF")

    def parse_module(self) -> None:
        while self.current().type != "EOF":
            if self.current().type == "NEWLINE":
                self.advance()
                continue
            self.parse_stmt()

    def parse_stmt(self) -> None:
        token = self.current()
        if token.type == "def":
            self.parse_funcdef()
        elif token.type == "if":
            self.parse_if()
        elif token.type == "while":
            self.parse_while()
        elif token.type == "for":
            self.parse_for()
        else:
            self.parse_simple_stmt()

    def parse_simple_stmt(self, *, allow_inline: bool = False) -> None:
        token = self.current()
        if token.type == "return":
            self.advance()
            if self.current().type not in {"NEWLINE", "DEDENT", "EOF"}:
                self.parse_expr_list()
        elif token.type == "pass":
            self.advance()
        elif token.type == "break":
            self.advance()
        elif token.type == "continue":
            self.advance()
        else:
            self.parse_expr_stmt()
        if not allow_inline:
            if self.current().type == "NEWLINE":
                self.advance()
            elif self.current().type in {"EOF", "DEDENT"}:
                return
            else:
                expected = ["\n"]
                raise ParserSyntaxError(self.current().line, self.current().column, self.current().lexeme, expected)

    def parse_expr_stmt(self) -> None:
        self.parse_testlist_star_expr()
        if self.current().lexeme in self.ASSIGNMENT_OPERATORS:
            op = self.advance()
            if op.lexeme == "=":
                self.parse_expr_stmt()
            else:
                self.parse_testlist_star_expr()

    def parse_testlist_star_expr(self) -> None:
        self.parse_expression()
        while self.current().type == ",":
            self.advance()
            if self.current().type in {"NEWLINE", "EOF"}:
                break
            self.parse_expression()

    def parse_expression(self) -> None:
        self.parse_or_test()

    def parse_or_test(self) -> None:
        self.parse_and_test()
        while self.match("or"):
            self.parse_and_test()

    def parse_and_test(self) -> None:
        self.parse_not_test()
        while self.match("and"):
            self.parse_not_test()

    def parse_not_test(self) -> None:
        if self.match("not"):
            self.parse_not_test()
        else:
            self.parse_comparison()

    def parse_comparison(self) -> None:
        self.parse_arith_expr()
        while self.current().lexeme in self.COMPARISON_OPERATORS:
            self.advance()
            self.parse_arith_expr()

    def parse_arith_expr(self) -> None:
        self.parse_term()
        while self.current().lexeme in {"+", "-"}:
            self.advance()
            self.parse_term()

    def parse_term(self) -> None:
        self.parse_factor()
        while self.current().lexeme in {"*", "/", "//", "%"}:
            self.advance()
            self.parse_factor()

    def parse_factor(self) -> None:
        if self.current().lexeme in {"+", "-"}:
            self.advance()
            self.parse_factor()
        else:
            self.parse_power()

    def parse_power(self) -> None:
        self.parse_atom_expr()
        if self.match("**"):
            self.parse_factor()

    def parse_atom_expr(self) -> None:
        self.parse_atom()
        while True:
            if self.match("("):
                self.parse_arglist_optional()
                self.expect(")")
            elif self.match("["):
                self.parse_subscript_list()
                self.expect("]")
            elif self.match("."):
                self.expect("NAME")
            else:
                break

    def parse_atom(self) -> None:
        token = self.current()
        if token.type == "NAME" or token.type in {"True", "False", "None"}:
            self.advance()
        elif token.type == "NUMBER" or token.type == "STRING":
            self.advance()
            while self.current().type == "STRING":
                self.advance()
        elif token.type == "(":
            self.advance()
            if self.current().type == ")":
                self.advance()
            else:
                self.parse_expression()
                while self.match(","):
                    if self.current().type == ")":
                        break
                    self.parse_expression()
                self.expect(")")
        elif token.type == "[":
            self.advance()
            if self.current().type == "]":
                self.advance()
            else:
                self.parse_expression()
                while self.current().type == ",":
                    comma = self.advance()
                    if self.current().type == "]":
                        raise ParserSyntaxError(comma.line, comma.column, comma.lexeme, ["]"])
                    self.parse_expression()
                self.expect("]")
        elif token.type == "{":
            self.parse_dict_or_set()
        else:
            expected = ["expresion"]
            raise ParserSyntaxError(token.line, token.column, token.lexeme, expected)

    def parse_dict_or_set(self) -> None:
        self.expect("{")
        if self.current().type == "}":
            self.advance()
            return
        self.parse_expression()
        if self.match(":"):
            self.parse_expression()
            while self.match(","):
                if self.current().type == "}":
                    break
                self.parse_expression()
                self.expect(":")
                self.parse_expression()
        else:
            while self.match(","):
                if self.current().type == "}":
                    break
                self.parse_expression()
        self.expect("}")

    def parse_subscript_list(self) -> None:
        if self.current().type == "]":
            return
        self.parse_subscript()
        while self.match(","):
            if self.current().type == "]":
                break
            self.parse_subscript()

    def parse_subscript(self) -> None:
        if self.current().type == ":":
            self.advance()
            if self.current().type not in {"]",
                                          ","}:
                self.parse_expression()
            if self.match(":"):
                if self.current().type not in {"]", ","}:
                    self.parse_expression()
            return
        self.parse_expression()
        if self.match(":"):
            if self.current().type not in {"]", ","}:
                self.parse_expression()
            if self.match(":"):
                if self.current().type not in {"]", ","}:
                    self.parse_expression()

    def parse_arglist_optional(self) -> None:
        if self.current().type == ")":
            return
        self.parse_argument()
        while self.match(","):
            if self.current().type == ")":
                break
            self.parse_argument()

    def parse_argument(self) -> None:
        self.parse_expression()
        if self.match("="):
            self.parse_expression()

    def parse_expr_list(self) -> None:
        self.parse_expression()
        while self.match(","):
            if self.current().type in {"NEWLINE", "EOF", ")"}:
                break
            self.parse_expression()

    def parse_suite(self) -> None:
        if self.match(":"):
            pass
        else:
            self.expect(":")
        if self.match("NEWLINE"):
            self.expect("INDENT")
            while self.current().type not in {"DEDENT", "EOF"}:
                if self.current().type == "NEWLINE":
                    self.advance()
                    continue
                self.parse_stmt()
            self.expect("DEDENT")
        else:
            self.parse_simple_stmt(allow_inline=True)
            if self.current().type == "NEWLINE":
                self.advance()

    def parse_funcdef(self) -> None:
        self.expect("def")
        self.expect("NAME")
        self.expect("(")
        if self.current().type != ")":
            self.parse_parameters()
        self.expect(")")
        if self.match("->"):
            self.parse_expression()
        self.parse_suite()

    def parse_parameters(self) -> None:
        self.parse_parameter()
        while self.match(","):
            if self.current().type == ")":
                break
            if self.current().type in {"NEWLINE", "DEDENT", "EOF"}:
                token = self.current()
                found = token.lexeme if token.type != "EOF" else "EOF"
                raise ParserSyntaxError(token.line, token.column, found, [")", ","])
            self.parse_parameter()

    def parse_parameter(self) -> None:
        self.expect("NAME")
        if self.match(":"):
            self.parse_expression()
        if self.match("="):
            self.parse_expression()

    def parse_if(self) -> None:
        self.expect("if")
        self.parse_expression()
        self.parse_suite()
        while self.match("elif"):
            self.parse_expression()
            self.parse_suite()
        if self.match("else"):
            self.parse_suite()

    def parse_while(self) -> None:
        self.expect("while")
        self.parse_expression()
        self.parse_suite()

    def parse_for(self) -> None:
        self.expect("for")
        self.expect("NAME")
        self.expect("in")
        self.parse_expression()
        self.parse_suite()

    def _format_expected(self, token_type: str) -> str:
        if token_type == "NEWLINE":
            return "\\n"
        if token_type == "INDENT":
            return "INDENT"
        if token_type == "DEDENT":
            return "DEDENT"
        if len(token_type) == 1 or token_type in Lexer.KEYWORDS or token_type in self.ASSIGNMENT_OPERATORS:
            return token_type
        if token_type == "NAME":
            return "identificador"
        return token_type


def parse_source(text: str) -> None:
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    parser.parse()


def run_single_source(text: str) -> str:
    try:
        parse_source(text)
    except LexerError as exc:
        if exc.message == "falla de indentacion":
            return f"<{exc.line},{exc.column}> Error sintactico: falla de indentacion"
        return f"<{exc.line},{exc.column}> Error sintactico: se encontro: \"{exc.message}\"; se esperaba: \"\""
    except ParserSyntaxError as exc:
        expected = ", ".join(f'"{item}"' for item in exc.expected)
        return f"<{exc.line},{exc.column}> Error sintactico: se encontro: \"{exc.found}\"; se esperaba: {expected}"
    return "El analisis sintactico ha finalizado exitosamente."


def read_source_from_path(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_output(path: str, message: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(message)


def load_test_cases(path: str) -> List[Tuple[str, str]]:
    cases: List[Tuple[str, str]] = []
    current_name: Optional[str] = None
    current_lines: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            if raw_line.startswith("### "):
                if current_name is not None:
                    cases.append((current_name, "".join(current_lines).rstrip("\n")))
                    current_lines = []
                current_name = raw_line[4:].strip()
            else:
                current_lines.append(raw_line)
        if current_name is not None:
            cases.append((current_name, "".join(current_lines).rstrip("\n")))
    return cases


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Analizador sintáctico básico para Python.")
    parser.add_argument("source", nargs="?", help="Ruta al archivo de código fuente. Si se omite, se lee stdin.")
    parser.add_argument("--out", dest="out", help="Ruta del archivo donde escribir el resultado.")
    parser.add_argument("--tests", dest="tests", help="Ejecuta los casos de prueba definidos en un archivo.")
    args = parser.parse_args(argv)

    messages: List[str] = []

    if args.tests:
        for name, snippet in load_test_cases(args.tests):
            message = run_single_source(snippet)
            messages.append(f"[{name}] {message}")
        final_message = "\n".join(messages)
        print(final_message)
        if args.out:
            write_output(args.out, final_message)
        return 0

    if args.source:
        try:
            source_code = read_source_from_path(args.source)
        except OSError:
            print(f"No se pudo leer el archivo: {args.source}")
            return 1
    else:
        source_code = sys.stdin.read()

    final_message = run_single_source(source_code)
    print(final_message)

    if args.out:
        write_output(args.out, final_message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
