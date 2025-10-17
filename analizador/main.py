if __package__ is None or __package__ == '':
    from lexer import lex
    from parser import Parser
    from funciones import escribir_reporte
else:
    from .lexer import lex
    from .parser import Parser
    from .funciones import escribir_reporte


def ejecutar():
    codigo = ''
    primera_linea = True
    while True:
        try:
            linea = input()
        except EOFError:
            break
        if primera_linea:
            codigo = linea
            primera_linea = False
        else:
            codigo = codigo + '\n' + linea
    tokens = lex(codigo)
    parser = Parser(tokens)
    exito, mensaje = parser.parse()
    resultado = mensaje
    print(resultado)
    escribir_reporte(resultado)


ejecutar()
