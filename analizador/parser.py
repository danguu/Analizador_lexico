"""Parser recursivo descendente para un subconjunto de Python.

El analizador cubre definiciones de funciones, condicionales, ciclos
``while`` y ``for``, sentencias ``return`` y expresiones con operadores
aritméticos, lógicos y relacionales básicos. También interpreta literales
numéricos, de cadena, listas, tuplas y diccionarios simples, así como
llamadas a funciones. Otros elementos del lenguaje (clases, ``try``,
``with``, comprensiones, etc.) quedan fuera del alcance documentado.
"""

# Se asume que existen las funciones y clases declaradas en funciones.py.

MENSAJE_EXITO = "El analisis sintactico ha finalizado exitosamente."


class Parser:
    """Implementa un analizador predictivo manual."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.actual = self.tokens[0]

    def avanzar(self):
        if self.posicion < len(self.tokens) - 1:
            self.posicion += 1
            self.actual = self.tokens[self.posicion]

    def verificar(self, tipo):
        return self.actual["tipo"] == tipo or self.actual["lexema"] == tipo

    def consumir(self, tipo, esperado):
        if self.verificar(tipo):
            token_consumido = self.actual
            self.avanzar()
            return token_consumido
        lanzar_error_sintactico(self.actual, [esperado])

    def coincidir(self, tipo):
        if self.verificar(tipo):
            token = self.actual
            self.avanzar()
            return token
        return None

    def parsear(self):
        while self.actual["tipo"] == "NUEVA_LINEA":
            self.avanzar()
        while self.actual["tipo"] != "EOF":
            self.sentencia()
            while self.actual["tipo"] == "NUEVA_LINEA":
                self.avanzar()
        return MENSAJE_EXITO

    def sentencia(self):
        tipo = self.actual["tipo"]
        lexema = self.actual["lexema"]
        if tipo == "DEF":
            self.sentencia_def()
        elif tipo == "IF":
            self.sentencia_if()
        elif tipo == "WHILE":
            self.sentencia_while()
        elif tipo == "FOR":
            self.sentencia_for()
        elif tipo == "RETURN":
            self.sentencia_return()
            self.consumir("NUEVA_LINEA", "fin de linea")
        else:
            self.expresion()
            self.consumir("NUEVA_LINEA", "fin de linea")

    def sentencia_def(self):
        self.consumir("DEF", "def")
        self.consumir("IDENT", "identificador")
        self.consumir("LPAREN", "(")
        if self.actual["tipo"] != "RPAREN":
            self.lista_parametros()
        self.consumir("RPAREN", ")")
        if self.actual["lexema"] == "->":
            self.avanzar()
            self.expresion()
        self.consumir("COLON", ":")
        self.suite_bloque()

    def lista_parametros(self):
        self.parametro()
        while self.actual["tipo"] == "COMMA":
            coma_token = self.actual
            self.avanzar()
            if self.actual["tipo"] == "RPAREN":
                lanzar_error_sintactico(coma_token, [")"])
            self.parametro()

    def parametro(self):
        self.consumir("IDENT", "identificador")
        if self.actual["lexema"] == ":":
            self.avanzar()
            self.tipo_anotacion()
        if self.actual["lexema"] == "=":
            self.avanzar()
            self.expresion()

    def tipo_anotacion(self):
        if self.actual["tipo"] == "LBRACKET":
            self.avanzar()
            self.expresion()
            if self.actual["tipo"] == "COMMA":
                coma = self.actual
                self.avanzar()
                if self.actual["tipo"] == "RBRACKET":
                    lanzar_error_sintactico(coma, ["]"])
                self.expresion()
            self.consumir("RBRACKET", "]")
            return
        self.expresion()

    def sentencia_if(self):
        self.consumir("IF", "if")
        self.expresion()
        self.consumir("COLON", ":")
        self.suite_bloque()
        while self.actual["tipo"] == "ELIF":
            self.avanzar()
            self.expresion()
            self.consumir("COLON", ":")
            self.suite_bloque()
        if self.actual["tipo"] == "ELSE":
            self.avanzar()
            self.consumir("COLON", ":")
            self.suite_bloque()

    def sentencia_while(self):
        self.consumir("WHILE", "while")
        self.expresion()
        self.consumir("COLON", ":")
        self.suite_bloque()

    def sentencia_for(self):
        self.consumir("FOR", "for")
        self.consumir("IDENT", "identificador")
        self.consumir("IN", "in")
        self.expresion()
        self.consumir("COLON", ":")
        self.suite_bloque()

    def sentencia_return(self):
        self.consumir("RETURN", "return")
        if self.actual["tipo"] != "NUEVA_LINEA":
            self.expresion()

    def suite_bloque(self):
        if self.actual["tipo"] == "NUEVA_LINEA":
            self.avanzar()
            self.consumir("INDENT", "INDENT")
            while self.actual["tipo"] == "NUEVA_LINEA":
                self.avanzar()
            while self.actual["tipo"] != "DEDENT":
                self.sentencia()
                while self.actual["tipo"] == "NUEVA_LINEA":
                    self.avanzar()
            self.consumir("DEDENT", "DEDENT")
            return
        self.sentencia()

    def expresion(self):
        self.expresion_or()

    def expresion_or(self):
        self.expresion_and()
        while self.actual["tipo"] == "OR":
            self.avanzar()
            self.expresion_and()

    def expresion_and(self):
        self.expresion_not()
        while self.actual["tipo"] == "AND":
            self.avanzar()
            self.expresion_not()

    def expresion_not(self):
        if self.actual["tipo"] == "NOT":
            self.avanzar()
            self.expresion_not()
        else:
            self.expresion_comparacion()

    def expresion_comparacion(self):
        self.expresion_aritmetica()
        while self.actual["lexema"] in ("==", "!=", "<", ">", "<=", ">="):
            self.avanzar()
            self.expresion_aritmetica()

    def expresion_aritmetica(self):
        self.expresion_termino()
        while self.actual["lexema"] in ("+", "-"):
            self.avanzar()
            self.expresion_termino()

    def expresion_termino(self):
        self.expresion_factor()
        while self.actual["lexema"] in ("*", "/", "%", "//"):
            self.avanzar()
            self.expresion_factor()

    def expresion_factor(self):
        if self.actual["lexema"] in ("+", "-"):
            self.avanzar()
            self.expresion_factor()
        else:
            self.expresion_potencia()

    def expresion_potencia(self):
        self.expresion_llamada()
        if self.actual["lexema"] == "**":
            self.avanzar()
            self.expresion_factor()

    def expresion_llamada(self):
        self.expresion_primaria()
        while self.actual["tipo"] == "LPAREN":
            self.avanzar()
            if self.actual["tipo"] != "RPAREN":
                self.lista_argumentos()
            self.consumir("RPAREN", ")")

    def lista_argumentos(self):
        self.expresion()
        while self.actual["tipo"] == "COMMA":
            self.avanzar()
            if self.actual["tipo"] == "RPAREN":
                lanzar_error_sintactico(self.actual, ["expresion"])
            self.expresion()

    def expresion_primaria(self):
        tipo = self.actual["tipo"]
        if tipo == "IDENT":
            self.avanzar()
            return
        if tipo in ("NUMBER", "STRING", "TRUE", "FALSE", "NONE"):
            self.avanzar()
            return
        if tipo == "LPAREN":
            self.avanzar()
            if self.actual["tipo"] != "RPAREN":
                self.expresion()
                while self.actual["tipo"] == "COMMA":
                    self.avanzar()
                    self.expresion()
            self.consumir("RPAREN", ")")
            return
        if tipo == "LBRACKET":
            self.avanzar()
            if self.actual["tipo"] != "RBRACKET":
                self.expresion()
                while self.actual["tipo"] == "COMMA":
                    coma = self.actual
                    self.avanzar()
                    if self.actual["tipo"] == "RBRACKET":
                        lanzar_error_sintactico(coma, ["]"])
                    self.expresion()
            self.consumir("RBRACKET", "]")
            return
        if tipo == "LBRACE":
            self.avanzar()
            if self.actual["tipo"] != "RBRACE":
                self.expresion()
                while self.actual["tipo"] == "COMMA":
                    self.avanzar()
                    self.expresion()
            self.consumir("RBRACE", "}")
            return
        lanzar_error_sintactico(self.actual, ["expresion"])


def ejecutar_parser(tokens):
    """Ejecuta el parser y devuelve el mensaje final."""
    parser = Parser(tokens)
    return parser.parsear()
