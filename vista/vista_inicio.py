"""
vista/vista_inicio.py
=====================
Pantalla de inicio: presenta el proyecto, los dos métodos del grupo y lo
que exige la guía del proyecto (lista de cumplimiento).
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .componentes import MarcoDesplazable
from .tema import COLORES, FUENTES


class VistaInicio(tk.Frame):
    def __init__(self, master, navegar):
        super().__init__(master, bg=COLORES["fondo"])
        self.navegar = navegar
        marco = MarcoDesplazable(self, horizontal=False)
        marco.pack(fill="both", expand=True)
        c = tk.Frame(marco.interior, bg=COLORES["fondo"])
        c.pack(fill="both", expand=True, padx=24, pady=20)

        portada = tk.Frame(c, bg=COLORES["primario"])
        portada.pack(fill="x")
        tk.Label(portada, text="Software de Investigación de Operaciones I", font=FUENTES["titulo"],
                 bg=COLORES["primario"], fg="#FFFFFF", anchor="w").pack(fill="x", padx=28, pady=(24, 2))
        tk.Label(portada, text="Grupo 9 · Método Simplex (maximizar y minimizar)",
                 font=FUENTES["subtitulo"], bg=COLORES["primario"], fg=COLORES["primario_suave"], anchor="w").pack(fill="x", padx=28)
        descripcion = tk.Label(portada, text=("Resuelve cualquier problema que usted escriba, muestra todo el procedimiento paso a paso con "
                                              "tablas, avisa los casos especiales y explica el resultado con los "
                                              "nombres y unidades del problema."),
                               font=FUENTES["base"], bg=COLORES["primario"], fg="#FFFFFF", anchor="w", justify="left",
                               wraplength=600)
        descripcion.pack(fill="x", padx=28, pady=(10, 24))
        portada.bind("<Configure>", lambda e: descripcion.configure(wraplength=max(300, e.width - 80)), add="+")

        fila = tk.Frame(c, bg=COLORES["fondo"])
        fila.pack(fill="x", pady=16)
        fila.grid_columnconfigure(0, weight=1, uniform="m")
        self._tarjeta_metodo(fila, 0, "Método Simplex", "Programación lineal · maximizar o minimizar",
                             ["Hasta 8 variables y 8 restricciones (≤).",
                              "Cada tabla con la variable que entra, la que sale y el pivote.",
                              "Cálculo de Zj y Cj − Zj y operaciones de fila explicadas.",
                              "Avisa: no acotado, óptimos alternativos y degeneración.",
                              "Análisis de sensibilidad: precios sombra, costos reducidos, rangos de c_j y b_i."],
                             "Abrir Simplex", lambda: self.navegar("simplex"))

    def _tarjeta_metodo(self, fila, columna, titulo, subtitulo, puntos, texto_boton, comando):
        tarjeta = tk.Frame(fila, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
        tarjeta.grid(row=0, column=columna, sticky="nsew", padx=(0, 12) if columna == 0 else (12, 0))
        tk.Frame(tarjeta, bg=COLORES["primario"] if columna == 0 else COLORES["secundario"], height=5).pack(fill="x")
        tk.Label(tarjeta, text=titulo, font=FUENTES["h2"], bg=COLORES["superficie"], fg=COLORES["texto"],
                 anchor="w").pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(tarjeta, text=subtitulo, font=FUENTES["pequena"], bg=COLORES["superficie"],
                 fg=COLORES["texto_suave"], anchor="w").pack(fill="x", padx=20)
        for punto in puntos:
            tk.Label(tarjeta, text="•  " + punto, font=FUENTES["base"], bg=COLORES["superficie"], fg=COLORES["texto"],
                     anchor="w", justify="left", wraplength=400).pack(fill="x", padx=24, pady=2)
        ttk.Button(tarjeta, text=texto_boton + "  ►", style="Primario.TButton", command=comando).pack(
            anchor="w", padx=20, pady=(12, 18))
