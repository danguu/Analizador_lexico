if __package__ is None or __package__ == '':
    from funciones import formato_error_sintactico, formato_error_indentacion
else:
    from .funciones import formato_error_sintactico, formato_error_indentacion

EXITO = 'El analisis sintactico ha finalizado exitosamente.'

OPERADORES_COMPARACION = ['==', '!=', '<', '<=', '>', '>=']
OPERADORES_SUMA = ['+', '-']
OPERADORES_PRODUCTO = ['*', '/', '%']


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.actual = tokens[0]
        self.mensaje_error = None
        if self.actual.tipo == 'INDENT_ERROR':
            self.mensaje_error = formato_error_indentacion(self.actual.linea, self.actual.columna)

    def avanzar(self):
        if self.posicion < len(self.tokens) - 1:
            self.posicion += 1
            self.actual = self.tokens[self.posicion]
            if self.mensaje_error is None and self.actual.tipo == 'INDENT_ERROR':
                self.mensaje_error = formato_error_indentacion(self.actual.linea, self.actual.columna)

    def omitir_nuevas_lineas(self):
        while self.actual.tipo == 'NEWLINE' and self.mensaje_error is None:
            self.avanzar()

    def consumir(self, tipo, esperados):
        if self.mensaje_error is not None:
            return
        if self.actual.tipo == tipo:
            self.avanzar()
        else:
            self.reportar_error(esperados)

    def reportar_error(self, esperados):
        if self.mensaje_error is None:
            self.mensaje_error = formato_error_sintactico(self.actual, esperados)

    def parse(self):
        if self.mensaje_error is not None:
            return False, self.mensaje_error
        self.parse_programa()
        if self.mensaje_error is not None:
            return False, self.mensaje_error
        if self.actual.tipo != 'EOF':
            self.reportar_error(['EOF'])
            return False, self.mensaje_error
        return True, EXITO

    def parse_programa(self):
        self.omitir_nuevas_lineas()
        while self.actual.tipo != 'EOF' and self.mensaje_error is None:
            self.parse_sentencia()
            self.omitir_nuevas_lineas()

    def parse_sentencia(self):
        if self.mensaje_error is not None:
            return
        tipo = self.actual.tipo
        if tipo == 'def':
            self.parse_funcion()
        elif tipo == 'if':
            self.parse_if()
        elif tipo == 'while':
            self.parse_while()
        elif tipo == 'for':
            self.parse_for()
        else:
            self.parse_sentencia_simple()

    def parse_funcion(self):
        self.avanzar()
        self.consumir('id', ['id'])
        self.consumir('(', ['('])
        if self.mensaje_error is not None:
            return
        if self.actual.tipo != ')':
            self.parse_parametros()
        self.consumir(')', [')'])
        self.consumir(':', [':'])
        self.parse_bloque()

    def parse_parametros(self):
        self.consumir('id', ['id'])
        if self.mensaje_error is not None:
            return
        if self.actual.tipo == '=':
            self.avanzar()
            self.parse_expresion()
        while self.actual.tipo == ',':
            self.avanzar()
            if self.actual.tipo == ')':
                break
            self.consumir('id', ['id'])
            if self.mensaje_error is not None:
                return
            if self.actual.tipo == '=':
                self.avanzar()
                self.parse_expresion()

    def parse_if(self):
        self.avanzar()
        self.parse_expresion()
        self.consumir(':', [':'])
        self.parse_bloque()
        while self.actual.tipo == 'elif':
            self.avanzar()
            self.parse_expresion()
            self.consumir(':', [':'])
            self.parse_bloque()
        if self.actual.tipo == 'else':
            self.avanzar()
            self.consumir(':', [':'])
            self.parse_bloque()

    def parse_while(self):
        self.avanzar()
        self.parse_expresion()
        self.consumir(':', [':'])
        self.parse_bloque()

    def parse_for(self):
        self.avanzar()
        self.consumir('id', ['id'])
        self.consumir('in', ['in'])
        self.parse_expresion()
        self.consumir(':', [':'])
        self.parse_bloque()

    def parse_sentencia_simple(self):
        tipo = self.actual.tipo
        if tipo == 'return':
            self.avanzar()
            if self.actual.tipo not in ['NEWLINE', 'DEDENT', 'EOF']:
                self.parse_expresion()
        elif tipo == 'break' or tipo == 'continue' or tipo == 'pass':
            self.avanzar()
        else:
            self.parse_expresion_sentencia()

    def parse_expresion_sentencia(self):
        self.parse_expresion()
        while self.actual.tipo == '=' and self.mensaje_error is None:
            self.avanzar()
            self.parse_expresion()

    def parse_bloque(self):
        if self.actual.tipo == 'NEWLINE':
            self.avanzar()
            self.consumir('INDENT', ['INDENT'])
            self.omitir_nuevas_lineas()
            while self.actual.tipo != 'DEDENT' and self.actual.tipo != 'EOF' and self.mensaje_error is None:
                self.parse_sentencia()
                self.omitir_nuevas_lineas()
            self.consumir('DEDENT', ['DEDENT'])
        else:
            self.parse_sentencia_simple()

    def parse_expresion(self):
        self.parse_or()

    def parse_or(self):
        self.parse_and()
        while self.actual.tipo == 'or' and self.mensaje_error is None:
            self.avanzar()
            self.parse_and()

    def parse_and(self):
        self.parse_not()
        while self.actual.tipo == 'and' and self.mensaje_error is None:
            self.avanzar()
            self.parse_not()

    def parse_not(self):
        if self.actual.tipo == 'not':
            self.avanzar()
            self.parse_not()
        else:
            self.parse_comparacion()

    def parse_comparacion(self):
        self.parse_termino_suma()
        while self.actual.tipo in OPERADORES_COMPARACION and self.mensaje_error is None:
            self.avanzar()
            self.parse_termino_suma()

    def parse_termino_suma(self):
        self.parse_termino_producto()
        while self.actual.tipo in OPERADORES_SUMA and self.mensaje_error is None:
            operador = self.actual.tipo
            if operador in OPERADORES_SUMA:
                self.avanzar()
                self.parse_termino_producto()
            else:
                break

    def parse_termino_producto(self):
        self.parse_factor()
        while self.actual.tipo in OPERADORES_PRODUCTO and self.mensaje_error is None:
            self.avanzar()
            self.parse_factor()

    def parse_factor(self):
        if self.actual.tipo == '+' or self.actual.tipo == '-':
            self.avanzar()
            self.parse_factor()
        else:
            self.parse_postfijo()

    def parse_postfijo(self):
        self.parse_atomo()
        while self.mensaje_error is None:
            if self.actual.tipo == '(':
                self.avanzar()
                if self.actual.tipo == ')':
                    self.avanzar()
                else:
                    self.parse_argumentos()
                    self.consumir(')', [')'])
            elif self.actual.tipo == '[':
                self.avanzar()
                self.parse_expresion()
                self.consumir(']', [']'])
            elif self.actual.tipo == '.':
                self.avanzar()
                self.consumir('id', ['id'])
            else:
                break

    def parse_argumentos(self):
        self.parse_expresion()
        while self.actual.tipo == ',' and self.mensaje_error is None:
            self.avanzar()
            if self.actual.tipo == ')':
                break
            self.parse_expresion()

    def parse_atomo(self):
        tipo = self.actual.tipo
        if tipo == 'id' or tipo == 'entero' or tipo == 'string' or tipo == 'True' or tipo == 'False' or tipo == 'None':
            self.avanzar()
            return
        if tipo == '(':
            self.avanzar()
            if self.actual.tipo == ')':
                self.avanzar()
                return
            self.parse_expresion()
            while self.actual.tipo == ',' and self.mensaje_error is None:
                self.avanzar()
                if self.actual.tipo == ')':
                    break
                self.parse_expresion()
            self.consumir(')', [')'])
            return
        if tipo == '[':
            self.avanzar()
            if self.actual.tipo == ']':
                self.avanzar()
                return
            self.parse_expresion()
            while self.actual.tipo == ',' and self.mensaje_error is None:
                coma_token = self.actual
                self.avanzar()
                if self.actual.tipo == ']':
                    self.avanzar()
                    return
                if self.actual.tipo == ')' or self.actual.tipo == 'NEWLINE' or self.actual.tipo == 'EOF' or self.actual.tipo == 'DEDENT' or self.actual.tipo == ':' or self.actual.tipo == ',':
                    if self.mensaje_error is None:
                        self.mensaje_error = formato_error_sintactico(coma_token, [']'])
                    return
                self.parse_expresion()
            self.consumir(']', [']'])
            return
        if tipo == '{':
            self.avanzar()
            if self.actual.tipo == '}':
                self.avanzar()
                return
            self.parse_expresion()
            self.consumir(':', [':'])
            self.parse_expresion()
            while self.actual.tipo == ',' and self.mensaje_error is None:
                self.avanzar()
                if self.actual.tipo == '}':
                    break
                self.parse_expresion()
                self.consumir(':', [':'])
                self.parse_expresion()
            self.consumir('}', ['}'])
            return
        self.reportar_error(['id', 'entero', 'string', '(', '[', '{'])


def analizar(tokens):
    parser = Parser(tokens)
    return parser.parse()

