"""
vista/vogel/panel_graficas_vogel.py
===================================
Gráficas de transporte: red de envíos, costo por ruta, uso de la oferta,
demanda atendida y la penalización máxima de cada paso de Vogel.
"""
from __future__ import annotations

import tkinter as tk

from ..componentes import Aviso, DiagramaRed, GraficoBarras, MarcoDesplazable
from ..formato import FORMATO
from ..tema import COLORES, PALETA_GRAFICAS


def _tarjeta(contenedor, fila, columna, columnas=1):
    marco = tk.Frame(contenedor, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
    marco.grid(row=fila, column=columna, columnspan=columnas, sticky="nsew", padx=6, pady=6)
    return marco


class PanelGraficasVogel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.area = MarcoDesplazable(self, horizontal=False)
        self.area.pack(fill="both", expand=True)
        tk.Label(self.area.interior, text="Resuelva un problema para ver las gráficas.", bg=COLORES["fondo"],
                 fg=COLORES["texto_suave"]).pack(pady=40)

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.mostrar(self.resultado)

    def mostrar(self, resultado) -> None:
        self.resultado = resultado
        self.area.limpiar()
        r, p = resultado, resultado.problema
        u = p.unidad_producto
        contenedor = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=12, pady=10)
        contenedor.grid_columnconfigure(0, weight=1, uniform="g")
        contenedor.grid_columnconfigure(1, weight=1, uniform="g")
        formato = FORMATO.decimal
        if r.costo_total.tiene_m:
            caja = tk.Frame(contenedor, bg=COLORES["fondo"])
            caja.grid(row=0, column=0, columnspan=2, sticky="we", padx=6, pady=6)
            Aviso(caja, "advertencia", "Costos con M",
                  "La solución usa rutas con costo M; en las gráficas de costo solo se dibuja la parte numérica."
                  ).pack(fill="x")

        # 1) Red de transporte
        envios = [(i, j, float(x), f"{FORMATO.num(x)} {u}") for i, j, x, _ in r.envios()]
        alto_red = max(380, 70 * max(r.m, r.n) + 90)
        DiagramaRed(_tarjeta(contenedor, 1, 0, 2), "Red de distribución (solución de Vogel)", r.origenes, r.destinos,
                    [f"Oferta: {FORMATO.num(x)} {u}" for x in r.oferta],
                    [f"Demanda: {FORMATO.num(x)} {u}" for x in r.demanda], envios,
                    fila_ficticia=r.m - 1 if r.ficticio == "origen" else None,
                    columna_ficticia=r.n - 1 if r.ficticio == "destino" else None,
                    subtitulo="El grosor de cada flecha es proporcional a la cantidad enviada. Las líneas punteadas "
                              "son envíos ficticios.", alto=alto_red).pack(fill="both", expand=True)

        # 2) Costo por ruta
        rutas = [(f"{r.origenes[i]} → {r.destinos[j]}", costo) for i, j, x, costo in r.envios()
                 if not r.es_fila_ficticia(i) and not r.es_columna_ficticia(j)]
        if rutas:
            GraficoBarras(_tarjeta(contenedor, 2, 0, 2), f"Costo de cada ruta usada ({p.unidad_costo})",
                          [n for n, _ in rutas], [("Costo", [c.c for _, c in rutas], PALETA_GRAFICAS[0])],
                          etiqueta_y=p.unidad_costo,
                          subtitulo=f"Costo total = {FORMATO.num(r.costo_total)} {p.unidad_costo}",
                          formato=formato, alto=360).pack(fill="both", expand=True)

        # 3) Oferta usada por origen
        usadas = [sum((x for (a, j), x in r.asignaciones.items() if a == i and not r.es_columna_ficticia(j)), 0)
                  for i in range(r.m)]
        GraficoBarras(_tarjeta(contenedor, 3, 0), f"Oferta enviada vs. disponible ({u})", r.origenes,
                      [("Enviado", usadas, PALETA_GRAFICAS[2]), ("Oferta", r.oferta, "#CBD5E1")],
                      formato=formato).pack(fill="both", expand=True)
        # 4) Demanda atendida por destino
        atendidas = [sum((x for (i, b), x in r.asignaciones.items() if b == j and not r.es_fila_ficticia(i)), 0)
                     for j in range(r.n)]
        GraficoBarras(_tarjeta(contenedor, 3, 1), f"Demanda atendida vs. requerida ({u})", r.destinos,
                      [("Atendida", atendidas, PALETA_GRAFICAS[1]), ("Demanda", r.demanda, "#CBD5E1")],
                      formato=formato).pack(fill="both", expand=True)
        # 5) Penalización máxima por paso
        pasos = [paso for paso in r.pasos if paso.modo == "penalizacion"]
        if pasos:
            valores = []
            for paso in pasos:
                tipo, k = paso.linea
                info = paso.penalizaciones_filas[k] if tipo == "fila" else paso.penalizaciones_columnas[k]
                valores.append(info.penalizacion.c if not info.penalizacion.tiene_m else 0)
            GraficoBarras(_tarjeta(contenedor, 4, 0, 2), "Penalización máxima escogida en cada paso de Vogel",
                          [f"Paso {paso.numero}" for paso in pasos],
                          [("Penalización", valores, PALETA_GRAFICAS[3])],
                          subtitulo="Vogel atiende primero la línea donde equivocarse cuesta más (mayor penalización)."
                                    + (" Las penalizaciones con M se dibujan como 0." if any(
                                        (paso.penalizaciones_filas.get(paso.linea[1]) if paso.linea[0] == "fila" else
                                         paso.penalizaciones_columnas.get(paso.linea[1])).penalizacion.tiene_m
                                        for paso in pasos) else ""),
                          formato=formato).pack(fill="both", expand=True)
