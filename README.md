# Laboratorio #4
*Generador de Código de Tres Direcciones (C3D)*

## Instrucciones de ejecución 
Para ejecutar el generador de código de tres direcciones, se debe proporcionar como entrada un archivo fuente escrito en el lenguaje propuesto en clase. El programa procesará el archivo, generará su correspondiente Árbol de Sintaxis Abstracta (AST) y producirá un archivo de salida con extensión .tac que contiene el código de tres direcciones.

La ejecución se realiza desde el archivo principal (main), donde se solicita la ruta del archivo de entrada. Una vez procesado, el sistema imprime en consola el código generado y los posibles errores encontrados, además de guardar el archivo de salida. 

## Diseño del Generador C3D
El generador de código de tres direcciones está basado en un recorrido del AST mediante el patrón 'Visitor'. Cada tipo de nodo del árbol es procesado por un método específico que traduce la estructura de alto nivel a instrucciones de bajo nivel en formato de tres direcciones.

## Generación de Temporales
Los temporales se generan de manera incremental mediante un contador interno. Se hace mediante el método: `nuevo_temp()`

Cada vez que se requiere almacenar un resultado intermedio, se crea un nuevo temporal con el formato:

```
t1, t2, t3, ...
```

## Generación de Etiquetas
Las etiquetas se utilizan para el control de flujo (condicionales y ciclos). Se generan también de forma incremental con un contador independiente, en el método: `nueva_etiqueta()`

Estas etiquetas permiten representar saltos condicionales y no condicionales dentro del código generado y siguen el formato: 

```
L1, L2, L3, ...
```

## Traducción de Expresiones Booleanas
Las expresiones booleanas se traducen utilizando evaluación de corto circuito (short-circuit). Esto significa que:

- En expresiones con AND (&&), si la primera condición es falsa, no se evalúa la segunda.
- En expresiones con OR (||), si la primera condición es verdadera, no se evalúa la segunda.

Se generan etiquetas que controlan el flujo de evaluación, evitando cálculos innecesarios. 

## Limitaciones Conocidas
- No se realiza análisis semántico completo (verificación de tipos o variables no declaradas).
- No se maneja una tabla de símbolos, por lo que no se valida el uso correcto de identificadores.
- El soporte del lenguaje está limitado a asignaciones, expresiones aritméticas y booleanas, y estructuras de control básicas (if, if-else, while).
- No se optimiza el código generado (eliminación de código muerto o reducción de temporales).
- El manejo de errores permite continuar la ejecución, pero puede generar código incompleto si existen múltiples errores.