"""
vista/simplex/vista_simplex.py
==============================
Pantalla completa del método Simplex: une todas las pestañas
(datos, modelo, paso a paso, tablas, solución y sensibilidad). Ofrece al controlador métodos simples para mostrar resultados y
errores.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ..componentes.dialogos import DialogosMixin
from ..formato import FORMATO
from ..tema import COLORES, FUENTES
from .panel_datos_simplex import PanelDatosSimplex
from .panel_iteraciones_simplex import PanelIteracionesSimplex, PanelTodasTablasSimplex
from .panel_resultados_simplex import PanelModeloSimplex, PanelSensibilidad, PanelSolucionSimplex


class VistaSimplex(DialogosMixin, tk.Frame):
    TITULO = "Método Simplex (maximizar / minimizar)"
    SUBTITULO = ("Programación lineal con restricciones ≤, hasta 8 variables y 8 restricciones. Muestra cada tabla "
                 "con la variable que entra, la que sale y el pivote, y el análisis de sensibilidad.")

    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.controlador = None
        self.resultado = None
        self.sensibilidad = None
        self.franja = tk.Label(self, text="Paso 1: escriba los datos o cargue un ejemplo y pulse «Resolver con Simplex».",
                               font=FUENTES["pequena_negrita"], bg=COLORES["primario_suave"],
                               fg=COLORES["primario_texto"], anchor="w", padx=14, pady=6)
        self.franja.pack(fill="x", padx=16, pady=(8, 0))
        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, padx=16, pady=(4, 12))
        self.panel_datos = PanelDatosSimplex(self.cuaderno)
        self.panel_modelo = PanelModeloSimplex(self.cuaderno)
        self.panel_pasos = PanelIteracionesSimplex(self.cuaderno)
        self.panel_tablas = PanelTodasTablasSimplex(self.cuaderno)
        self.panel_solucion = PanelSolucionSimplex(self.cuaderno)
        self.panel_sensibilidad = PanelSensibilidad(self.cuaderno)
        for panel, titulo in ((self.panel_datos, "1 · Datos"), (self.panel_modelo, "2 · Modelo"),
                              (self.panel_pasos, "3 · Paso a paso"), (self.panel_tablas, "4 · Tablas"),
                              (self.panel_solucion, "5 · Solución"), (self.panel_sensibilidad, "6 · Sensibilidad")):
            self.cuaderno.add(panel, text=titulo)
        FORMATO.suscribir(self.refrescar)

    # --------------------------------------------------- API del controlador
    def establecer_controlador(self, controlador) -> None:
        self.controlador = controlador
        self.panel_datos.controlador = controlador

    def mostrar_resultado(self, resultado, sensibilidad) -> None:
        self.resultado, self.sensibilidad = resultado, sensibilidad
        self.panel_modelo.mostrar(resultado.problema)
        self.panel_pasos.mostrar(resultado)
        self.panel_tablas.mostrar(resultado)
        self.panel_solucion.mostrar(resultado)
        if sensibilidad is not None:
            self.panel_sensibilidad.mostrar(sensibilidad)
        else:
            self.panel_sensibilidad.mostrar_mensaje(
                "No hay análisis de sensibilidad porque el problema no tiene una solución óptima finita "
                "(es no acotado).", "advertencia")
        self._actualizar_franja()
        self.cuaderno.select(self.panel_pasos)

    def _actualizar_franja(self) -> None:
        r = self.resultado
        if r is None:
            return
        p = r.problema
        if r.es_optimo:
            texto = (f"Resultado: ÓPTIMO · z* = {FORMATO.num(r.z)} {p.unidad_z} · {r.numero_pivoteos} iteración(es) · "
                     f"revise las pestañas 3 a 6")
            fondo, color = COLORES["exito_suave"], COLORES["exito"]
        elif r.estado == "no_acotado":
            texto = "Resultado: problema NO ACOTADO (z puede crecer sin límite) · vea las pestañas 3 y 5"
            fondo, color = COLORES["error_suave"], COLORES["error"]
        else:
            texto = "Resultado: el método se detuvo por el límite de iteraciones"
            fondo, color = COLORES["advertencia_suave"], COLORES["advertencia"]
        especiales = [c.titulo for c in r.casos if c.nivel in ("advertencia", "error") and c.tipo != "no_acotado"]
        if especiales:
            texto += "  ·  Casos especiales: " + "; ".join(especiales)
        self.franja.configure(text=texto, bg=fondo, fg=color)

    def refrescar(self) -> None:
        """Vuelve a dibujar todo (por ejemplo al cambiar fracción/decimal)."""
        if self.resultado is None:
            return
        for panel in (self.panel_modelo, self.panel_pasos, self.panel_tablas, self.panel_solucion,
                      self.panel_sensibilidad):
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

    def avisar_casos(self, resultado) -> None:
        importantes = [c for c in resultado.casos if c.nivel in ("error", "advertencia")]
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
        texto = "Datos listos. Pulse «Resolver con Simplex» (o Ctrl + Enter) para resolver este problema."
        if self.resultado is not None:
            texto += "  Las demás pestañas todavía muestran el problema resuelto antes."
        self.franja.configure(text=texto, bg=COLORES["info_suave"], fg=COLORES["info"])
