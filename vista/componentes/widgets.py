"""
vista/componentes/widgets.py
============================
Componentes visuales reutilizables (solo presentación, sin matemática):

* MarcoDesplazable: área con barras de desplazamiento y rueda del ratón.
* Tarjeta: recuadro blanco con título (estilo moderno tipo "card").
* Aviso: mensaje de color para casos especiales (error, advertencia, info, éxito).
* Campo: casilla de texto que se pone roja cuando tiene un error.
* TextoRico: texto de solo lectura con estilos (títulos, negrillas, fórmulas).
* Leyenda: muestras de color con su significado.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..tema import COLORES, FUENTES, px

# -------------------------------------------------------------------------
# Rueda del ratón: un solo manejador global que desplaza el área que está
# debajo del puntero (funciona igual en Windows, macOS y Linux).
# -------------------------------------------------------------------------
_CLASES_CON_RUEDA_PROPIA = ("Text", "Listbox", "Treeview", "TCombobox", "Spinbox", "TSpinbox")


def instalar_rueda_global(raiz: tk.Misc) -> None:
    def desplazar(evento):
        try:
            widget = raiz.winfo_containing(evento.x_root, evento.y_root)
        except (KeyError, tk.TclError):
            return
        if widget is None:
            return
        clase = widget.winfo_class()
        if clase == "Text":
            try:
                primero, ultimo = widget.yview()
            except tk.TclError:
                return
            if not (primero <= 0.0 and ultimo >= 1.0):
                return                    # el texto es largo: él mismo se desplaza
        elif clase in _CLASES_CON_RUEDA_PROPIA:
            return
        if evento.num == 4:
            pasos = -1
        elif evento.num == 5:
            pasos = 1
        else:
            pasos = -1 if evento.delta > 0 else 1
        horizontal = bool(evento.state & 0x0001)                # tecla Shift
        while widget is not None:
            tabla_ancha = getattr(widget, "_desplazable_horizontal", None)
            if horizontal and tabla_ancha is not None:
                tabla_ancha.desplazar(pasos * 3)
                return
            marco = getattr(widget, "_marco_desplazable", None)
            if marco is not None:
                marco.desplazar(pasos * 3, horizontal)
                return
            widget = widget.master

    raiz.bind_all("<MouseWheel>", desplazar, add="+")
    raiz.bind_all("<Shift-MouseWheel>", desplazar, add="+")
    raiz.bind_all("<Button-4>", desplazar, add="+")
    raiz.bind_all("<Button-5>", desplazar, add="+")


class MarcoDesplazable(tk.Frame):
    """Marco con desplazamiento vertical (y horizontal si el contenido es ancho).

    El contenido se coloca dentro de ``self.interior``.
    """

    def __init__(self, master, fondo: str | None = None, ajustar_ancho: bool = True, horizontal: bool = True,
                 **kwargs):
        fondo = fondo or COLORES["fondo"]
        super().__init__(master, bg=fondo, **kwargs)
        self.ajustar_ancho = ajustar_ancho
        self.horizontal = horizontal      # False: el contenido siempre toma el ancho visible (solo vertical)
        self.canvas = tk.Canvas(self, bg=fondo, highlightthickness=0, bd=0,
                                yscrollincrement=20, xscrollincrement=20)
        self.interior = tk.Frame(self.canvas, bg=fondo)
        self._ventana = self.canvas.create_window(0, 0, window=self.interior, anchor="nw")
        self.barra_v = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.barra_h = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.barra_v.set, xscrollcommand=self.barra_h.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.barra_v.grid(row=0, column=1, sticky="ns")
        self.barra_h.grid(row=1, column=0, sticky="ew")
        self.barra_h.grid_remove()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas._marco_desplazable = self
        self.interior._marco_desplazable = self
        self._pendiente = None
        self._ancho_actual = None
        self._ancho_maximo = 0          # en modo horizontal el ancho solo crece (evita oscilaciones)
        self._ultimo_visible = None
        self.interior.bind("<Configure>", self._actualizar)
        self.canvas.bind("<Configure>", self._actualizar)

    def _actualizar(self, evento=None):
        if evento is not None and evento.widget is self.canvas and evento.width != self._ultimo_visible:
            self._ultimo_visible = evento.width       # cambió el tamaño de la ventana: se recalcula
            self._ancho_maximo = 0
        # Se agrupan los eventos para recalcular una sola vez (evita bucles de redimensionamiento)
        if self._pendiente is None:
            self._pendiente = self.after_idle(self._aplicar)

    def reiniciar_ancho(self) -> None:
        """Permite que el contenido vuelva a angostarse (por ejemplo al reducir la tabla)."""
        self._ancho_maximo = 0
        self._actualizar()

    def _aplicar(self):
        self._pendiente = None
        if not self.winfo_exists():
            return
        ancho_contenido = self.interior.winfo_reqwidth()
        ancho_visible = self.canvas.winfo_width()
        if not self.horizontal:
            ancho_contenido = min(ancho_contenido, ancho_visible)
        if self.ajustar_ancho and ancho_contenido <= ancho_visible and self._ancho_maximo <= ancho_visible:
            nuevo_ancho = ancho_visible
            mostrar_barra = False
        else:
            nuevo_ancho = max(ancho_contenido, ancho_visible if self.ajustar_ancho else 0, self._ancho_maximo)
            self._ancho_maximo = nuevo_ancho
            mostrar_barra = nuevo_ancho > ancho_visible > 1
        if nuevo_ancho != self._ancho_actual:
            self._ancho_actual = nuevo_ancho
            self.canvas.itemconfigure(self._ventana, width=nuevo_ancho)
        if mostrar_barra and not self.barra_h.winfo_ismapped():
            self.barra_h.grid()
        elif not mostrar_barra and self.barra_h.winfo_ismapped():
            self.barra_h.grid_remove()
        region = self.canvas.bbox("all")
        if region is not None:
            self.canvas.configure(scrollregion=region)

    def desplazar(self, pasos: int, horizontal: bool = False) -> None:
        if horizontal:
            if self.barra_h.winfo_ismapped():
                self.canvas.xview_scroll(pasos, "units")
        elif self.interior.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(pasos, "units")

    def al_inicio(self) -> None:
        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(0)

    def limpiar(self) -> None:
        for hijo in self.interior.winfo_children():
            hijo.destroy()
        self._ancho_maximo = 0
        self.al_inicio()


class Tarjeta(tk.Frame):
    """Recuadro blanco con borde suave, título opcional y un ``cuerpo``."""

    def __init__(self, master, titulo: str | None = None, subtitulo: str | None = None,
                 relleno: int = 16, **kwargs):
        super().__init__(master, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                         highlightthickness=1, bd=0, **kwargs)
        if titulo:
            tk.Label(self, text=titulo, font=FUENTES["h2"], bg=COLORES["superficie"],
                     fg=COLORES["texto"], anchor="w", justify="left").pack(
                fill="x", padx=relleno, pady=(relleno - 2, 0))
        if subtitulo:
            self.etiqueta_subtitulo = tk.Label(
                self, text=subtitulo, font=FUENTES["pequena"], bg=COLORES["superficie"],
                fg=COLORES["texto_suave"], anchor="w", justify="left", wraplength=300)
            self.etiqueta_subtitulo.pack(fill="x", padx=relleno, pady=(2, 0))
            # El margen extra (24 px) evita que el texto empuje el ancho de la tarjeta (bucle de tamaño)
            self.bind("<Configure>", lambda e: self.etiqueta_subtitulo.configure(
                wraplength=max(200, e.width - 2 * relleno - 24)), add="+")
        self.cuerpo = tk.Frame(self, bg=COLORES["superficie"])
        self.cuerpo.pack(fill="both", expand=True, padx=relleno,
                         pady=(10 if titulo else relleno, relleno))


_ESTILO_AVISO = {
    "error": ("error", "error_suave", "error_borde"),
    "advertencia": ("advertencia", "advertencia_suave", "advertencia_borde"),
    "info": ("info", "info_suave", "info_borde"),
    "exito": ("exito", "exito_suave", "exito_borde"),
}


def dibujar_icono(canvas: tk.Canvas, nivel: str, x: int, y: int, r: int = 10) -> None:
    """Dibuja el ícono del aviso con figuras (no depende de fuentes con símbolos)."""
    color = COLORES[_ESTILO_AVISO.get(nivel, _ESTILO_AVISO["info"])[0]]
    if nivel == "advertencia":
        canvas.create_polygon(x, y - r, x + r, y + r - 1, x - r, y + r - 1, fill=color, outline=color)
        canvas.create_line(x, y - r / 2.6, x, y + r / 3.2, fill="#FFFFFF", width=2)
        canvas.create_oval(x - 1.4, y + r / 1.75 - 1.4, x + 1.4, y + r / 1.75 + 1.4, fill="#FFFFFF",
                           outline="#FFFFFF")
        return
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=color)
    if nivel == "exito":
        canvas.create_line(x - r / 2, y, x - r / 7, y + r / 2.6, x + r / 1.8, y - r / 2.4,
                           fill="#FFFFFF", width=2, capstyle="round", joinstyle="round")
    elif nivel == "error":
        d = r / 2.4
        canvas.create_line(x - d, y - d, x + d, y + d, fill="#FFFFFF", width=2, capstyle="round")
        canvas.create_line(x - d, y + d, x + d, y - d, fill="#FFFFFF", width=2, capstyle="round")
    else:
        canvas.create_line(x, y - r / 8, x, y + r / 2, fill="#FFFFFF", width=2, capstyle="round")
        canvas.create_oval(x - 1.4, y - r / 2 - 1.4, x + 1.4, y - r / 2 + 1.4, fill="#FFFFFF",
                           outline="#FFFFFF")


class Aviso(tk.Frame):
    """Mensaje de color para avisar casos especiales con texto claro."""

    def __init__(self, master, nivel: str, titulo: str, mensaje: str = "", **kwargs):
        fuerte, suave, borde = (COLORES[k] for k in _ESTILO_AVISO.get(nivel, _ESTILO_AVISO["info"]))
        super().__init__(master, bg=suave, highlightbackground=borde, highlightthickness=1, **kwargs)
        tk.Frame(self, bg=fuerte, width=5).pack(side="left", fill="y")
        icono = tk.Canvas(self, width=30, height=30, bg=suave, highlightthickness=0)
        icono.pack(side="left", anchor="n", padx=(10, 2), pady=10)
        dibujar_icono(icono, nivel, 15, 15, 10)
        cuerpo = tk.Frame(self, bg=suave)
        cuerpo.pack(side="left", fill="both", expand=True, padx=(4, 12), pady=8)
        tk.Label(cuerpo, text=titulo, font=FUENTES["base_negrita"], bg=suave, fg=fuerte,
                 anchor="w", justify="left").pack(fill="x")
        self._mensaje = None
        if mensaje:
            self._mensaje = tk.Label(cuerpo, text=mensaje, font=FUENTES["base"], bg=suave,
                                     fg=COLORES["texto"], anchor="w", justify="left", wraplength=300)
            self._mensaje.pack(fill="x", pady=(2, 0))
            self.bind("<Configure>", self._ajustar, add="+")

    def _ajustar(self, evento):
        if self._mensaje is not None:
            self._mensaje.configure(wraplength=max(200, evento.width - 90))


class Campo(tk.Entry):
    """Casilla de ingreso de datos con resaltado de error."""

    def __init__(self, master, variable: tk.StringVar | None = None, ancho: int = 10,
                 alinear: str = "center", **kwargs):
        super().__init__(master, textvariable=variable, width=ancho, justify=alinear, relief="flat",
                         bd=0, bg=COLORES["superficie"], fg=COLORES["texto"],
                         insertbackground=COLORES["texto"], highlightthickness=1,
                         highlightbackground=COLORES["borde_fuerte"], highlightcolor=COLORES["primario"],
                         font=FUENTES["base"], disabledbackground=COLORES["fondo"], **kwargs)
        self.con_error = False
        self.fondo_normal = COLORES["superficie"]
        self.bind("<KeyRelease>", lambda e: self.limpiar_error(), add="+")
        self.bind("<FocusIn>", lambda e: self.after_idle(self._seleccionar), add="+")
        self.bind("<Return>", self._siguiente, add="+")

    def _seleccionar(self):
        try:
            self.select_range(0, "end")
        except tk.TclError:
            pass

    def _siguiente(self, _evento):
        siguiente = self.tk_focusNext()
        if siguiente is not None:
            siguiente.focus_set()
        return "break"

    def establecer_fondo(self, color: str) -> None:
        """Cambia el color normal de la casilla (se recupera al corregir un error)."""
        self.fondo_normal = color
        self.configure(bg=color)

    def marcar_error(self) -> None:
        self.con_error = True
        self.configure(bg=COLORES["error_suave"], highlightbackground=COLORES["error"],
                       highlightcolor=COLORES["error"])

    def limpiar_error(self) -> None:
        if self.con_error:
            self.con_error = False
            self.configure(bg=self.fondo_normal, highlightbackground=COLORES["borde_fuerte"],
                           highlightcolor=COLORES["primario"])


class TextoRico(tk.Frame):
    """Texto de solo lectura con estilos. Permite seleccionar y copiar (Ctrl+C)."""

    TECLAS_PERMITIDAS = {"Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next",
                         "Shift_L", "Shift_R", "Control_L", "Control_R"}

    def __init__(self, master, alto: int = 12, fondo: str | None = None, **kwargs):
        fondo = fondo or COLORES["superficie"]
        super().__init__(master, bg=fondo, **kwargs)
        self.texto = tk.Text(self, wrap="word", height=alto, font=FUENTES["base"], bg=fondo,
                             fg=COLORES["texto"], relief="flat", bd=0, padx=14, pady=12,
                             highlightthickness=0, spacing1=1, spacing3=3, cursor="arrow",
                             selectbackground=COLORES["primario_suave"],
                             selectforeground=COLORES["texto"], insertwidth=0)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.texto.yview)
        self.texto.configure(yscrollcommand=barra.set)
        self.texto.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self._configurar_etiquetas()
        self.texto.bind("<Key>", self._solo_lectura)
        for evento in ("<<Paste>>", "<<Cut>>", "<<Clear>>"):
            self.texto.bind(evento, lambda e: "break")
        self.texto.bind("<Button-1>", lambda e: self.texto.focus_set(), add="+")

    def _solo_lectura(self, evento):
        if evento.state & 0x000C and evento.keysym.lower() in ("c", "a"):   # Ctrl (o Cmd en Mac)
            if evento.keysym.lower() == "a":
                self.texto.tag_add("sel", "1.0", "end")
                return "break"
            return None
        if evento.keysym in self.TECLAS_PERMITIDAS:
            return None
        return "break"

    def _configurar_etiquetas(self):
        t, c = self.texto, COLORES
        t.tag_configure("titulo", font=FUENTES["h2"], foreground=c["primario_texto"], spacing1=10,
                        spacing3=6)
        t.tag_configure("subtitulo", font=FUENTES["h3"], foreground=c["texto"], spacing1=8, spacing3=3)
        t.tag_configure("negrita", font=FUENTES["base_negrita"])
        t.tag_configure("suave", foreground=c["texto_suave"])
        t.tag_configure("pequena", font=FUENTES["pequena"], foreground=c["texto_suave"])
        t.tag_configure("mono", font=FUENTES["mono"])
        t.tag_configure("formula", font=FUENTES["mono"], background=c["superficie_alt"],
                        lmargin1=18, lmargin2=18, foreground=COLORES["texto"])
        t.tag_configure("vineta", lmargin1=14, lmargin2=30)
        t.tag_configure("exito", foreground=c["exito"], font=FUENTES["base_negrita"])
        t.tag_configure("error", foreground=c["error"], font=FUENTES["base_negrita"])
        t.tag_configure("advertencia", foreground=c["advertencia"], font=FUENTES["base_negrita"])
        t.tag_configure("info", foreground=c["info"], font=FUENTES["base_negrita"])
        t.tag_configure("entra", foreground=COLORES["info"], font=FUENTES["base_negrita"])
        t.tag_configure("sale", foreground=COLORES["advertencia"], font=FUENTES["base_negrita"])
        t.tag_configure("pivote", background=c["celda_pivote"], foreground="#FFFFFF",
                        font=FUENTES["base_negrita"])
        t.tag_configure("resaltado", background=c["razon_minima"])
        t.tag_configure("alternativo", foreground=c["alternativo_texto"], font=FUENTES["base_negrita"])

    def limpiar(self) -> None:
        self.texto.delete("1.0", "end")

    def escribir(self, texto: str, *etiquetas) -> None:
        self.texto.insert("end", texto, etiquetas)

    def escribir_bloques(self, bloques) -> None:
        """``bloques`` = lista de (texto, etiquetas). Cada texto debe incluir sus saltos de línea."""
        for texto, etiquetas in bloques:
            if isinstance(etiquetas, str):
                etiquetas = (etiquetas,) if etiquetas else ()
            self.texto.insert("end", texto, tuple(etiquetas))

    def mostrar(self, bloques) -> None:
        self.limpiar()
        self.escribir_bloques(bloques)
        self.texto.yview_moveto(0)

    def contenido(self) -> str:
        return self.texto.get("1.0", "end-1c")


class Leyenda(tk.Frame):
    """Fila de muestras de color: [■ Columna pivote] [■ Fila pivote] ..."""

    def __init__(self, master, elementos, fondo: str | None = None, **kwargs):
        fondo = fondo or COLORES["superficie"]
        super().__init__(master, bg=fondo, **kwargs)
        for color, texto in elementos:
            caja = tk.Frame(self, bg=fondo)
            caja.pack(side="left", padx=(0, 14))
            tk.Frame(caja, bg=color, width=14, height=14, highlightthickness=1,
                     highlightbackground=COLORES["borde_fuerte"]).pack(side="left", padx=(0, 5))
            tk.Label(caja, text=texto, font=FUENTES["pequena"], bg=fondo,
                     fg=COLORES["texto_suave"]).pack(side="left")


def etiqueta(master, texto: str, fuente: str = "base", color: str = "texto", fondo: str = "superficie",
             **kwargs) -> tk.Label:
    """Atajo para crear etiquetas con los colores y fuentes del tema."""
    return tk.Label(master, text=texto, font=FUENTES[fuente], fg=COLORES.get(color, color),
                    bg=COLORES.get(fondo, fondo), **kwargs)


def tarjeta_dato(master, titulo: str, valor: str, color: str = "primario", detalle: str = ""):
    """Recuadro con un dato grande (KPI)."""
    caja = tk.Frame(master, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
    tk.Frame(caja, bg=COLORES[color], height=4).pack(fill="x")
    tk.Label(caja, text=titulo, font=FUENTES["pequena_negrita"], bg=COLORES["superficie"],
             fg=COLORES["texto_suave"], anchor="w").pack(fill="x", padx=14, pady=(10, 0))
    tk.Label(caja, text=valor, font=FUENTES["grande"] if len(valor) <= 9 else FUENTES["h2"],
             bg=COLORES["superficie"], fg=COLORES[color], anchor="w").pack(fill="x", padx=14)
    if detalle:
        texto = tk.Label(caja, text=detalle, font=FUENTES["pequena"], bg=COLORES["superficie"],
                         fg=COLORES["texto_suave"], anchor="w", justify="left", wraplength=150)
        texto.pack(fill="x", padx=14, pady=(0, 10))
        caja.bind("<Configure>", lambda e: texto.configure(wraplength=max(120, e.width - 34)), add="+")
    else:
        tk.Frame(caja, bg=COLORES["superficie"], height=10).pack()
    return caja


def mostrar_avisos(contenedor, casos) -> None:
    orden = {"error": 0, "advertencia": 1, "exito": 2, "info": 3}
    for caso in sorted(casos, key=lambda c: orden.get(c.nivel, 9)):
        Aviso(contenedor, caso.nivel, caso.titulo, caso.mensaje).pack(fill="x", pady=(0, 8))


class DesplazableHorizontal(tk.Frame):
    """Contenedor para una tabla ancha: si no cabe, aparece una barra horizontal SOLO para la tabla
    (el resto de la página conserva su ancho y el texto se sigue leyendo sin desplazarse)."""

    def __init__(self, master, fondo: str | None = None, **kwargs):
        fondo = fondo or COLORES["superficie"]
        super().__init__(master, bg=fondo, **kwargs)
        self.canvas = tk.Canvas(self, bg=fondo, highlightthickness=0, bd=0, width=100, height=10,
                                xscrollincrement=20)
        self.barra = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.barra.set)
        self.canvas.pack(side="top", fill="x", expand=True)
        self.interior = tk.Frame(self.canvas, bg=fondo)
        self.canvas.create_window(0, 0, window=self.interior, anchor="nw")
        for widget in (self, self.canvas, self.interior):
            widget._desplazable_horizontal = self
        self.interior.bind("<Configure>", self._ajustar)
        self.canvas.bind("<Configure>", self._ajustar)

    def _ajustar(self, _evento=None):
        ancho, alto = self.interior.winfo_reqwidth(), self.interior.winfo_reqheight()
        if int(self.canvas.cget("height")) != alto:
            self.canvas.configure(height=alto)
        self.canvas.configure(scrollregion=(0, 0, ancho, alto))
        necesita = ancho > self.canvas.winfo_width() > 1
        if necesita and not self.barra.winfo_ismapped():
            self.barra.pack(side="top", fill="x")
        elif not necesita and self.barra.winfo_ismapped():
            self.barra.pack_forget()
            self.canvas.xview_moveto(0)

    def desplazar(self, pasos: int) -> None:
        if self.barra.winfo_ismapped():
            self.canvas.xview_scroll(pasos, "units")


def tabla_desplazable(master, clase, *args, **kwargs):
    """Crea una tabla (TablaCanvas o TablaTransporteCanvas) dentro de un DesplazableHorizontal."""
    contenedor = DesplazableHorizontal(master, fondo=master.cget("bg"))
    contenedor.pack(fill="x", anchor="w")
    tabla = clase(contenedor.interior, *args, **kwargs)
    tabla.pack(anchor="w")
    return tabla


class FilaFlexible(tk.Frame):
    """Fila de tarjetas que pasa a varias filas cuando la ventana es angosta."""

    def __init__(self, master, ancho_minimo: int = 210, separacion: int = 10, **kwargs):
        super().__init__(master, bg=master.cget("bg"), **kwargs)
        self.ancho_minimo, self.separacion = px(ancho_minimo), separacion
        self.elementos = []
        self._columnas = 0
        self.bind("<Configure>", self._reorganizar)

    def agregar(self, widget) -> None:
        self.elementos.append(widget)
        self._columnas = 0
        self._reorganizar()

    def _reorganizar(self, _evento=None):
        if not self.elementos:
            return
        ancho = self.winfo_width() if self.winfo_width() > 1 else len(self.elementos) * (self.ancho_minimo + 10)
        columnas = max(1, min(len(self.elementos), (ancho + self.separacion) // (self.ancho_minimo + self.separacion)))
        if columnas == self._columnas:
            return
        self._columnas = columnas
        for k in range(len(self.elementos) + 1):
            self.grid_columnconfigure(k, weight=0, uniform="")
        for k, widget in enumerate(self.elementos):
            fila, columna = divmod(k, columnas)
            widget.grid(row=fila, column=columna, sticky="nsew",
                        padx=(0, self.separacion if columna < columnas - 1 else 0), pady=(0, self.separacion))
        for k in range(columnas):
            self.grid_columnconfigure(k, weight=1, uniform="tarjetas")

