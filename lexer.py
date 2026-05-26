import ply.lex as lex

tokens = (
    'ID', 
    'NUM',
    'TRUE', 
    'FALSE', 
    'OR', 
    'AND', 
    'NOT',
    'IF', 
    'ELSE', 
    'WHILE', 
    'APAREN', 
    'CPAREN', 
    'PUNTOCOMA',
    'IGUAL',
    'MAS', 
    'MENOS', 
    'MULT', 
    'DIV', 
    'MAYQ', 
    'MENQ', 
    'MAYOQ', 
    'MENOQ', 
    'IG', 
    'NOIG'
)

#palabras reservadas mapeo de las cadenas exactas al tipo de token esperado
RESERVADAS = {
     'true': 'TRUE', 'false': 'FALSE', 'if': 'IF', 'else': 'ELSE', 'while': 'WHILE'}

#def tokens
class Token:
    def __init__(self, tipo, valor, linea, col_inicio, col_fin):
        self.tipo = tipo #id token
        self.valor = valor #lexema
        self.linea = linea
        self.col_inicio = col_inicio
        self.col_fin = col_fin

    def __repr__(self):
        return f"<{self.tipo}, {self.valor}, {self.linea}, {self.col_inicio}, {self.col_fin}>"

class Lexer: 
    #scanner
    #se recorre caracter por caracter
    def __init__(self, fuente=None):
        self.fuente = fuente #codigo fuente, entrada, a string
        self.pos = 0 #indice global del caracter actual
        self.linea_actual = 1 #contador
        self.columna_actual = 1 #contador
        self.tokens = [] #lista de tokens validos
        self.errores = [] #lista de err lexicos 
        self.pila_indentacion = [0] #pila de estado
        self.limite_indentacion = 5
        self.indice_token_actual = 0
    
    # conversión de Token a formato LexToken para uso con ply.yacc
    def convertir_LexToken(self, t): 
        tok = lex.LexToken()
        tok.type = t.tipo
        tok.value = t.valor
        tok.lineno = t.linea
        tok.lexpos = t.col_inicio
        return tok

    def token(self): 
        while self.indice_token_actual < len(self.tokens): 
            t = self.tokens[self.indice_token_actual]
            self.indice_token_actual += 1

            # ignorar tokens que no se usarán para análisis sintáctico
            if t.tipo in ('NEWLINE'): 
                continue
            
            return self.convertir_LexToken(t)
        return None

    def input(self, fuente): 
        self.fuente = fuente #codigo fuente, entrada, a string
        self.pos = 0 #indice global del caracter actual
        self.linea_actual = 1 #contador
        self.columna_actual = 1 #contador
        self.tokens = [] #lista de tokens validos
        self.errores_lexicos = [] #lista de err lexicos 
        self.pila_indentacion = [0] #pila de estado
        self.indice_token_actual = 0
    
        self._tokenizar_todo()

    
    def reportar_error(self, mensaje):
        #no lanza excepciones solo guarda el error para que la ejecucion continue
        err = f"line {self.linea_actual}, col {self.columna_actual}: ERROR LEXICO: {mensaje}"
        self.errores.append(err)
    
    def _tokenizar_todo(self):
        #separa el texto por líneas manteniendo el salto de línea al final
        lineas = self.fuente.splitlines(keepends=True)
        
        for num_linea, contenido in enumerate(lineas, 1):
            self.linea_actual = num_linea
            self.columna_actual = 1
            self.pos = 0 #reiniciamos la posicion del puntero de lectura de la linea
            
            if not contenido.strip():
                # ignorar lineas vacias
                continue

            idx = 0
            # manejar resto de la linea
            self.pos = idx #mov indice global hasta la  ultima indent
            self.columna_actual = idx + 1
            
            #se lee caracter por caracter consumeindo la linea
            while self.pos < len(contenido):
                char = contenido[self.pos]

                #si no son incio de linea ignorar espacios en blanco entre lexemas
                if char.isspace() and char != '\n':
                    self.avanzar()
                    continue

                #emitir token NEWLINE si salto de linea 
                if char == '\n':
                    self.tokens.append(Token('NEWLINE', '\\n', self.linea_actual, self.columna_actual, self.columna_actual))
                    self.avanzar()
                    continue

                # operadores dobles usando lookahead
                proximo = contenido[self.pos + 1] if self.pos + 1 < len(contenido) else ""
                if char == '=' and proximo == '=':
                    self.agregar_token('IG', '==', 2)
                    continue
                if char == '!' and proximo == '=':
                    self.agregar_token('NOIG', '!=', 2)
                    continue
                if char == '>' and proximo == '=':
                    self.agregar_token('MAYOQ', '>=', 2)
                    continue
                if char == '<' and proximo == '=':
                    self.agregar_token('MENOQ', '<=', 2)
                    continue
                if char == '&' and proximo == '&': 
                    self.agregar_token('AND', '&&', 2)
                    continue
                if char == '|' and proximo == '|': 
                    self.agregar_token('OR', '||', 2)
                    continue

                # operadores y puntuacion
                simples = {
                    '+': 'MAS', '-': 'MENOS', '*': 'MULT', '/': 'DIV', '(': 'APAREN', ')': 'CPAREN', ';': 'PUNTOCOMA', '=': 'IGUAL', '>': 'MAYQ', '<': 'MENQ', '!': 'NOT'
                }

                if char in simples:
                    self.agregar_token(simples[char], char)
                    continue

                #ver literales numericas
                if char.isdigit():
                    self.manejar_numero(contenido)
                    continue

                #ver id y reservadas
                if char.isalpha() or char == '_':
                    self.manejar_id(contenido)
                    continue

                #si caracter fuera del lenguaje error lexico
                self.reportar_error(f"carácter inesperado '{char}'")
                #forzar continuacion del analisis
                self.avanzar()

    def avanzar(self, n=1):
        #mov fila y columan
        self.pos += n
        self.columna_actual += n

    def agregar_token(self, tipo, valor, longitud=1):
        #registrar token avanzando puntero
        self.tokens.append(Token(tipo, valor, self.linea_actual, self.columna_actual, self.columna_actual + longitud - 1))
        self.avanzar(longitud)

    def manejar_numero(self, contenido):
        #acepta digitos considerando un punto como decimal
        inicio_col = self.columna_actual
        lexema = ""
        while self.pos < len(contenido) and contenido[self.pos].isdigit():
            lexema += contenido[self.pos]
            self.avanzar()
        
        self.tokens.append(Token('NUM', lexema, self.linea_actual, inicio_col, self.columna_actual - 1))

    def manejar_id(self, contenido):
        #lee letras numeros y guiones bajo
        inicio_col = self.columna_actual
        lexema = ""
        while self.pos < len(contenido) and (contenido[self.pos].isalnum() or contenido[self.pos] == '_'):
            lexema += contenido[self.pos]
            self.avanzar()
        
        #ver id>31 o error de tamaño
        if len(lexema) > 31:
            self.reportar_error(f"identificador invalido: {lexema[:31]}")
            lexema = lexema[:31]

        #si no es reservada es id
        tipo = RESERVADAS.get(lexema, 'ID')
        self.tokens.append(Token(tipo, lexema, self.linea_actual, inicio_col, self.columna_actual - 1))