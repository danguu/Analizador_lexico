KEYWORDS = {
    "False", "class", "finally", "is", "return",
    "None", "continue", "for", "lambda", "try",
    "True", "def", "from", "nonlocal", "while",
    "and", "del", "global", "not", "with",
    "as", "elif", "if", "or", "yield",
    "assert", "else", "import", "pass",
    "break", "except", "in", "raise"
}

MULTI_OPS = {
    "==": "tk_igual", "!=": "tk_distinto",
    "<=": "tk_menor_igual", ">=": "tk_mayor_igual",
    "->": "tk_ejecuta", "+=": "tk_suma_asig",
    "-=": "tk_resta_asig", "*=": "tk_mult_asig",
    "/=": "tk_div_asig", "%=": "tk_mod_asig",
    "**": "tk_potencia", "//": "tk_div_entera",
}

SINGLE_OPS = {
    "(": "tk_par_izq", ")": "tk_par_der",
    "[": "tk_cor_izq", "]": "tk_cor_der",
    "{": "tk_llave_izq", "}": "tk_llave_der",
    ",": "tk_coma", ":": "tk_dos_puntos",
    ".": "tk_punto", "+": "tk_suma",
    "-": "tk_resta", "*": "tk_mult",
    "/": "tk_div", "%": "tk_mod",
    "=": "tk_asig", "<": "tk_menor", ">": "tk_mayor",
}

WHITESPACE = {" ", "\t", "\r", "\n"}


def es_letra(cr): return cr.isalpha() or cr == "_"
def es_digito(cr): return cr.isdigit()
def es_id_parte(cr): return es_letra(cr) or es_digito(cr)

