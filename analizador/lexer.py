if __package__ is None or __package__ == '':
    from tokens import Token
else:
    from .tokens import Token

KEYWORDS = [
    'def', 'return', 'if', 'elif', 'else', 'while', 'for', 'in', 'break',
    'continue', 'pass', 'and', 'or', 'not', 'class', 'True', 'False', 'None'
]

SYMBOLS = ['(', ')', ',', ':', '[', ']', '{', '}', '.', ';']
OPERATORS = ['+', '-', '*', '/', '%']


def es_letra(caracter):
    if caracter >= 'a' and caracter <= 'z':
        return True
    if caracter >= 'A' and caracter <= 'Z':
        return True
    return False


def es_digito(caracter):
    return caracter >= '0' and caracter <= '9'


def agregar_token(tokens, tipo, lexema, linea, columna):
    tokens.append(Token(tipo, lexema, linea, columna))


def manejar_indentacion(tokens, pila, espacios, linea):
    actual = pila[len(pila) - 1]
    if espacios > actual:
        pila.append(espacios)
        agregar_token(tokens, 'INDENT', '', linea, 1)
        return False
    if espacios < actual:
        while len(pila) > 0 and espacios < pila[len(pila) - 1]:
            pila.pop()
            agregar_token(tokens, 'DEDENT', '', linea, 1)
        if len(pila) == 0 or espacios != pila[len(pila) - 1]:
            agregar_token(tokens, 'INDENT_ERROR', '', linea, espacios + 1)
            return True
    return False


def lex(codigo):
    tokens = []
    longitud = len(codigo)
    indice = 0
    linea = 1
    columna = 1
    pila_indentacion = [0]
    inicio_linea = True
    linea_con_contenido = False
    error_indentacion = False

    while indice < longitud:
        caracter = codigo[indice]
        if caracter == '\r':
            indice += 1
            continue
        if caracter == '\n':
            if linea_con_contenido:
                agregar_token(tokens, 'NEWLINE', '', linea, columna)
            linea += 1
            columna = 1
            indice += 1
            inicio_linea = True
            linea_con_contenido = False
            continue
        if inicio_linea:
            espacios = 0
            posicion = indice
            while posicion < longitud:
                actual = codigo[posicion]
                if actual == ' ':
                    espacios += 1
                    posicion += 1
                elif actual == '\t':
                    espacios += 4
                    posicion += 1
                else:
                    break
            if posicion >= longitud:
                indice = posicion
                columna = espacios + 1
                break
            siguiente = codigo[posicion]
            if siguiente == '\n':
                indice = posicion
                columna = 1
                inicio_linea = True
                linea_con_contenido = False
                continue
            if siguiente == '#':
                indice = posicion
                columna = espacios + 1
                inicio_linea = False
                continue
            else:
                if manejar_indentacion(tokens, pila_indentacion, espacios, linea):
                    error_indentacion = True
                    break
                inicio_linea = False
                columna = espacios + 1
                indice = posicion
                continue
        if caracter == ' ':
            indice += 1
            columna += 1
            continue
        if caracter == '\t':
            indice += 1
            columna += 4
            continue
        if caracter == '#':
            linea_con_contenido = True
            while indice < longitud and codigo[indice] != '\n':
                indice += 1
                columna += 1
            continue
        if es_letra(caracter) or caracter == '_':
            inicio_columna = columna
            inicio = indice
            while indice < longitud:
                actual = codigo[indice]
                if es_letra(actual) or es_digito(actual) or actual == '_':
                    indice += 1
                    columna += 1
                else:
                    break
            lexema = codigo[inicio:indice]
            tipo = lexema if lexema in KEYWORDS else 'id'
            agregar_token(tokens, tipo, lexema, linea, inicio_columna)
            linea_con_contenido = True
            continue
        if es_digito(caracter):
            inicio_columna = columna
            inicio = indice
            while indice < longitud and es_digito(codigo[indice]):
                indice += 1
                columna += 1
            lexema = codigo[inicio:indice]
            agregar_token(tokens, 'entero', lexema, linea, inicio_columna)
            linea_con_contenido = True
            continue
        if caracter == '"' or caracter == "'":
            inicio_columna = columna
            inicio = indice
            cierre = caracter
            indice += 1
            columna += 1
            while indice < longitud and codigo[indice] != cierre and codigo[indice] != '\n':
                if codigo[indice] == '\\' and indice + 1 < longitud:
                    indice += 1
                    columna += 1
                indice += 1
                columna += 1
            if indice < longitud and codigo[indice] == cierre:
                indice += 1
                columna += 1
            lexema = codigo[inicio:indice]
            agregar_token(tokens, 'string', lexema, linea, inicio_columna)
            linea_con_contenido = True
            continue
        if caracter == '=':
            inicio_columna = columna
            if indice + 1 < longitud and codigo[indice + 1] == '=':
                agregar_token(tokens, '==', '==', linea, inicio_columna)
                indice += 2
                columna += 2
            else:
                agregar_token(tokens, '=', '=', linea, inicio_columna)
                indice += 1
                columna += 1
            linea_con_contenido = True
            continue
        if caracter == '!':
            inicio_columna = columna
            if indice + 1 < longitud and codigo[indice + 1] == '=':
                agregar_token(tokens, '!=', '!=', linea, inicio_columna)
                indice += 2
                columna += 2
                linea_con_contenido = True
                continue
        if caracter == '<':
            inicio_columna = columna
            if indice + 1 < longitud and codigo[indice + 1] == '=':
                agregar_token(tokens, '<=', '<=', linea, inicio_columna)
                indice += 2
                columna += 2
            else:
                agregar_token(tokens, '<', '<', linea, inicio_columna)
                indice += 1
                columna += 1
            linea_con_contenido = True
            continue
        if caracter == '>':
            inicio_columna = columna
            if indice + 1 < longitud and codigo[indice + 1] == '=':
                agregar_token(tokens, '>=', '>=', linea, inicio_columna)
                indice += 2
                columna += 2
            else:
                agregar_token(tokens, '>', '>', linea, inicio_columna)
                indice += 1
                columna += 1
            linea_con_contenido = True
            continue
        operador_encontrado = False
        contador = 0
        while contador < len(OPERATORS):
            simbolo = OPERATORS[contador]
            if caracter == simbolo:
                inicio_columna = columna
                agregar_token(tokens, simbolo, simbolo, linea, inicio_columna)
                indice += 1
                columna += 1
                linea_con_contenido = True
                operador_encontrado = True
                break
            contador += 1
        if operador_encontrado:
            continue
        simbolo_encontrado = False
        contador = 0
        while contador < len(SYMBOLS):
            simbolo = SYMBOLS[contador]
            if caracter == simbolo:
                inicio_columna = columna
                agregar_token(tokens, simbolo, simbolo, linea, inicio_columna)
                indice += 1
                columna += 1
                linea_con_contenido = True
                simbolo_encontrado = True
                break
            contador += 1
        if simbolo_encontrado:
            continue
        indice += 1
        columna += 1

    if not error_indentacion and linea_con_contenido:
        agregar_token(tokens, 'NEWLINE', '', linea, columna)

    if not error_indentacion:
        while len(pila_indentacion) > 1:
            pila_indentacion.pop()
            agregar_token(tokens, 'DEDENT', '', linea, 1)

    agregar_token(tokens, 'EOF', '', linea, columna)
    return tokens

