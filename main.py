import os
from lexer import Lexer
from parser import parser
from parser import errores_sintacticos
from GeneradorC3D import GeneradorC3D

lexer = Lexer()

# Carpeta de outputs de .tac (codigo 3 direcciones)
TAC_DIR = os.path.join(os.path.dirname(__file__), "tac_outputs")

def ensure_dirs():
    os.makedirs(TAC_DIR, exist_ok=True)


def leer_archivo(ruta): 
    with open(ruta, "r", encoding="utf-8") as f: 
        contenido = f.readlines()
    return contenido

def escribir_archivo(ruta, contenido): 
    with open(ruta, "w", encoding="utf-8") as f: 
        f.write(contenido)

def procesar_archivo(ruta): 
    ensure_dirs()

    lineas = leer_archivo(ruta)
    codigo = "".join(lineas)

    base = os.path.basename(ruta).rsplit('.', 1)[0]

    # limpiar errores antes
    errores_sintacticos.clear()
    lexer.errores = []

    ast = parser.parse(input=codigo, lexer=lexer, debug=False)

    # generar .tac 
    generador = GeneradorC3D()
    generador.visitar(ast)

    tac = "\n".join(generador.codigo)
    ruta_tac = os.path.join(TAC_DIR, f"{base}.tac")

    escribir_archivo(ruta_tac, tac)
    
    print("\nArchivo output de C3D (.tac) generado.")

    errores = lexer.errores + errores_sintacticos + generador.errores

    return {
        "ast": ast,
        "tac": tac,
        "errores": errores
    }

if __name__ == "__main__": 
    op = 0
    codigo = ""
    errores = []

    while op != 3: 
        print("\nMENU")
        print("1) Leer archivo y generar TAC")
        print("2) Mostrar errores")
        print("3) Salir")

        op = int(input("-> "))

        if op == 1: 
            print("Ingrese ruta de archivo:")
            ruta = input(". ")

            resultado = procesar_archivo(ruta)

            codigo = resultado["tac"] 

            print("\nCODIGO 3 DIRECCIONES GENERADO")
            print(codigo)

        elif op == 2: 
            print("\nERRORES")
            errores = resultado["errores"]
            if not errores:
                print("No hay errores.")
            else:
                for err in errores:
                    print(err)
        
        elif op == 3:
            break