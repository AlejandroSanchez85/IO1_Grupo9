"""
vista/componentes/dialogos.py
=============================
Ventanas de diálogo comunes (mensajes, confirmaciones y selección de
archivos). Las vistas las heredan para que el controlador nunca use
tkinter directamente.
"""
from __future__ import annotations

from tkinter import filedialog, messagebox


class DialogosMixin:
    def mostrar_mensaje(self, titulo: str, texto: str, nivel: str = "info") -> None:
        if nivel == "error":
            messagebox.showerror(titulo, texto, parent=self)
        elif nivel == "advertencia":
            messagebox.showwarning(titulo, texto, parent=self)
        else:
            messagebox.showinfo(titulo, texto, parent=self)

    def confirmar(self, titulo: str, texto: str) -> bool:
        return bool(messagebox.askyesno(titulo, texto, parent=self))

    def pedir_archivo_abrir(self, carpeta_inicial=None) -> str:
        return filedialog.askopenfilename(parent=self, title="Abrir problema",
                                          initialdir=str(carpeta_inicial) if carpeta_inicial else None,
                                          filetypes=[("Problema (JSON)", "*.json"), ("Todos", "*.*")]) or ""

    def pedir_archivo_guardar(self, carpeta_inicial=None, nombre: str = "problema.json") -> str:
        return filedialog.asksaveasfilename(parent=self, title="Guardar problema", defaultextension=".json",
                                            initialdir=str(carpeta_inicial) if carpeta_inicial else None,
                                            initialfile=nombre,
                                            filetypes=[("Problema (JSON)", "*.json")]) or ""
