"""Módulo encargado del control de indentación."""

# Se asume que ErrorIndentacion y lanzar_error_indentacion ya están
# definidos en el espacio de nombres compartido.


class PilaIndentacion:
    """Implementa la pila de indentación estilo Python."""

    def __init__(self):
        self.valores = [0]

    def procesar(self, espacios, linea, columna):
        """Recibe la cantidad de espacios iniciales y genera tokens INDENT/DEDENT."""
        tope = self.valores[len(self.valores) - 1]
        if espacios == tope:
            return []
        if espacios > tope:
            self.valores.append(espacios)
            return [crear_token("INDENT", "", linea, columna)]
        tokens = []
        while len(self.valores) > 1 and espacios < self.valores[len(self.valores) - 1]:
            self.valores.pop()
            tokens.append(crear_token("DEDENT", "", linea, columna))
        if self.valores[len(self.valores) - 1] != espacios:
            lanzar_error_indentacion(linea, columna)
        return tokens

    def finalizar(self, linea_final):
        """Genera los DEDENT restantes al finalizar el archivo."""
        tokens = []
        while len(self.valores) > 1:
            self.valores.pop()
            tokens.append(crear_token("DEDENT", "", linea_final, 1))
        return tokens
