"""Tokenizador manual encargado de producir la secuencia de tokens."""

PALABRAS_RESERVADAS = {}


def registrar_reservada(lexema, nombre):
    """Registra una palabra reservada en la tabla local."""
    PALABRAS_RESERVADAS[lexema] = nombre


lista_reservadas_base = [
    ("def", "DEF"),
    ("if", "IF"),
    ("elif", "ELIF"),
    ("else", "ELSE"),
    ("while", "WHILE"),
    ("for", "FOR"),
    ("in", "IN"),
    ("return", "RETURN"),
    ("and", "AND"),
    ("or", "OR"),
    ("not", "NOT"),
    ("True", "TRUE"),
    ("False", "FALSE"),
    ("None", "NONE"),
]

indice_reservada = 0
longitud_reservadas = len(lista_reservadas_base)
while indice_reservada < longitud_reservadas:
    par = lista_reservadas_base[indice_reservada]
    registrar_reservada(par[0], par[1])
    indice_reservada += 1

if "KEYWORDS" in globals():
    lista_keywords = list(KEYWORDS)
    indice_keyword = 0
    longitud_keywords = len(lista_keywords)
    while indice_keyword < longitud_keywords:
        palabra_keyword = lista_keywords[indice_keyword]
        if palabra_keyword not in PALABRAS_RESERVADAS:
            minus = palabra_keyword.lower()
            if minus in PALABRAS_RESERVADAS:
                registrar_reservada(palabra_keyword, PALABRAS_RESERVADAS[minus])
            else:
                registrar_reservada(palabra_keyword, palabra_keyword.upper())
        indice_keyword += 1


OPERADORES_DOBLES = {}


def registrar_operador_doble(lexema):
    """Agrega un operador compuesto a la tabla local."""
    if len(lexema) != 2:
        return
    primero = lexema[0]
    segundo = lexema[1]
    if primero not in OPERADORES_DOBLES:
        OPERADORES_DOBLES[primero] = {}
    OPERADORES_DOBLES[primero][segundo] = lexema


lista_operadores_base = ["==", "!=", "<=", ">=", "->", "//", "**"]
indice_op = 0
longitud_op = len(lista_operadores_base)
while indice_op < longitud_op:
    registrar_operador_doble(lista_operadores_base[indice_op])
    indice_op += 1

if "MULTI_OPS" in globals():
    lista_multis = list(MULTI_OPS.keys())
    indice_multi = 0
    longitud_multi = len(lista_multis)
    while indice_multi < longitud_multi:
        registrar_operador_doble(lista_multis[indice_multi])
        indice_multi += 1


SIMBOLOS_SIMPLES = {
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
    ",": "COMMA",
    ":": "COLON",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "%": "PERCENT",
    "=": "EQUAL",
    "<": "LT",
    ">": "GT",
    "!": "EXCLAMATION",
    ".": "DOT",
}

TRADUCTOR_SIMPLES = {
    "tk_par_izq": "LPAREN",
    "tk_par_der": "RPAREN",
    "tk_cor_izq": "LBRACKET",
    "tk_cor_der": "RBRACKET",
    "tk_llave_izq": "LBRACE",
    "tk_llave_der": "RBRACE",
    "tk_coma": "COMMA",
    "tk_dos_puntos": "COLON",
    "tk_punto": "DOT",
    "tk_suma": "PLUS",
    "tk_resta": "MINUS",
    "tk_mult": "STAR",
    "tk_div": "SLASH",
    "tk_mod": "PERCENT",
    "tk_asig": "EQUAL",
    "tk_menor": "LT",
    "tk_mayor": "GT",
}

if "SINGLE_OPS" in globals():
    lista_simbolos = list(SINGLE_OPS.keys())
    indice_simbolo = 0
    longitud_simbolos = len(lista_simbolos)
    while indice_simbolo < longitud_simbolos:
        simbolo = lista_simbolos[indice_simbolo]
        if simbolo not in SIMBOLOS_SIMPLES:
            nombre_original = SINGLE_OPS[simbolo]
            if nombre_original in TRADUCTOR_SIMPLES:
                SIMBOLOS_SIMPLES[simbolo] = TRADUCTOR_SIMPLES[nombre_original]
            else:
                SIMBOLOS_SIMPLES[simbolo] = simbolo
        indice_simbolo += 1


if "es_letra" in globals():
    verificador_letra = es_letra
else:
    def verificador_letra(caracter):
        codigo = ord(caracter)
        if codigo >= ord("a") and codigo <= ord("z"):
            return True
        if codigo >= ord("A") and codigo <= ord("Z"):
            return True
        return caracter == "_"

if "es_digito" in globals():
    verificador_digito = es_digito
else:
    def verificador_digito(caracter):
        codigo = ord(caracter)
        return codigo >= ord("0") and codigo <= ord("9")

if "es_id_parte" in globals():
    verificador_identificador = es_id_parte
else:
    def verificador_identificador(caracter):
        return verificador_letra(caracter) or verificador_digito(caracter)


def tokenizar(lineas):
    """Transforma las líneas en la secuencia de tokens esperada."""
    tokens = []
    pila_indentacion = PilaIndentacion()
    linea_actual = 1
    total_lineas = len(lineas)
    while linea_actual <= total_lineas:
        linea = lineas[linea_actual - 1]
        indice = 0
        longitud = len(linea)
        espacios = 0
        while indice < longitud and linea[indice] == " ":
            indice += 1
            espacios += 1
        if indice < longitud and linea[indice] == "\t":
            lanzar_error_indentacion(linea_actual, indice + 1)
        resto = linea[indice:]
        if resto == "" or resto.startswith("#"):
            tokens.append(crear_token("NUEVA_LINEA", "", linea_actual, 1))
            linea_actual += 1
            continue
        indent_tokens = pila_indentacion.procesar(espacios, linea_actual, indice + 1)
        indice_ind = 0
        longitud_indent = len(indent_tokens)
        while indice_ind < longitud_indent:
            tokens.append(indent_tokens[indice_ind])
            indice_ind += 1
        while indice < longitud:
            caracter = linea[indice]
            if caracter == "#":
                indice = longitud
                break
            if caracter == " " or caracter == "\t":
                indice += 1
                continue
            if verificador_letra(caracter):
                inicio = indice
                while indice < longitud and verificador_identificador(linea[indice]):
                    indice += 1
                lexema = linea[inicio:indice]
                tipo = PALABRAS_RESERVADAS.get(lexema, "IDENT")
                tokens.append(crear_token(tipo, lexema, linea_actual, inicio + 1))
                continue
            if verificador_digito(caracter):
                inicio = indice
                while indice < longitud and verificador_digito(linea[indice]):
                    indice += 1
                lexema = linea[inicio:indice]
                tokens.append(crear_token("NUMBER", lexema, linea_actual, inicio + 1))
                continue
            if caracter == '"' or caracter == "'":
                inicio = indice
                delimitador = caracter
                indice += 1
                cerrado = False
                while indice < longitud:
                    if linea[indice] == delimitador:
                        cerrado = True
                        indice += 1
                        break
                    indice += 1
                if not cerrado:
                    tokens.append(crear_token("STRING", linea[inicio:indice], linea_actual, inicio + 1))
                    lanzar_error_sintactico(tokens[len(tokens) - 1], [delimitador])
                lexema = linea[inicio:indice]
                tokens.append(crear_token("STRING", lexema, linea_actual, inicio + 1))
                continue
            if caracter in OPERADORES_DOBLES:
                siguiente = ""
                if indice + 1 < longitud:
                    siguiente = linea[indice + 1]
                mapa = OPERADORES_DOBLES[caracter]
                if siguiente in mapa:
                    lexema = caracter + siguiente
                    tokens.append(crear_token(lexema, lexema, linea_actual, indice + 1))
                    indice += 2
                    continue
            if caracter in SIMBOLOS_SIMPLES:
                tipo_simbolo = SIMBOLOS_SIMPLES[caracter]
                tokens.append(crear_token(tipo_simbolo, caracter, linea_actual, indice + 1))
                indice += 1
                continue
            lanzar_error_sintactico(crear_token("DESCONOCIDO", caracter, linea_actual, indice + 1), ["token valido"])
        tokens.append(crear_token("NUEVA_LINEA", "", linea_actual, longitud + 1))
        linea_actual += 1
    tokens_finales = pila_indentacion.finalizar(linea_actual)
    indice_dedent = 0
    longitud_dedent = len(tokens_finales)
    while indice_dedent < longitud_dedent:
        tokens.append(tokens_finales[indice_dedent])
        indice_dedent += 1
    tokens.append(crear_token("EOF", "EOF", linea_actual, 1))
    return tokens
