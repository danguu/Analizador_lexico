# Palabras reservadas de Python 
KEYWORDS = {
    "False", "class", "finally", "is", "return",
    "None", "continue", "for", "lambda", "try",
    "True", "def", "from", "nonlocal", "while",
    "and", "del", "global", "not", "with",
    "as", "elif", "if", "or", "yield",
    "assert", "else", "import", "pass",
    "break", "except", "in", "raise"
}

# Operadores de dos caracteres (prioridad subcadena más larga)
MULTI_OPS = {
    "==": "tk_igual",
    "!=": "tk_distinto",
    "<=": "tk_menor_igual",
    ">=": "tk_mayor_igual",
    "->": "tk_ejecuta",
    "+=": "tk_suma_asig",
    "-=": "tk_resta_asig",
    "*=": "tk_mult_asig",
    "/=": "tk_div_asig",
    "%=": "tk_mod_asig",
    "**": "tk_potencia",
    "//": "tk_div_entera",
}

# Operadores y símbolos de un solo carácter
SINGLE_OPS = {
    "(": "tk_par_izq",
    ")": "tk_par_der",
    "[": "tk_cor_izq",
    "]": "tk_cor_der",
    "{": "tk_llave_izq",
    "}": "tk_llave_der",
    ",": "tk_coma",
    ":": "tk_dos_puntos",
    ".": "tk_punto",
    "+": "tk_suma",
    "-": "tk_resta",
    "*": "tk_mult",
    "/": "tk_div",
    "%": "tk_mod",
    "=": "tk_asig",
    "<": "tk_menor",
    ">": "tk_mayor",
}

WHITESPACE = {" ", "\t", "\r"}


def is_identifier_start(ch):
    return ch == "_" or ch.isalpha()


def is_identifier_part(ch):
    return ch == "_" or ch.isalnum()


def lex(input_text):
    tokens_out = []
    i = 0
    line = 1
    col = 1
    n = len(input_text)

    def emit(s):
        tokens_out.append(s)

    def error_here():
        print(f">>> Error léxico(linea:{line},posicion:{col})")
        return None

    while i < n:
        ch = input_text[i]

        # Salto de línea
        if ch == "\n":
            i += 1
            line += 1
            col = 1
            continue

        # Espacios o tabs
        if ch in WHITESPACE:
            i += 1
            col += 1
            continue

        # Comentarios
        if ch == "#":
            while i < n and input_text[i] != "\n":
                i += 1
                col += 1
            continue

        # Cadenas
        if ch == "'" or ch == '"':
            quote = ch
            start_line, start_col = line, col
            i += 1
            col += 1
            start_content = i
            while i < n and input_text[i] != quote and input_text[i] != "\n":
                if input_text[i] == "\\" and i + 1 < n:
                    i += 2
                    col += 2
                else:
                    i += 1
                    col += 1
            if i >= n or input_text[i] == "\n":
                print(f">>> Error léxico(linea:{start_line},posicion:{start_col})")
                return None
            content = input_text[start_content:i]
            i += 1
            col += 1
            emit(f'<tk_cadena,"{content}",{start_line},{start_col}>')
            continue

        # Números enteros (con o sin signo)
        if ch in "+-" or ch.isdigit():
            start_line, start_col = line, col
            j = i
            if input_text[j] in "+-" and j + 1 < n and input_text[j + 1].isdigit():
                j += 1
            while j < n and input_text[j].isdigit():
                j += 1
            if j > i and (input_text[i].isdigit() or (input_text[i] in "+-" and j > i + 1)):
                lexema = input_text[i:j]
                emit(f"<tk_entero,{lexema},{start_line},{start_col}>")
                col += (j - i)
                i = j
                continue

        # Identificadores o palabras reservadas
        if is_identifier_start(ch):
            start_line, start_col = line, col
            j = i + 1
            while j < n and is_identifier_part(input_text[j]):
                j += 1
            lexema = input_text[i:j]
            if lexema in KEYWORDS:
                emit(f"<{lexema},{start_line},{start_col}>")
            else:
                emit(f"<id,{lexema},{start_line},{start_col}>")
            col += (j - i)
            i = j
            continue

        # Operadores de dos caracteres
        if i + 1 < n:
            two = input_text[i:i+2]
            if two in MULTI_OPS:
                emit(f"<{MULTI_OPS[two]},{line},{col}>")
                i += 2
                col += 2
                continue

        # Operadores de un carácter
        if ch in SINGLE_OPS:
            emit(f"<{SINGLE_OPS[ch]},{line},{col}>")
            i += 1
            col += 1
            continue

        # Carácter ilegal
        return error_here()

    return tokens_out


def main():
    in_path = input("Nombre del archivo de entrada: ").strip()
    out_path = input("Nombre del archivo de salida: ").strip()

    try:
        with open(in_path, "r", encoding="utf-8") as f:
            source = f.read()
    except:
        print("No se pudo leer el archivo de entrada")
        return

    tokens = lex(source)
    if tokens is None:
        return

    with open(out_path, "w", encoding="utf-8") as f:
        for t in tokens:
            f.write(t + "\n")


if __name__ == "__main__":
    main()
