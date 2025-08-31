import sys
import keyword

# --- Configuración de tokens ---

KEYWORDS = set(keyword.kwlist)  # Palabras reservadas oficiales de Python

# Operadores/símbolos de uno y dos caracteres (respetar subcadena más larga)
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
        # Reportar el primer error y abortar
        print(f">>> Error léxico(linea:{line},posicion:{col})")
        return None

    while i < n:
        ch = input_text[i]

        # Saltar nuevas líneas
        if ch == "\n":
            i += 1
            line += 1
            col = 1
            continue

        # Ignorar espacios y tabs
        if ch in WHITESPACE:
            i += 1
            col += 1
            continue

        # Comentarios: '#' hasta fin de línea
        if ch == "#":
            # consumir hasta fin de línea (sin emitir tokens)
            while i < n and input_text[i] != "\n":
                i += 1
                col += 1
            continue  # la próxima iteración verá el '\n' o EOF

        # Strings: '...' o "..."
        if ch == "'" or ch == '"':
            quote = ch
            start_line, start_col = line, col
            i += 1
            col += 1
            start_content = i
            # leer hasta la comilla que cierra (no soportamos comillas triples aquí)
            while i < n and input_text[i] != quote and input_text[i] != "\n":
                # soporte básico de escape \" y \'
                if input_text[i] == "\\" and i + 1 < n:
                    i += 2
                    col += 2
                else:
                    i += 1
                    col += 1
            # fin de buffer
            if i >= n or input_text[i] == "\n":
                print(f">>> Error léxico(linea:{start_line},posicion:{start_col})")
                return None
            # cerrar comilla
            content = input_text[start_content:i]
            i += 1
            col += 1
            emit(f'<tk_cadena,"{content}",{start_line},{start_col}>')
            continue

        # Números enteros (con o sin signo)
        if ch in "+-" or ch.isdigit():
            start_line, start_col = line, col
            j = i
            # signo opcional
            if input_text[j] in "+-":
                # debe estar seguido de dígito para considerarse número con signo
                if j + 1 < n and input_text[j + 1].isdigit():
                    j += 1
                else:
                    # No es número, procesar como operador simple más abajo
                    pass
            # consumir dígitos
            while j < n and input_text[j].isdigit():
                j += 1
            # si realmente consumimos al menos un dígito:
            if (i != j and input_text[i].isdigit()) or (input_text[i] in "+-" and i+1 <= j-0):
                # Emitir número entero
                lexema = input_text[i:j]
                emit(f"<tk_entero,{lexema},{start_line},{start_col}>")
                col += (j - i)
                i = j
                continue
            # de lo contrario, caer a operadores (p.ej '+', '-')


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

        # Operadores de dos caracteres (subcadena más larga)
        matched = False
        if i + 1 < n:
            two = input_text[i:i+2]
            if two in MULTI_OPS:
                emit(f"<{MULTI_OPS[two]},{line},{col}>")
                i += 2
                col += 2
                matched = True
                continue

        if matched:
            continue

        # Operadores/símbolos de un carácter
        if ch in SINGLE_OPS:
            emit(f"<{SINGLE_OPS[ch]},{line},{col}>")
            i += 1
            col += 1
            continue

        # Si llegamos aquí, es un carácter ilegal → error
        return error_here()

    return tokens_out


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 lexer.py <entrada.py> <salida.txt>")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2]

    try:
        with open(in_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"No se pudo leer el archivo de entrada: {e}")
        sys.exit(1)

    tokens = lex(source)
    if tokens is None:
        # Ya se imprimió el error en stdout; además, no generamos archivo de salida
        sys.exit(1)

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            for t in tokens:
                f.write(t + "\n")
    except Exception as e:
        print(f"No se pudo escribir el archivo de salida: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
