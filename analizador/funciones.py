def formato_error_sintactico(token, esperados):
    texto_esperados = '", "'.join(esperados)
    lexema = token.lexema
    if lexema == '':
        lexema = token.tipo
    return '<' + str(token.linea) + ',' + str(token.columna) + '> Error sintactico: se encontro: "' + lexema + '"; se esperaba: "' + texto_esperados + '".'

def formato_error_indentacion(linea, columna):
    return '<' + str(linea) + ',' + str(columna) + '>Error sintactico: falla de indentacion'

def escribir_reporte(texto):
    archivo = open('reporte.txt', 'w')
    archivo.write(texto)
    archivo.close()

