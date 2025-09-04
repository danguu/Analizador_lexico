import sys
from lexer_core import lexer


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 main.py archivo.py")
        sys.exit(1)

    archivo = sys.argv[1]

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            source = f.read()
    except:
        print("No se pudo leer el archivo:", archivo)
        sys.exit(1)

    tokens = lexer(source)

    if tokens is not None:
        # Guardar en archivo
        with open("tokens.txt", "w", encoding="utf-8") as out:
            for t in tokens:
                out.write(t + "\n")
