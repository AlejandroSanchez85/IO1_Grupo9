"""
vista/componentes/panel_reporte.py
==================================
Pestaña "Reporte": muestra TODO el procedimiento en texto y permite
copiarlo, guardarlo como .txt o exportarlo a HTML (para abrirlo en el
navegador e imprimirlo como PDF para el informe).
"""
from __future__ import annotations

import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..tema import COLORES, FUENTES
from .widgets import TextoRico


class PanelReporte(tk.Frame):
    def __init__(self, master, nombre_base: str = "reporte"):
        super().__init__(master, bg=COLORES["fondo"])
        self.nombre_base = nombre_base
        self.generar_texto = None      # función sin argumentos -> str
        self.generar_html = None       # función sin argumentos -> str
        barra = tk.Frame(self, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
        barra.pack(fill="x")
        caja = tk.Frame(barra, bg=COLORES["superficie"])
        caja.pack(fill="x", padx=12, pady=8)
        tk.Label(caja, text="Reporte completo del procedimiento", font=FUENTES["h3"], bg=COLORES["superficie"],
                 fg=COLORES["texto"]).pack(side="left")
        ttk.Button(caja, text="Exportar HTML (imprimir a PDF)", style="Primario.TButton",
                   command=self.exportar_html).pack(side="right", padx=4)
        ttk.Button(caja, text="Guardar .txt", style="Chico.TButton", command=self.guardar_txt).pack(side="right",
                                                                                                  padx=4)
        ttk.Button(caja, text="Copiar todo", style="Chico.TButton", command=self.copiar).pack(side="right", padx=4)
        self.texto = TextoRico(self, alto=30)
        self.texto.texto.configure(font=FUENTES["mono"], wrap="none")
        barra_h = ttk.Scrollbar(self, orient="horizontal", command=self.texto.texto.xview)
        self.texto.texto.configure(xscrollcommand=barra_h.set)
        self.texto.pack(fill="both", expand=True, padx=12, pady=(10, 0))
        barra_h.pack(fill="x", padx=12, pady=(0, 10))
        self.texto.mostrar([("Resuelva un problema para generar el reporte.\n", ("suave",))])

    def configurar(self, generar_texto, generar_html) -> None:
        self.generar_texto, self.generar_html = generar_texto, generar_html
        self.refrescar()

    def refrescar(self) -> None:
        if self.generar_texto is not None:
            self.texto.mostrar([(self.generar_texto(), ())])

    def copiar(self) -> None:
        contenido = self.texto.contenido()
        self.clipboard_clear()
        self.clipboard_append(contenido)
        messagebox.showinfo("Reporte", "El reporte se copió al portapapeles.", parent=self)

    def guardar_txt(self) -> None:
        if self.generar_texto is None:
            messagebox.showwarning("Reporte", "Primero resuelva un problema.", parent=self)
            return
        ruta = filedialog.asksaveasfilename(parent=self, defaultextension=".txt", initialfile=f"{self.nombre_base}.txt",
                                            filetypes=[("Texto", "*.txt")])
        if not ruta:
            return
        try:
            Path(ruta).write_text(self.generar_texto(), encoding="utf-8")
            messagebox.showinfo("Reporte", f"Reporte guardado en:\n{ruta}", parent=self)
        except OSError as error:
            messagebox.showerror("Reporte", f"No se pudo guardar el archivo:\n{error}", parent=self)

    def exportar_html(self) -> None:
        if self.generar_html is None:
            messagebox.showwarning("Reporte", "Primero resuelva un problema.", parent=self)
            return
        ruta = filedialog.asksaveasfilename(parent=self, defaultextension=".html",
                                            initialfile=f"{self.nombre_base}.html", filetypes=[("HTML", "*.html")])
        if not ruta:
            return
        try:
            Path(ruta).write_text(self.generar_html(), encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Reporte", f"No se pudo guardar el archivo:\n{error}", parent=self)
            return
        try:
            webbrowser.open(Path(ruta).resolve().as_uri())
        except Exception:
            pass
        messagebox.showinfo("Reporte", f"Reporte HTML guardado en:\n{ruta}\n\nSe abrirá en el navegador; use "
                                       f"Imprimir → Guardar como PDF si lo necesita para el informe.", parent=self)
