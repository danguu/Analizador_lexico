from lexer_core import lexer

archivo = input("Dame el archivo para analizar: ")

try:
    with open(archivo, "r", encoding="utf-8") as f:
        source = f.read()
except:  # noqa: E722
    print("No se pudo leer el archivo:", archivo)
    exit

tokens = lexer(source)

if tokens is not None:
    # Guardar en archivo
    with open("tokens.txt", "w", encoding="utf-8") as out:
        for t in tokens:
            out.write(t + "\n")
