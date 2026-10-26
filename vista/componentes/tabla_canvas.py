"""
vista/componentes/tabla_canvas.py
=================================
Tabla dibujada en un Canvas. Permite colorear CADA celda (columna pivote,
fila pivote, elemento pivote, valores óptimos...), cosa que el Treeview de
Tkinter no permite. El tamaño de las columnas se calcula con el texto.
"""
from __future__ import annotations

import tkinter as tk

from ..tema import COLORES, FUENTES


class TablaCanvas(tk.Canvas):
    """Tabla con estilos por celda.

    Parámetros
    ----------
    filas : list[list[str]]       textos de la tabla (pueden tener saltos de línea).
    filas_encabezado : int        cuántas filas iniciales son encabezado (fondo oscuro).
    columnas_encabezado : int     cuántas columnas iniciales son rótulos (fondo gris).
    estilos : dict                {(fila, col): {"bg":..., "fg":..., "negrita": bool}}
    estilos_fila / estilos_columna: estilos para filas o columnas completas (del cuerpo).
    alinear : dict                {col: "w" | "e" | "center"}
    """

    def __init__(self, master, filas, filas_encabezado: int = 1, columnas_encabezado: int = 1,
                 estilos=None, estilos_fila=None, estilos_columna=None, alinear=None,
                 ancho_minimo: int = 54, ancho_maximo: int = 420, relleno_x: int = 10,
                 relleno_y: int = 6, fondo: str | None = None, **kwargs):
        super().__init__(master, bg=fondo or COLORES["superficie"], highlightthickness=0, bd=0, **kwargs)
        self.filas = [[("" if v is None else str(v)) for v in fila] for fila in filas]
        self.filas_encabezado = filas_encabezado
        self.columnas_encabezado = columnas_encabezado
        self.estilos = estilos or {}
        self.estilos_fila = estilos_fila or {}
        self.estilos_columna = estilos_columna or {}
        self.alinear = alinear or {}
        self.ancho_minimo, self.ancho_maximo = ancho_minimo, ancho_maximo
        self.relleno_x, self.relleno_y = relleno_x, relleno_y
        self.dibujar()

    def _estilo(self, r: int, c: int) -> dict:
        es_encabezado = r < self.filas_encabezado
        if es_encabezado:
            estilo = {"bg": COLORES["tabla_encabezado"], "fg": COLORES["tabla_encabezado_texto"],
                      "negrita": True}
        elif c < self.columnas_encabezado:
            estilo = {"bg": COLORES["tabla_lateral"], "fg": COLORES["texto"], "negrita": True}
        else:
            par = (r - self.filas_encabezado) % 2 == 0
            estilo = {"bg": COLORES["tabla_par"] if par else COLORES["tabla_impar"],
                      "fg": COLORES["texto"], "negrita": False}
        if not es_encabezado:
            if c in self.estilos_columna and c >= self.columnas_encabezado:
                estilo.update(self.estilos_columna[c])
            if r in self.estilos_fila:
                estilo.update(self.estilos_fila[r])
        if (r, c) in self.estilos:
            estilo.update(self.estilos[(r, c)])
        return estilo

    def dibujar(self) -> None:
        self.delete("all")
        if not self.filas:
            self.configure(width=1, height=1)
            return
        normal, negrita = FUENTES["tabla"], FUENTES["tabla_negrita"]
        alto_linea = negrita.metrics("linespace")
        columnas = max(len(f) for f in self.filas)
        for fila in self.filas:
            fila.extend([""] * (columnas - len(fila)))

        # Ancho de cada columna según el texto más largo
        anchos = []
        for c in range(columnas):
            ancho = self.ancho_minimo
            for r, fila in enumerate(self.filas):
                fuente = negrita if self._estilo(r, c).get("negrita") else normal
                for linea in fila[c].split("\n"):
                    ancho = max(ancho, fuente.measure(linea) + 2 * self.relleno_x)
            anchos.append(min(ancho, self.ancho_maximo))
        altos = [max(len(v.split("\n")) for v in fila) * alto_linea + 2 * self.relleno_y
                 for fila in self.filas]

        y = 0
        for r, fila in enumerate(self.filas):
            x = 0
            for c, valor in enumerate(fila):
                estilo = self._estilo(r, c)
                x1, y1 = x + anchos[c], y + altos[r]
                self.create_rectangle(x, y, x1, y1, fill=estilo["bg"],
                                      outline=estilo.get("borde", COLORES["tabla_rejilla"]))
                alineacion = estilo.get("alinear", self.alinear.get(c, "center"))
                if alineacion == "w":
                    tx, ancla = x + self.relleno_x, "w"
                elif alineacion == "e":
                    tx, ancla = x1 - self.relleno_x, "e"
                else:
                    tx, ancla = (x + x1) / 2, "center"
                self.create_text(tx, (y + y1) / 2, text=valor, anchor=ancla, fill=estilo["fg"],
                                 font=negrita if estilo.get("negrita") else normal,
                                 justify="center" if ancla == "center" else "left",
                                 width=self.ancho_maximo - 2 * self.relleno_x)
                x = x1
            y += altos[r]
        self.configure(width=sum(anchos) + 1, height=sum(altos) + 1)
        self.anchos, self.altos = anchos, altos
