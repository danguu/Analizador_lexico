# Analizador_lexico

## Descripción General
Este proyecto implementa un **analizador léxico (lexer)** simple en Python.  
El lexer lee un archivo .py, lo recorre carácter a carácter y produce una lista de *tokens* con su tipo, valor (cuando aplica) y posición (línea, columna).

El resultado de la ejecución es un archivo `tokens.txt` que contiene todos los tokens identificados en el código fuente de entrada.

## Estructura del Proyecto

- **main.py**  
  Archivo principal. Recibe un archivo de entrada por línea de comandos, llama al lexer y guarda los tokens en `tokens.txt`.

- **tokens_def.py**  
  Contiene las definiciones de:
  - Palabras reservadas (`KEYWORDS`).
  - Operadores de dos caracteres (`MULTI_OPS`).
  - Operadores/caracteres simples (`SINGLE_OPS`).
  - Funciones auxiliares para verificar letras, dígitos e identificadores.

- **lexer_core.py**  
  Implementación del **autómata de estados finitos** que hace el análisis léxico.  
  Reconoce:
  - Identificadores y palabras reservadas.
  - Números enteros.
  - Cadenas entre comillas simples o dobles (con soporte básico para escapes).
  - Operadores y caracteres especiales.
  - Comentarios (líneas que comienzan con `#`).

## Cómo Ejecutar

1. Guardar el archivo de código fuente que se quiere analizar. Ejemplo: `ejemplo.py`

   ```python
   def suma(a, b):
       return a + b  # suma dos numeros
   ```

2. Ejecutar el programa desde la terminal:

   ```bash
   python3 main.py ejemplo.py
   ```

3. Revisar el archivo generado **tokens.txt**. Ejemplo de salida para el código anterior:

   ```
   <def,1,1>
   <id,suma,1,5>
   <tk_par_izq,1,9>
   <id,a,1,10>
   <tk_coma,1,11>
   <id,b,1,13>
   <tk_par_der,1,14>
   <tk_dos_puntos,1,15>
   <return,2,5>
   <id,a,2,12>
   <tk_entero,+,2,14>   # <-- el '+' fue interpretado como número (limitación actual)
   <id,b,2,16>
   ```
