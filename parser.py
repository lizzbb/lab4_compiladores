import ply.yacc as yacc
from lexer import tokens

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'IG', 'NOIG'),
    ('left', 'MENOQ', 'MAYOQ', 'MAYQ', 'MENQ'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULT', 'DIV'),
    ('right', 'UMENOS')
)

errores_sintacticos = []

def p_error(p): 
    if p:
        errores_sintacticos.append(
            f"line {p.lineno}, col {p.lexpos}, token {p.type}, ERROR SINTÁCTICO: token inesperado: '{p.value}'"
        )
    else:
        errores_sintacticos.append("EOF inesperado: ERROR SINTÁCTICO")

# definición de gramática 
def p_programa(p):
    '''programa : lista_sentencias'''
    p[0] = ('programa', p[1])


def p_lista_sentencias(p):
    '''lista_sentencias : lista_sentencias sentencia
                        | sentencia'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_sentencia(p):
    '''sentencia : asignacion
                 | if
                 | while'''
    p[0] = p[1]

def p_asignacion(p):
    '''asignacion : ID IGUAL expresion PUNTOCOMA'''
    p[0] = ('asignacion', p[1], p[3])

def p_if(p):
    '''if : IF APAREN expresion CPAREN sentencia'''
    p[0] = ('if', p[3], p[5], None)

def p_if_else(p):
    '''if : IF APAREN expresion CPAREN sentencia ELSE sentencia'''
    p[0] = ('if', p[3], p[5], p[7])

def p_while(p):
    '''while : WHILE APAREN expresion CPAREN sentencia'''
    p[0] = ('while', p[3], p[5])

def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion MENQ expresion
                 | expresion MAYQ expresion
                 | expresion MENOQ expresion
                 | expresion MAYOQ expresion
                 | expresion IG expresion
                 | expresion NOIG expresion
                 | expresion AND expresion
                 | expresion OR expresion'''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expresion_umenos(p):
    '''expresion : MENOS expresion %prec UMENOS'''
    p[0] = ('umenos', p[2])

def p_expresion_paren(p):
    '''expresion : APAREN expresion CPAREN'''
    p[0] = p[2]

def p_expresion_not(p):
    '''expresion : NOT expresion'''
    p[0] = ('not', p[2])

def p_expresion_bool(p):
    '''expresion : TRUE
                 | FALSE'''
    p[0] = ('bool', p[1])

def p_expresion_num(p):
    '''expresion : NUM'''
    p[0] = ('num', p[1])

def p_expresion_id(p):
    '''expresion : ID'''
    p[0] = ('id', p[1])

# creación de parser con ply.yacc
parser = yacc.yacc()