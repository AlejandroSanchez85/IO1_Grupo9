"""
modelo/excepciones.py
=====================
Excepciones propias del modelo. La vista las captura y muestra un mensaje
claro sin que el programa se cierre.
"""
from __future__ import annotations


class ErrorValidacion(Exception):
    """Uno o varios datos ingresados no son válidos.

    ``errores`` es una lista de tuplas ``(mensaje, campo)``. El ``campo`` es
    un identificador que la vista entiende para resaltar la casilla con el
    error, por ejemplo ``("c", 0)`` = coeficiente de z de la variable 1, o
    ``("costo", 1, 2)`` = costo de la fila 2, columna 3.
    """

    def __init__(self, errores):
        self.errores = list(errores)
        super().__init__("\n".join(mensaje for mensaje, _ in self.errores))

    @property
    def mensajes(self):
        return [mensaje for mensaje, _ in self.errores]

    @property
    def campos(self):
        return [campo for _, campo in self.errores if campo is not None]


class ErrorArchivo(Exception):
    """No se pudo leer o escribir un archivo de problema (JSON)."""
