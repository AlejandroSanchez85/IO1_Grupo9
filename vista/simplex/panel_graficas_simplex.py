"""
vista/simplex/panel_graficas_simplex.py
=======================================
Gráficas del Simplex: evolución de z por iteración, valores óptimos,
aporte de cada variable a z, uso de recursos y precios sombra.
"""
from __future__ import annotations

import tkinter as tk

from ..componentes import Aviso, GraficoBarras, GraficoLineas, MarcoDesplazable
from ..formato import FORMATO
from ..tema import COLORES, PALETA_GRAFICAS
from .panel_iteraciones_simplex import lista_iteraciones


def _tarjeta(contenedor, fila, columna, columnas=1):
    marco = tk.Frame(contenedor, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
    marco.grid(row=fila, column=columna, columnspan=columnas, sticky="nsew", padx=6, pady=6)
    return marco


class PanelGraficasSimplex(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.sensibilidad = None
        self.area = MarcoDesplazable(self, horizontal=False)
        self.area.pack(fill="both", expand=True)
        tk.Label(self.area.interior, text="Resuelva un problema para ver las gráficas.", bg=COLORES["fondo"],
                 fg=COLORES["texto_suave"]).pack(pady=40)

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.mostrar(self.resultado, self.sensibilidad)

    def mostrar(self, resultado, sensibilidad=None) -> None:
        self.resultado, self.sensibilidad = resultado, sensibilidad
        self.area.limpiar()
        p = resultado.problema
        contenedor = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=12, pady=10)
        contenedor.grid_columnconfigure(0, weight=1, uniform="g")
        contenedor.grid_columnconfigure(1, weight=1, uniform="g")
        formato = FORMATO.decimal

        # 1) Evolución de z
        elementos = lista_iteraciones(resultado)
        etiquetas = [("Alt." if it.estado == "alternativa" else f"T{it.numero}") for it in elementos]
        GraficoLineas(_tarjeta(contenedor, 0, 0, 2), f"Evolución de z en cada tabla ({p.unidad_z})", etiquetas,
                      [it.tabla.z for it in elementos], etiqueta_y=p.unidad_z,
                      subtitulo="Cada punto es el valor de z de una tabla del Simplex. El último es el resultado "
                                "final.", formato=formato).pack(fill="both", expand=True)
        if not resultado.es_optimo:
            caja = tk.Frame(contenedor, bg=COLORES["fondo"])
            caja.grid(row=1, column=0, columnspan=2, sticky="we", padx=6, pady=6)
            Aviso(caja, "error" if resultado.estado == "no_acotado" else "advertencia", "Sin solución óptima",
                  "Como el problema no tiene solución óptima finita, solo se muestra la evolución de z.").pack(fill="x")
            return

        t = resultado.tabla_final
        nombres = [v.nombre for v in p.variables]
        valores = [t.valor(j) for j in range(p.n)]
        # 2) Valores óptimos
        GraficoBarras(_tarjeta(contenedor, 1, 0), "Plan óptimo: valor de cada variable", nombres,
                      [("Valor óptimo", valores, PALETA_GRAFICAS[0])],
                      subtitulo="Unidades: " + "; ".join(f"{v.nombre} en {v.unidad}" for v in p.variables),
                      formato=formato).pack(fill="both", expand=True)
        # 3) Aporte a z
        aportes = [p.variables[j].coeficiente * valores[j] for j in range(p.n)]
        GraficoBarras(_tarjeta(contenedor, 1, 1), f"Aporte de cada variable a z ({p.unidad_z})", nombres,
                      [("c_j · x_j", aportes, PALETA_GRAFICAS[2])], etiqueta_y=p.unidad_z,
                      subtitulo=f"La suma de las barras es z* = {FORMATO.num(t.z)} {p.unidad_z}.",
                      formato=formato).pack(fill="both", expand=True)
        # 4) Uso de recursos
        recursos = [r.nombre for r in p.restricciones]
        usados = [r.lado_derecho - t.valor(p.n + i) for i, r in enumerate(p.restricciones)]
        GraficoBarras(_tarjeta(contenedor, 2, 0, 2), "Uso de cada recurso: usado vs. disponible", recursos,
                      [("Usado", usados, PALETA_GRAFICAS[0]), ("Disponible (b_i)", [r.lado_derecho for r in
                                                                                    p.restricciones],
                                                               "#CBD5E1")],
                      subtitulo="Si la barra de 'Usado' iguala a 'Disponible', la restricción está activa "
                                "(cuello de botella). Unidades: " + "; ".join(f"{r.nombre} en {r.unidad}"
                                                                             for r in p.restricciones),
                      formato=formato, alto=360).pack(fill="both", expand=True)
        # 5) Precios sombra
        if sensibilidad is not None:
            GraficoBarras(_tarjeta(contenedor, 3, 0, 2), f"Precio sombra de cada recurso ({p.unidad_z} por unidad)",
                          recursos, [("Precio sombra", sensibilidad.precios_sombra, PALETA_GRAFICAS[3])],
                          subtitulo="Cuánto cambiaría z con una unidad más de cada recurso (0 = recurso que sobra).",
                          formato=formato).pack(fill="both", expand=True)
