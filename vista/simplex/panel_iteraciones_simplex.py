"""
vista/simplex/panel_iteraciones_simplex.py
==========================================
* PanelIteracionesSimplex: PASO A PASO con navegación (anterior/siguiente).
  Muestra la tabla de cada iteración con la columna pivote, la fila pivote
  y el elemento pivote resaltados, y debajo la explicación completa.
* PanelTodasTablasSimplex: todas las tablas una debajo de otra.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..componentes import Leyenda, MarcoDesplazable, TablaCanvas, TextoRico, etiqueta
from ..explicaciones import textos_simplex as TS
from ..formato import FORMATO
from ..tema import COLORES, FUENTES


def lista_iteraciones(resultado):
    """Iteraciones a mostrar (incluye la tabla de la solución alternativa si existe)."""
    elementos = list(resultado.iteraciones)
    if resultado.iteracion_alternativa is not None:
        elementos.append(resultado.iteracion_alternativa)
    return elementos


def crear_tabla(master, resultado, indice, iteracion):
    datos = TS.datos_tabla(resultado, indice, FORMATO, iteracion)
    return TablaCanvas(master, datos["filas"], filas_encabezado=datos["filas_encabezado"],
                       columnas_encabezado=datos["columnas_encabezado"], estilos=datos["estilos"],
                       estilos_fila=datos["estilos_fila"])


LEYENDA = [(COLORES["col_pivote"], "Columna pivote (entra)"), (COLORES["fila_pivote"], "Fila pivote (sale)"),
           (COLORES["celda_pivote"], "Elemento pivote"), (COLORES["razon_minima"], "Razón mínima"),
           (COLORES["optimo"], "Valor óptimo"), (COLORES["alternativo"], "Cj − Zj = 0 (óptimo alternativo)"),
           (COLORES["no_acotado"], "Columna sin a > 0 (no acotado)")]


class PanelIteracionesSimplex(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.elementos = []
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
        self.selector = ttk.Combobox(caja, textvariable=self.var_selector, state="readonly", width=52)
        self.selector.pack(side="left", padx=4)
        self.selector.bind("<<ComboboxSelected>>", lambda e: self.ir(self.selector.current()))
        self.boton_siguiente = ttk.Button(caja, text="Siguiente ►", style="Chico.TButton",
                                          command=lambda: self.ir(self.indice + 1))
        self.boton_siguiente.pack(side="left", padx=4)
        self.boton_ultima = ttk.Button(caja, text="►►", width=4, style="Chico.TButton",
                                       command=lambda: self.ir(len(self.elementos) - 1))
        self.boton_ultima.pack(side="left")
        self.etiqueta_posicion = etiqueta(caja, "", "base_negrita", "primario")
        self.etiqueta_posicion.pack(side="right")
        Leyenda(barra, LEYENDA).pack(fill="x", padx=14, pady=(0, 8))

        paneles = ttk.Panedwindow(self, orient="vertical")
        paneles.pack(fill="both", expand=True, pady=(6, 0))
        self.paneles = paneles
        arriba = tk.Frame(paneles, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                          highlightthickness=1)
        self.titulo_tabla = tk.Label(arriba, text="Resuelva un problema para ver el paso a paso.",
                                     font=FUENTES["h3"], bg=COLORES["superficie"], fg=COLORES["texto"], anchor="w")
        self.titulo_tabla.pack(fill="x", padx=14, pady=(10, 4))
        self.area_tabla = MarcoDesplazable(arriba, fondo=COLORES["superficie"], ajustar_ancho=False)
        self.area_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        abajo = tk.Frame(paneles, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                         highlightthickness=1)
        self.explicacion = TextoRico(abajo, alto=14)
        self.explicacion.pack(fill="both", expand=True)
        paneles.add(arriba, weight=3)
        paneles.add(abajo, weight=4)
        self._actualizar_botones()

    def mostrar(self, resultado) -> None:
        self.resultado = resultado
        self.elementos = lista_iteraciones(resultado)
        self.selector.configure(values=[
            TS.titulo_iteracion(resultado, min(k, len(resultado.iteraciones) - 1), it)
            for k, it in enumerate(self.elementos)])
        self.ir(0)
        self.after(120, self._ajustar_division)

    def _ajustar_division(self) -> None:
        """Da a la tabla el alto que necesita (máximo 60 % del panel)."""
        try:
            alto_total = self.paneles.winfo_height()
            alto_tabla = self.area_tabla.interior.winfo_reqheight() + self.titulo_tabla.winfo_reqheight() + 40
            if alto_total > 200:
                self.paneles.sashpos(0, max(160, min(alto_tabla, int(alto_total * 0.6))))
        except tk.TclError:
            pass

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.ir(self.indice)

    def ir(self, indice: int) -> None:
        if not self.elementos:
            return
        indice = max(0, min(indice, len(self.elementos) - 1))
        self.indice = indice
        it = self.elementos[indice]
        indice_modelo = min(indice, len(self.resultado.iteraciones) - 1)
        self.selector.current(indice)
        self.titulo_tabla.configure(text=TS.titulo_iteracion(self.resultado, indice_modelo, it))
        self.etiqueta_posicion.configure(text=f"Tabla {indice + 1} de {len(self.elementos)}")
        self.area_tabla.limpiar()
        crear_tabla(self.area_tabla.interior, self.resultado, indice_modelo, it).pack(anchor="nw", padx=4, pady=4)
        self.explicacion.mostrar(TS.bloques_iteracion(self.resultado, indice_modelo, FORMATO, it))
        self._actualizar_botones()

    def _actualizar_botones(self):
        hay = bool(self.elementos)
        estado_atras = "normal" if hay and self.indice > 0 else "disabled"
        estado_adelante = "normal" if hay and self.indice < len(self.elementos) - 1 else "disabled"
        self.boton_primera.configure(state=estado_atras)
        self.boton_anterior.configure(state=estado_atras)
        self.boton_siguiente.configure(state=estado_adelante)
        self.boton_ultima.configure(state=estado_adelante)


class PanelTodasTablasSimplex(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        Leyenda(self, LEYENDA, fondo=COLORES["fondo"]).pack(fill="x", padx=16, pady=(8, 2))
        self.area = MarcoDesplazable(self, ajustar_ancho=False)
        self.area.pack(fill="both", expand=True)

    def mostrar(self, resultado) -> None:
        self.resultado = resultado
        self.area.limpiar()
        contenedor = self.area.interior
        for k, it in enumerate(lista_iteraciones(resultado)):
            indice = min(k, len(resultado.iteraciones) - 1)
            tarjeta = tk.Frame(contenedor, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                               highlightthickness=1)
            tarjeta.pack(fill="x", anchor="w", padx=16, pady=8)
            tk.Label(tarjeta, text=TS.titulo_iteracion(resultado, indice, it), font=FUENTES["h3"],
                     bg=COLORES["superficie"], fg=COLORES["primario_texto"], anchor="w").pack(fill="x", padx=12,
                                                                                            pady=(10, 4))
            crear_tabla(tarjeta, resultado, indice, it).pack(anchor="w", padx=12, pady=(0, 6))
            tk.Label(tarjeta, text=self._resumen(resultado, it), font=FUENTES["base"], bg=COLORES["superficie"],
                     fg=COLORES["texto_suave"], anchor="w", justify="left").pack(fill="x", padx=12, pady=(0, 10))

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.mostrar(self.resultado)

    @staticmethod
    def _resumen(resultado, it) -> str:
        t = it.tabla
        z = f"z = {FORMATO.num(t.z)} {resultado.problema.unidad_z}"
        if it.columna_entra is not None and it.fila_sale is not None:
            prefijo = "Óptimo alternativo: " if it.estado == "optima" else ""
            return (f"{prefijo}Entra {t.simbolos[it.columna_entra]} · Sale {t.simbolos[t.base[it.fila_sale]]} · "
                    f"Pivote = {FORMATO.num(it.pivote)} · {z}")
        if it.estado == "no_acotada":
            return f"Entra {t.simbolos[it.columna_entra]}, pero ningún a > 0: problema NO ACOTADO · {z}"
        if it.estado in ("optima", "alternativa"):
            return f"Tabla óptima · {z}"
        return z
