## Analizador sintáctico manual

Este proyecto construye un analizador recursivo descendente que reutiliza los
componentes del analizador léxico existente en el repositorio. El archivo
`analizador/lexer.py` sincroniza la tabla de palabras reservadas y operadores
con las definiciones de `tokens_def.py`, de modo que ambos módulos comparten la
misma nomenclatura base de símbolos.

### Subconjunto soportado

El parser reconoce el siguiente subconjunto de Python:

* Definiciones de funciones `def` con parámetros opcionales, anotaciones
  sencillas y cláusula de retorno `->`.
* Sentencias condicionales `if`/`elif`/`else`.
* Bucles `while` y `for` con iterables simples.
* La sentencia `return` con expresiones opcionales.
* Expresiones que combinan operadores lógicos (`and`, `or`, `not`), relacionales
  (`==`, `!=`, `<`, `>`, `<=`, `>=`) y aritméticos (`+`, `-`, `*`, `/`, `%`,
  `//`, `**`).
* Literales numéricos, de cadena, booleanos (`True`, `False`), `None`, listas,
  tuplas, diccionarios y llamadas a funciones.

Quedan fuera de alcance construcciones como clases, `try`/`except`, `with`,
comprensiones, asignaciones (incluso simples), `pass`, operadores bit a bit y
`match`.
Si el código fuente utiliza alguno de estos elementos se generará el mensaje de
error sintáctico correspondiente, deteniendo el análisis en el primer token no
soportado.

### Casos de prueba

En `analizador/pruebas/` se incluyen los archivos de ejemplo utilizados para la
validación automatizada:

* `entrada_0.txt` / `salida_0.txt`: error sintáctico causado por una lista de
  tipos mal cerrada.
* `entrada_1.txt` / `salida_1.txt`: error por una indentación incorrecta.

### Ejecución

El programa lee desde la entrada estándar y escribe el reporte en pantalla y en
`reporte.txt`. Para ejecutar cualquiera de las pruebas provistas:

```bash
python analizador/main.py < analizador/pruebas/entrada_0.txt
```

La salida debe coincidir con el contenido del archivo de referencia
correspondiente.
