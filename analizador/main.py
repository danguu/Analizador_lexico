"""Punto de entrada del analizador sintáctico."""

contexto = {"__builtins__": __builtins__}

for ruta in [
    "tokens_def.py",
    "analizador/funciones.py",
    "analizador/automata.py",
    "analizador/lexer.py",
    "analizador/parser.py",
]:
    contenido = open(ruta, "r").read()
    exec(contenido, contexto)

leer_entrada = contexto["leer_entrada"]
escribir_reporte = contexto["escribir_reporte"]
ErrorAnalisis = contexto["ErrorAnalisis"]
ErrorIndentacion = contexto["ErrorIndentacion"]
ErrorSintactico = contexto["ErrorSintactico"]
tokenizar = contexto["tokenizar"]
ejecutar_parser = contexto["ejecutar_parser"]
MENSAJE_EXITO = contexto["MENSAJE_EXITO"]

lineas = leer_entrada()
resultado = ""
try:
    tokens = tokenizar(lineas)
    resultado = ejecutar_parser(tokens)
except ErrorAnalisis as error:
    resultado = error.mensaje
print(resultado)
escribir_reporte(resultado)
