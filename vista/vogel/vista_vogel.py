"""
vista/vogel/vista_vogel.py
==========================
Pantalla completa del método de Vogel: datos, planteamiento, paso a paso,
todas las tablas, solución, optimalidad (MODI), gráficas y reporte.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ..componentes.dialogos import DialogosMixin
from ..componentes.panel_reporte import PanelReporte
from ..formato import FORMATO
from ..reportes import html_vogel, texto_vogel
from ..tema import COLORES, FUENTES
from .panel_datos_vogel import PanelDatosVogel
from .panel_graficas_vogel import PanelGraficasVogel
from .panel_pasos_vogel import PanelPasosVogel, PanelTodosPasosVogel
from .panel_resultados_vogel import PanelModi, PanelPlanteamientoVogel, PanelSolucionVogel


class VistaVogel(DialogosMixin, tk.Frame):
    TITULO = "Transporte · Método de Vogel"
    SUBTITULO = ("Minimiza el costo de transporte (hasta 8 orígenes × 8 destinos, balanceado o no). Muestra las "
                 "penalizaciones de cada paso, la celda escogida, la tabla final y el costo total.")

    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.controlador = None
        self.resultado = None
        self.modi = None
        self.franja = tk.Label(self, text="Paso 1: escriba la tabla de transporte o cargue un ejemplo y pulse "
                                          "«Resolver con Vogel».", font=FUENTES["pequena_negrita"],
                               bg=COLORES["primario_suave"], fg=COLORES["primario_texto"], anchor="w", padx=14, pady=6)
        self.franja.pack(fill="x", padx=16, pady=(8, 0))
        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, padx=16, pady=(4, 12))
        self.panel_datos = PanelDatosVogel(self.cuaderno)
        self.panel_planteamiento = PanelPlanteamientoVogel(self.cuaderno)
        self.panel_pasos = PanelPasosVogel(self.cuaderno)
        self.panel_todos = PanelTodosPasosVogel(self.cuaderno)
        self.panel_solucion = PanelSolucionVogel(self.cuaderno)
        self.panel_modi = PanelModi(self.cuaderno)
        self.panel_graficas = PanelGraficasVogel(self.cuaderno)
        self.panel_reporte = PanelReporte(self.cuaderno, "reporte_vogel")
        for panel, titulo in ((self.panel_datos, "1 · Datos"), (self.panel_planteamiento, "2 · Modelo"),
                              (self.panel_pasos, "3 · Paso a paso"), (self.panel_todos, "4 · Tablas"),
                              (self.panel_solucion, "5 · Solución"), (self.panel_modi, "6 · MODI"),
                              (self.panel_graficas, "7 · Gráficas"), (self.panel_reporte, "8 · Reporte")):
            self.cuaderno.add(panel, text=titulo)

        # --- Pestañas 7 · Gráficas y 8 · Reporte ---
        self.cuaderno.hide(self.panel_graficas)
        self.cuaderno.hide(self.panel_reporte)
        
        FORMATO.suscribir(self.refrescar)

    # --------------------------------------------------- API del controlador
    def establecer_controlador(self, controlador) -> None:
        self.controlador = controlador
        self.panel_datos.controlador = controlador

    def mostrar_resultado(self, resultado, modi) -> None:
        self.resultado, self.modi = resultado, modi
        self.panel_planteamiento.mostrar(resultado)
        self.panel_pasos.mostrar(resultado)
        self.panel_todos.mostrar(resultado)
        self.panel_solucion.mostrar(resultado, modi)
        if modi is not None:
            self.panel_modi.mostrar(resultado, modi)
        self.panel_graficas.mostrar(resultado)
        self.panel_reporte.configurar(lambda: texto_vogel(self.resultado, self.modi, FORMATO),
                                      lambda: html_vogel(self.resultado, self.modi, FORMATO))
        self._actualizar_franja()
        self.cuaderno.select(self.panel_pasos)

    def _actualizar_franja(self) -> None:
        r, modi = self.resultado, self.modi
        if r is None:
            return
        p = r.problema
        texto = f"Resultado Vogel: costo total = {FORMATO.num(r.costo_total)} {p.unidad_costo} · {len(r.pasos)} pasos"
        if modi is not None and modi.rutas_prohibidas_usadas:
            texto += " · INFACTIBLE con las rutas permitidas"
        elif modi is not None:
            texto += (" · Vogel ya es ÓPTIMO" if modi.vogel_es_optimo else
                      f" · óptimo (MODI) = {FORMATO.num(modi.costo_optimo)} {p.unidad_costo}")
        especiales = [c.titulo for c in r.casos if c.nivel in ("advertencia", "error")]
        if modi is not None:
            especiales += [c.titulo for c in modi.casos if c.nivel == "error"]
        if especiales:
            texto += "  ·  " + "; ".join(especiales)
        infactible = modi is not None and modi.rutas_prohibidas_usadas
        fondo = COLORES["error_suave"] if infactible else (COLORES["advertencia_suave"] if especiales
                                                            else COLORES["exito_suave"])
        color = COLORES["error"] if infactible else (COLORES["advertencia"] if especiales else COLORES["exito"])
        self.franja.configure(text=texto, bg=fondo, fg=color)

    def refrescar(self) -> None:
        if self.resultado is None:
            return
        for panel in (self.panel_planteamiento, self.panel_pasos, self.panel_todos, self.panel_solucion,
                      self.panel_modi, self.panel_graficas, self.panel_reporte):
            panel.refrescar()
        self._actualizar_franja()

    def mostrar_errores(self, errores) -> None:
        self.cuaderno.select(self.panel_datos)
        self.panel_datos.marcar_errores([campo for _, campo in errores if campo is not None])
        mensajes = [mensaje for mensaje, _ in errores]
        texto = "\n".join(f"• {m}" for m in mensajes[:10])
        if len(mensajes) > 10:
            texto += f"\n… y {len(mensajes) - 10} error(es) más."
        messagebox.showerror("Revise los datos",
                             f"No se puede resolver todavía. Corrija lo siguiente (las casillas con error están en "
                             f"rojo):\n\n{texto}", parent=self)

    def avisar_casos(self, resultado, modi) -> None:
        importantes = [c for c in resultado.casos if c.nivel in ("error", "advertencia")]
        if modi is not None:
            importantes += [c for c in modi.casos if c.nivel == "error"]
        if not importantes:
            return
        texto = "\n\n".join(f"• {c.titulo}\n{c.mensaje}" for c in importantes)
        if any(c.nivel == "error" for c in importantes):
            messagebox.showwarning("Caso especial detectado", texto, parent=self)
        else:
            messagebox.showinfo("Caso especial detectado", texto, parent=self)

    def seleccionar_datos(self) -> None:
        self.cuaderno.select(self.panel_datos)

    def marcar_datos_nuevos(self) -> None:
        """Avisa que los resultados mostrados son del problema anterior hasta que se vuelva a resolver."""
        texto = "Datos listos. Pulse «Resolver con Vogel» (o Ctrl + Enter) para resolver este problema."
        if self.resultado is not None:
            texto += "  Las demás pestañas todavía muestran el problema resuelto antes."
        self.franja.configure(text=texto, bg=COLORES["info_suave"], fg=COLORES["info"])
