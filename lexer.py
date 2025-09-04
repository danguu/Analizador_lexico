# -------------------
# Conjuntos del autómata
# -------------------
KEYWORDS = {
    "False", "class", "finally", "is", "return",
    "None", "continue", "for", "lambda", "try",
    "True", "def", "from", "nonlocal", "while",
    "and", "del", "global", "not", "with",
    "as", "elif", "if", "or", "yield",
    "assert", "else", "import", "pass",
    "break", "except", "in", "raise"
}

MULTI_OPS = {
    "==": "tk_igual", "!=": "tk_distinto",
    "<=": "tk_menor_igual", ">=": "tk_mayor_igual",
    "->": "tk_ejecuta", "+=": "tk_suma_asig",
    "-=": "tk_resta_asig", "*=": "tk_mult_asig",
    "/=": "tk_div_asig", "%=": "tk_mod_asig",
    "**": "tk_potencia", "//": "tk_div_entera",
}

SINGLE_OPS = {
    "(": "tk_par_izq", ")": "tk_par_der",
    "[": "tk_cor_izq", "]": "tk_cor_der",
    "{": "tk_llave_izq", "}": "tk_llave_der",
    ",": "tk_coma", ":": "tk_dos_puntos",
    ".": "tk_punto", "+": "tk_suma",
    "-": "tk_resta", "*": "tk_mult",
    "/": "tk_div", "%": "tk_mod",
    "=": "tk_asig", "<": "tk_menor", ">": "tk_mayor",
}

WHITESPACE = {" ", "\t", "\r", "\n"}


def es_letra(ch): return ch.isalpha() or ch == "_"
def es_digito(ch): return ch.isdigit()
def es_id_parte(ch): return es_letra(ch) or es_digito(ch)


# -------------------
# AUTÓMATA LÉXICO
# -------------------
def lexer(texto):
    tokens = []
    estado = "q0"
    lexema = ""
    i, linea, columna = 0, 1, 1
    n = len(texto)

    while i < n:
        ch = texto[i]

        # -------------------
        # δ(q0, símbolo)
        # -------------------
        if estado == "q0":
            lexema = ""

            # Ignorar espacios
            if ch in WHITESPACE:
                if ch == "\n":
                    linea += 1
                    columna = 1
                else:
                    columna += 1
                i += 1
                continue

            # Identificador o palabra reservada
            elif es_letra(ch):
                estado = "q_id"
                lexema += ch
                start_line, start_col = linea, columna
                i += 1
                columna += 1

            # Número
            elif ch in "+-" or es_digito(ch):
                estado = "q_num"
                lexema += ch
                start_line, start_col = linea, columna
                i += 1
                columna += 1

            # Cadena
            elif ch in "\"'":
                estado = "q_str"
                quote = ch
                start_line, start_col = linea, columna
                i += 1
                columna += 1

            # Comentario
            elif ch == "#":
                estado = "q_comment"
                i += 1
                columna += 1

            # Operadores de dos caracteres
            elif i+1 < n and texto[i:i+2] in MULTI_OPS:
                tokens.append(f"<{MULTI_OPS[texto[i:i+2]]},{linea},{columna}>")
                i += 2
                columna += 2

            # Operadores de un caracter
            elif ch in SINGLE_OPS:
                tokens.append(f"<{SINGLE_OPS[ch]},{linea},{columna}>")
                i += 1
                columna += 1

            # Error
            else:
                print(f">>> Error léxico(linea:{linea},columna:{columna})")
                return None

        # -------------------
        # δ(q_id, símbolo)
        # -------------------
        elif estado == "q_id":
            if i < n and es_id_parte(ch):
                lexema += ch
                i += 1
                columna += 1
            else:
                # Estado de aceptación
                if lexema in KEYWORDS:
                    tokens.append(f"<{lexema},{start_line},{start_col}>")
                else:
                    tokens.append(f"<id,{lexema},{start_line},{start_col}>")
                estado = "q0"

        # -------------------
        # δ(q_num, símbolo)
        # -------------------
        elif estado == "q_num":
            if i < n and es_digito(ch):
                lexema += ch
                i += 1
                columna += 1
            else:
                # Estado de aceptación
                tokens.append(f"<tk_entero,{lexema},{start_line},{start_col}>")
                estado = "q0"

        # -------------------
        # δ(q_str, símbolo)
        # -------------------
        elif estado == "q_str":
            if i < n and texto[i] != quote and texto[i] != "\n":
                if texto[i] == "\\" and i + 1 < n:  # caracter escapado
                    lexema += texto[i:i+2]
                    i += 2
                    columna += 2
                else:
                    lexema += texto[i]
                    i += 1
                    columna += 1
            else:
                if i >= n or texto[i] == "\n":
                    print(f">>> Error léxico(linea:{start_line},columna:{start_col})")
                    return None
                tokens.append(f'<tk_cadena,"{lexema}",{start_line},{start_col}>')
                i += 1
                columna += 1
                estado = "q0"

        # -------------------
        # δ(q_comment, símbolo)
        # -------------------
        elif estado == "q_comment":
            if i < n and texto[i] != "\n":
                i += 1
                columna += 1
            else:
                estado = "q0"

    return tokens

