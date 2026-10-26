"""
vista/vogel/panel_pasos_vogel.py
================================
* PanelPasosVogel: PASO A PASO de Vogel con navegación. Cada paso muestra
  las penalizaciones de filas y columnas, la línea escogida, la celda
  escogida, la asignación y la línea tachada; debajo, la explicación.
* PanelTodosPasosVogel: todas las tablas de los pasos, una debajo de otra.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..componentes import Leyenda, MarcoDesplazable, TablaTransporteCanvas, TextoRico, etiqueta
from ..explicaciones import textos_transporte as TT
from ..formato import FORMATO
from ..tema import COLORES, FUENTES

LEYENDA_VOGEL = [(COLORES["elegida"], "Celda escogida en el paso"), (COLORES["asignada"], "Celda ya asignada"),
                 (COLORES["linea_elegida"], "Línea de mayor penalización"), (COLORES["primario"], "Penalización mayor"),
                 (COLORES["tachado"], "Línea tachada"), (COLORES["ficticio"], "Ficticio"),
                 (COLORES["prohibida"], "Ruta prohibida (M)")]


class PanelPasosVogel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.indice = 0
        self.var_selector = tk.StringVar()
        barra = tk.Frame(self, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
        barra.pack(fill="x")
        caja = tk.Frame(barra, bg=COLORES["superficie"])
        caja.pack(fill="x", padx=12, pady=8)
        self.boton_primera = ttk.Button(caja, text="◄◄", width=4, style="Chico.TButton", command=lambda: self.ir(0))
        self.boton_primera.pack(side="left")
        self.boton_anterior = ttk.Button(caja, text="◄ Anterior", style="Chico.TButton",
                                         command=lambda: self.ir(self.indice - 1))
        self.boton_anterior.pack(side="left", padx=4)
        self.selector = ttk.Combobox(caja, textvariable=self.var_selector, state="readonly", width=46)
        self.selector.pack(side="left", padx=4)
        self.selector.bind("<<ComboboxSelected>>", lambda e: self.ir(self.selector.current()))
        self.boton_siguiente = ttk.Button(caja, text="Siguiente ►", style="Chico.TButton",
                                          command=lambda: self.ir(self.indice + 1))
        self.boton_siguiente.pack(side="left", padx=4)
        self.boton_ultima = ttk.Button(caja, text="►►", width=4, style="Chico.TButton",
                                       command=lambda: self.ir(len(self.resultado.pasos) - 1 if self.resultado else 0))
        self.boton_ultima.pack(side="left")
        self.etiqueta_posicion = etiqueta(caja, "", "base_negrita", "primario")
        self.etiqueta_posicion.pack(side="right")
        Leyenda(barra, LEYENDA_VOGEL).pack(fill="x", padx=14, pady=(0, 8))

        self.paneles = ttk.Panedwindow(self, orient="vertical")
        self.paneles.pack(fill="both", expand=True, pady=(6, 0))
        arriba = tk.Frame(self.paneles, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                          highlightthickness=1)
        self.titulo = tk.Label(arriba, text="Resuelva un problema para ver el paso a paso.", font=FUENTES["h3"],
                               bg=COLORES["superficie"], fg=COLORES["texto"], anchor="w")
        self.titulo.pack(fill="x", padx=14, pady=(10, 4))
        self.area_tabla = MarcoDesplazable(arriba, fondo=COLORES["superficie"], ajustar_ancho=False)
        self.area_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        abajo = tk.Frame(self.paneles, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                         highlightthickness=1)
        self.explicacion = TextoRico(abajo, alto=12)
        self.explicacion.pack(fill="both", expand=True)
        self.paneles.add(arriba, weight=3)
        self.paneles.add(abajo, weight=3)
        self._actualizar_botones()

    def mostrar(self, resultado) -> None:
        self.resultado = resultado
        self.selector.configure(values=[TT.titulo_paso(resultado, k) for k in range(len(resultado.pasos))])
        self.ir(0)
        self.after(120, self._ajustar_division)

    def _ajustar_division(self) -> None:
        try:
            alto_total = self.paneles.winfo_height()
            alto_tabla = self.area_tabla.interior.winfo_reqheight() + self.titulo.winfo_reqheight() + 40
            if alto_total > 200:
                self.paneles.sashpos(0, max(180, min(alto_tabla, int(alto_total * 0.62))))
        except tk.TclError:
            pass

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.ir(self.indice)

    def ir(self, indice: int) -> None:
        if self.resultado is None or not self.resultado.pasos:
            return
        indice = max(0, min(indice, len(self.resultado.pasos) - 1))
        self.indice = indice
        self.selector.current(indice)
        self.titulo.configure(text=TT.titulo_paso(self.resultado, indice))
        self.etiqueta_posicion.configure(text=f"Paso {indice + 1} de {len(self.resultado.pasos)}")
        self.area_tabla.limpiar()
        TablaTransporteCanvas(self.area_tabla.interior, **TT.datos_tabla_paso(self.resultado, indice, FORMATO)).pack(
            anchor="nw", padx=4, pady=4)
        self.explicacion.mostrar(TT.bloques_paso(self.resultado, indice, FORMATO))
        self._actualizar_botones()

    def _actualizar_botones(self):
        total = len(self.resultado.pasos) if self.resultado else 0
        atras = "normal" if total and self.indice > 0 else "disabled"
        adelante = "normal" if total and self.indice < total - 1 else "disabled"
        self.boton_primera.configure(state=atras)
        self.boton_anterior.configure(state=atras)
        self.boton_siguiente.configure(state=adelante)
        self.boton_ultima.configure(state=adelante)


class PanelTodosPasosVogel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        Leyenda(self, LEYENDA_VOGEL, fondo=COLORES["fondo"]).pack(fill="x", padx=16, pady=(8, 2))
        self.area = MarcoDesplazable(self, ajustar_ancho=False)
        self.area.pack(fill="both", expand=True)

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.mostrar(self.resultado)

    def mostrar(self, resultado) -> None:
        self.resultado = resultado
        self.area.limpiar()
        r = resultado
        for k, paso in enumerate(r.pasos):
            tarjeta = tk.Frame(self.area.interior, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                               highlightthickness=1)
            tarjeta.pack(fill="x", anchor="w", padx=16, pady=8)
            tk.Label(tarjeta, text=TT.titulo_paso(r, k), font=FUENTES["h3"], bg=COLORES["superficie"],
                     fg=COLORES["primario_texto"], anchor="w").pack(fill="x", padx=12, pady=(10, 4))
            TablaTransporteCanvas(tarjeta, **TT.datos_tabla_paso(r, k, FORMATO)).pack(anchor="w", padx=12)
            i, j = paso.celda
            resumen = (f"Celda {TT.nombre_celda(r, paso.celda)} · costo {FORMATO.num(paso.costo)} · se asignan "
                       f"{FORMATO.num(paso.cantidad)} {r.problema.unidad_producto} · se tacha la "
                       f"{TT.nombre_linea(r, paso.tachada)}")
            if paso.linea is not None and paso.modo == "penalizacion":
                resumen = f"Mayor penalización en la {TT.nombre_linea(r, paso.linea)} · " + resumen
            if paso.empate_lineas:
                resumen += " · EMPATE de penalización"
            if paso.simultaneo and len(paso.filas_activas) + len(paso.columnas_activas) > 2:
                resumen += " · DEGENERACIÓN (fila y columna a la vez)"
            tk.Label(tarjeta, text=resumen, font=FUENTES["base"], bg=COLORES["superficie"], fg=COLORES["texto_suave"],
                     anchor="w", justify="left", wraplength=1100).pack(fill="x", padx=12, pady=(6, 10))
