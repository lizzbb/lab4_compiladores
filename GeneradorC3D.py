class GeneradorC3D:

    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.codigo = []
        self.errores = []

    def nuevo_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def nueva_etiqueta(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emitir(self, instruccion):
        self.codigo.append(instruccion)
    
    def reportar_error(self, msg):
        self.errores.append(msg)

    def visitar(self, nodo):
        if nodo is None:
            return None

        if isinstance(nodo, list):
            for n in nodo:
                self.visitar(n)
            return None

        metodo = getattr(self, f"visitar_{nodo[0]}", self.visitar_generico)
        return metodo(nodo)

    def visitar_generico(self, nodo):
        pass
    
    # expresiones
    def visitar_num(self, nodo):
        return str(nodo[1])

    def visitar_id(self, nodo):
        return nodo[1]

    def visitar_bool(self, nodo):
        return '1' if nodo[1] == 'true' else '0'

    # operaciones 
    def visitar_binop(self, nodo):
        _, op, izq, der = nodo

        if op in ['&&', '||']:
            self.reportar_error("Uso incorrecto de operador lógico en contexto aritmético")
            return None

        t1 = self.visitar(izq)
        t2 = self.visitar(der)

        if t1 is None or t2 is None:
            return None

        temp = self.nuevo_temp()
        self.emitir(f"{temp} = {t1} {op} {t2}")
        return temp

    def visitar_not(self, nodo):
        val = self.visitar(nodo[1])
        if val is None:
            return None

        temp = self.nuevo_temp()
        self.emitir(f"{temp} = !{val}")
        return temp

    def visitar_umenos(self, nodo):
        val = self.visitar(nodo[1])
        if val is None:
            return None

        temp = self.nuevo_temp()
        self.emitir(f"{temp} = -{val}")
        return temp

    # booleanos
    def visitar_bool_expr(self, nodo, Ltrue, Lfalse):
        metodo = getattr(self, f"bool_{nodo[0]}", None)

        if metodo:
            metodo(nodo, Ltrue, Lfalse)
        else:
            temp = self.visitar(nodo)
            if temp is None:
                return

            self.emitir(f"if {temp} goto {Ltrue}")
            self.emitir(f"goto {Lfalse}")

    def bool_binop(self, nodo, Ltrue, Lfalse):
        _, op, izq, der = nodo

        # RELACIONALES
        if op in ['<', '>', '<=', '>=', '==', '!=']:
            t1 = self.visitar(izq)
            t2 = self.visitar(der)

            if t1 is None or t2 is None:
                return

            self.emitir(f"if {t1} {op} {t2} goto {Ltrue}")
            self.emitir(f"goto {Lfalse}")
        
        # AND
        elif op == '&&':
            Lmid = self.nueva_etiqueta()

            self.visitar_bool_expr(izq, Lmid, Lfalse)

            self.emitir(f"{Lmid}:")
            self.visitar_bool_expr(der, Ltrue, Lfalse)

        # OR
        elif op == '||':
            Lmid = self.nueva_etiqueta()

            self.visitar_bool_expr(izq, Ltrue, Lmid)

            self.emitir(f"{Lmid}:")
            self.visitar_bool_expr(der, Ltrue, Lfalse)

        else:
            self.reportar_error(f"Operador no soportado: {op}")
    
    def bool_not(self, nodo, Ltrue, Lfalse):
        _, expr = nodo
        self.visitar_bool_expr(expr, Lfalse, Ltrue)
    
    def bool_bool(self, nodo, Ltrue, Lfalse):
        if nodo[1] == 'true':
            self.emitir(f"goto {Ltrue}")
        else:
            self.emitir(f"goto {Lfalse}")

    def bool_id(self, nodo, Ltrue, Lfalse):
        val = nodo[1]
        self.emitir(f"if {val} goto {Ltrue}")
        self.emitir(f"goto {Lfalse}")

    def bool_num(self, nodo, Ltrue, Lfalse):
        if nodo[1] != 0:
            self.emitir(f"goto {Ltrue}")
        else:
            self.emitir(f"goto {Lfalse}")
    
    # sentencias
    def visitar_programa(self, nodo):
        _, lista = nodo
        for stmt in lista:
            self.visitar(stmt)

    def visitar_asignacion(self, nodo):
        _, nombre, expr = nodo

        valor = self.visitar(expr)

        if valor is None:
            self.reportar_error(f"No se pudo asignar a '{nombre}' por error en expresión")
            return

        self.emitir(f"{nombre} = {valor}")

    def visitar_bloque(self, nodo):
        _, lista = nodo
        for stmt in lista:
            self.visitar(stmt)

    # de control
    def visitar_if(self, nodo):
        _, cond, then, else_ = nodo

        Ltrue = self.nueva_etiqueta()
        Lfalse = self.nueva_etiqueta()
        Lend = self.nueva_etiqueta()

        self.visitar_bool_expr(cond, Ltrue, Lfalse)

        self.emitir(f"{Ltrue}:")
        self.visitar(then)
        self.emitir(f"goto {Lend}")

        self.emitir(f"{Lfalse}:")
        if else_:
            self.visitar(else_)

        self.emitir(f"{Lend}:")
    
    def visitar_while(self, nodo):
        _, cond, cuerpo = nodo

        Linicio = self.nueva_etiqueta()
        Ltrue = self.nueva_etiqueta()
        Lfalse = self.nueva_etiqueta()

        self.emitir(f"{Linicio}:")

        self.visitar_bool_expr(cond, Ltrue, Lfalse)

        self.emitir(f"{Ltrue}:")
        self.visitar(cuerpo)
        self.emitir(f"goto {Linicio}")

        self.emitir(f"{Lfalse}:")
