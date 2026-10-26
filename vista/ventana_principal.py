"""
vista/ventana_principal.py
==========================
Ventana principal: barra lateral de navegación (Inicio, Simplex,
Ayuda), encabezado y el área donde se muestra cada pantalla. También
captura cualquier error inesperado para que el programa NO se cierre.
"""
from __future__ import annotations

import sys
import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from .componentes import instalar_rueda_global
from .formato import FORMATO, MODO_DECIMAL, MODO_FRACCION
from .simplex import VistaSimplex
from .tema import COLORES, FUENTES, aplicar_tema, px
from .vista_ayuda import VistaAyuda
from .vista_inicio import VistaInicio


def _icono(canvas: tk.Canvas, tipo: str, color: str) -> None:
    """Íconos dibujados con figuras (no dependen de fuentes especiales)."""
    canvas.delete("all")
    if tipo == "inicio":
        canvas.create_polygon(3, 10, 11, 3, 19, 10, fill="", outline=color, width=2)
        canvas.create_rectangle(6, 10, 16, 18, outline=color, width=2)
    elif tipo == "simplex":
        canvas.create_rectangle(3, 3, 19, 19, outline=color, width=2)
        for k in (8.5, 13.5):
            canvas.create_line(3, k, 19, k, fill=color)
            canvas.create_line(k, 3, k, 19, fill=color)
    else:
        canvas.create_oval(3, 3, 19, 19, outline=color, width=2)
        canvas.create_text(11, 11, text="?", fill=color, font=FUENTES["base_negrita"])


class ElementoNavegacion(tk.Frame):
    def __init__(self, master, texto: str, icono: str, comando):
        super().__init__(master, bg=COLORES["lateral"], cursor="hand2")
        self.comando, self.icono_tipo, self.activo = comando, icono, False
        self.barra = tk.Frame(self, bg=COLORES["lateral"], width=4)
        self.barra.pack(side="left", fill="y")
        self.icono = tk.Canvas(self, width=22, height=22, bg=COLORES["lateral"], highlightthickness=0)
        self.icono.pack(side="left", padx=(14, 10), pady=11)
        self.etiqueta = tk.Label(self, text=texto, font=FUENTES["lateral"], bg=COLORES["lateral"],
                                 fg=COLORES["lateral_texto"], anchor="w")
        self.etiqueta.pack(side="left", fill="x", expand=True)
        for widget in (self, self.icono, self.etiqueta, self.barra):
            widget.bind("<Button-1>", lambda e: self.comando())
            widget.bind("<Enter>", lambda e: self._pintar(hover=True))
            widget.bind("<Leave>", lambda e: self._pintar(hover=False))
        self._pintar()

    def establecer_activo(self, activo: bool) -> None:
        self.activo = activo
        self._pintar()

    def _pintar(self, hover: bool = False) -> None:
        if self.activo:
            fondo, texto, barra, fuente = COLORES["lateral_activo"], "#FFFFFF", "#818CF8", FUENTES["lateral_negrita"]
        elif hover:
            fondo, texto, barra, fuente = COLORES["lateral_hover"], "#FFFFFF", COLORES["lateral_hover"], FUENTES["lateral"]
        else:
            fondo, texto, barra, fuente = COLORES["lateral"], COLORES["lateral_texto"], COLORES["lateral"], FUENTES["lateral"]
        for widget in (self, self.icono, self.etiqueta):
            widget.configure(bg=fondo)
        self.barra.configure(bg=barra)
        self.etiqueta.configure(fg=texto, font=fuente)
        _icono(self.icono, self.icono_tipo, COLORES["secundario"] if self.activo else texto)


class VentanaPrincipal:
    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title("IO1 · Grupo 9 — Método Simplex")
        self.raiz.geometry("1380x860")
        self.raiz.minsize(1080, 660)
        aplicar_tema(self.raiz)
        instalar_rueda_global(self.raiz)
        self.raiz.report_callback_exception = self._error_no_controlado
        if sys.platform.startswith("win"):
            try:
                self.raiz.state("zoomed")
            except tk.TclError:
                pass
        self.vistas: dict = {}
        self.elementos: dict = {}
        self._crear_estructura()
        self.vista_inicio = VistaInicio(self.contenido, self.mostrar)
        self.vista_simplex = VistaSimplex(self.contenido)
        self.vista_ayuda = VistaAyuda(self.contenido)
        for clave, vista, titulo, subtitulo in (
                ("inicio", self.vista_inicio, "Inicio", "Proyecto final · Investigación de Operaciones 1 · Grupo 9"),
                ("simplex", self.vista_simplex, VistaSimplex.TITULO, VistaSimplex.SUBTITULO),
                ("ayuda", self.vista_ayuda, "Ayuda y manual de uso", "Cómo ingresar los datos, interpretar los "
                                                                    "resultados y usar los ejemplos.")):
            vista.grid(row=0, column=0, sticky="nsew")
            self.vistas[clave] = (vista, titulo, subtitulo)
        self.actual = None

    # ------------------------------------------------------------ estructura
    def _crear_estructura(self):
        lateral = tk.Frame(self.raiz, bg=COLORES["lateral"], width=px(250))
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        logo = tk.Frame(lateral, bg=COLORES["lateral"])
        logo.pack(fill="x", padx=18, pady=(22, 18))
        insignia = tk.Canvas(logo, width=42, height=42, bg=COLORES["lateral"], highlightthickness=0)
        insignia.pack(side="left")
        insignia.create_oval(1, 1, 41, 41, fill=COLORES["primario"], outline="")
        insignia.create_text(21, 21, text="IO", fill="#FFFFFF", font=FUENTES["h3"])
        textos = tk.Frame(logo, bg=COLORES["lateral"])
        textos.pack(side="left", padx=10)
        tk.Label(textos, text="IO1 · Grupo 9", font=FUENTES["logo"], bg=COLORES["lateral"],
                 fg=COLORES["lateral_titulo"]).pack(anchor="w")
        tk.Label(textos, text="Método Simplex", font=FUENTES["pequena"], bg=COLORES["lateral"],
                 fg=COLORES["lateral_tenue"]).pack(anchor="w")
        tk.Label(lateral, text="MENÚ", font=FUENTES["mini"], bg=COLORES["lateral"], fg=COLORES["lateral_tenue"]).pack(
            anchor="w", padx=22, pady=(6, 4))
        for clave, texto, icono in (("inicio", "Inicio", "inicio"), ("simplex", "Simplex (max / min)", "simplex"),
                                    ("ayuda", "Ayuda", "ayuda")):
            elemento = ElementoNavegacion(lateral, texto, icono, lambda c=clave: self.mostrar(c))
            elemento.pack(fill="x")
            self.elementos[clave] = elemento

        pie = tk.Frame(lateral, bg=COLORES["lateral"])
        pie.pack(side="bottom", fill="x", padx=18, pady=16)
        tk.Label(pie, text="Mostrar números como:", font=FUENTES["pequena_negrita"], bg=COLORES["lateral"],
                 fg=COLORES["lateral_texto"]).pack(anchor="w")
        self.var_formato = tk.StringVar(value=FORMATO.modo)
        for valor, texto in ((MODO_FRACCION, "Fracciones (5/3)"), (MODO_DECIMAL, "Decimales (1.6667)")):
            ttk.Radiobutton(pie, text=texto, value=valor, variable=self.var_formato, style="Lateral.TRadiobutton",
                            command=lambda: FORMATO.cambiar_modo(self.var_formato.get())).pack(anchor="w", pady=1)
        tk.Frame(pie, bg=COLORES["lateral_hover"], height=1).pack(fill="x", pady=12)
        tk.Label(pie, text="",
                 font=FUENTES["mini"], bg=COLORES["lateral"], fg=COLORES["lateral_tenue"], justify="left").pack(
            anchor="w")
        tk.Label(pie, text="", font=FUENTES["mini"], bg=COLORES["lateral"],
                 fg=COLORES["lateral_tenue"]).pack(anchor="w", pady=(6, 0))

        derecha = tk.Frame(self.raiz, bg=COLORES["fondo"])
        derecha.pack(side="left", fill="both", expand=True)
        encabezado = tk.Frame(derecha, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                              highlightthickness=1)
        encabezado.pack(fill="x")
        self.titulo = tk.Label(encabezado, text="", font=FUENTES["titulo"], bg=COLORES["superficie"],
                               fg=COLORES["texto"], anchor="w")
        self.titulo.pack(fill="x", padx=24, pady=(14, 0))
        self.subtitulo = tk.Label(encabezado, text="", font=FUENTES["subtitulo"], bg=COLORES["superficie"],
                                  fg=COLORES["texto_suave"], anchor="w", justify="left")
        self.subtitulo.pack(fill="x", padx=24, pady=(2, 14))
        encabezado.bind("<Configure>", lambda e: self.subtitulo.configure(wraplength=max(300, e.width - 60)))
        self.contenido = tk.Frame(derecha, bg=COLORES["fondo"])
        self.contenido.pack(fill="both", expand=True)
        self.contenido.grid_rowconfigure(0, weight=1)
        self.contenido.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------ navegación
    def mostrar(self, clave: str) -> None:
        if clave not in self.vistas:
            return
        vista, titulo, subtitulo = self.vistas[clave]
        vista.tkraise()
        self.titulo.configure(text=titulo)
        self.subtitulo.configure(text=subtitulo)
        for nombre, elemento in self.elementos.items():
            elemento.establecer_activo(nombre == clave)
        self.actual = clave

    def _error_no_controlado(self, tipo, valor, rastro):
        """Cualquier error inesperado se muestra en un mensaje y el programa sigue abierto."""
        detalle = "".join(traceback.format_exception(tipo, valor, rastro))
        print(detalle, file=sys.stderr)
        messagebox.showerror("Error inesperado",
                             "Ocurrió un error, pero el programa sigue funcionando.\n\n"
                             f"{tipo.__name__}: {valor}\n\nSi se repite, revise los datos ingresados.",
                             parent=self.raiz)

    def iniciar(self) -> None:
        self.raiz.mainloop()
