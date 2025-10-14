"""Funciones auxiliares para el analizador sintáctico."""

# Clases de excepciones para comunicar errores controlados.
class ErrorAnalisis(Exception):
    """Representa un error detectado durante el análisis."""

    def __init__(self, mensaje):
        self.mensaje = mensaje
        Exception.__init__(self, mensaje)


class ErrorSintactico(ErrorAnalisis):
    """Error específico producido por el parser."""


class ErrorIndentacion(ErrorAnalisis):
    """Error producido por una falla en la indentación."""


def leer_entrada():
    """Lee todas las líneas de la entrada estándar hasta EOF."""
    lineas = []
    while True:
        try:
            linea = input()
        except EOFError:
            break
        lineas.append(linea)
    return lineas


def escribir_reporte(contenido):
    """Escribe el reporte en el archivo de salida requerido."""
    archivo = open("reporte.txt", "w")
    archivo.write(contenido)
    archivo.close()


def crear_token(tipo, lexema, linea, columna):
    """Crea la estructura de un token simple."""
    return {
        "tipo": tipo,
        "lexema": lexema,
        "linea": linea,
        "columna": columna,
    }


def nombre_visible_token(token):
    """Devuelve el nombre visible para reportar un token."""
    tipo = token["tipo"]
    lexema = token["lexema"]
    if tipo == "EOF":
        return "EOF"
    if tipo in (
        "IDENT",
        "NUMBER",
        "STRING",
    ):
        return tipo.lower()
    if tipo == "NUEVA_LINEA":
        return "fin de linea"
    if len(lexema) == 1:
        return lexema
    return lexema


def formatear_error_sintactico(token, esperados):
    """Construye el mensaje de error sintáctico."""
    linea = token["linea"]
    columna = token["columna"]
    lexema = token["lexema"]
    if token["tipo"] == "EOF":
        lexema_visible = "EOF"
    else:
        lexema_visible = lexema
    piezas_esperados = []
    indice = 0
    longitud = len(esperados)
    while indice < longitud:
        piezas_esperados.append('"' + esperados[indice] + '"')
        indice += 1
    esperado = ", ".join(piezas_esperados)
    return (
        "<" + str(linea) + "," + str(columna) + "> Error sintactico: se encontro: "
        '"' + lexema_visible + '"; se esperaba: ' + esperado + "."
    )


def formatear_error_indentacion(linea, columna):
    """Crea el mensaje para fallos de indentación."""
    return "<" + str(linea) + "," + str(columna) + ">Error sintactico: falla de indentacion"


def lanzar_error_sintactico(token, esperados):
    """Lanza un error sintáctico con el formato solicitado."""
    raise ErrorSintactico(formatear_error_sintactico(token, esperados))


def lanzar_error_indentacion(linea, columna):
    """Lanza un error de indentación con el formato solicitado."""
    raise ErrorIndentacion(formatear_error_indentacion(linea, columna))
