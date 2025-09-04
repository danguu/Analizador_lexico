from tokens_def import KEYWORDS, MULTI_OPS, SINGLE_OPS, WHITESPACE
from tokens_def import es_letra, es_digito, es_id_parte


def lexer(texto):
    tokens = []
    estado = "q0"
    lexema = ""
    i, linea, columna = 0, 1, 1
    n = len(texto)

    while i < n:
        cr = texto[i]

        # Estado inicial q0
        if estado == "q0":
            lexema = ""

            if cr in WHITESPACE:
                if cr == "\n":
                    linea += 1
                    columna = 1
                else:
                    columna += 1
                i += 1
                continue

            elif es_letra(cr):
                estado = "q_id"
                lexema += cr
                start_line, start_col = linea, columna
                i += 1
                columna += 1

            elif cr in "+-" or es_digito(cr):
                estado = "q_num"
                lexema += cr
                start_line, start_col = linea, columna
                i += 1
                columna += 1

            elif cr in "\"'":
                estado = "q_str"
                quote = cr
                start_line, start_col = linea, columna
                i += 1
                columna += 1

            elif cr == "#":
                estado = "q_comment"
                i += 1
                columna += 1

            elif i+1 < n and texto[i:i+2] in MULTI_OPS:
                tokens.append(f"<{MULTI_OPS[texto[i:i+2]]},{linea},{columna}>")
                i += 2
                columna += 2

            elif cr in SINGLE_OPS:
                tokens.append(f"<{SINGLE_OPS[cr]},{linea},{columna}>")
                i += 1
                columna += 1

            else:
                print(f">>> Error léxico(linea:{linea},columna:{columna})")
                return None

        # Identificadores
        elif estado == "q_id":
            if i < n and es_id_parte(cr):
                lexema += cr
                i += 1
                columna += 1
            else:
                if lexema in KEYWORDS:
                    tokens.append(f"<{lexema},{start_line},{start_col}>")
                else:
                    tokens.append(f"<id,{lexema},{start_line},{start_col}>")
                estado = "q0"

        # Números
        elif estado == "q_num":
            if i < n and es_digito(cr):
                lexema += cr
                i += 1
                columna += 1
            else:
                tokens.append(f"<tk_entero,{lexema},{start_line},{start_col}>")
                estado = "q0"

        # Cadenas
        elif estado == "q_str":
            if i < n and texto[i] != quote and texto[i] != "\n":
                if texto[i] == "\\" and i + 1 < n:
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

        # Comentarios
        elif estado == "q_comment":
            if i < n and texto[i] != "\n":
                i += 1
                columna += 1
            else:
                estado = "q0"

    return tokens
