"""
vista/vogel/panel_datos_vogel.py
================================
Pantalla de INGRESO DE DATOS del problema de transporte (Vogel). Se
escribe como en los libros: destinos arriba, orígenes a la izquierda,
costos unitarios en el centro, oferta a la derecha y demanda abajo.
Muestra en vivo si el problema está balanceado.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from modelo.numeros import convertir_numero
from ..componentes import Campo, MarcoDesplazable, Tarjeta, etiqueta
from ..formato import FORMATO
from ..tema import COLORES, FUENTES

MAX_ORIGENES = 8
MAX_DESTINOS = 8


class PanelDatosVogel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.controlador = None
        self.m, self.n = 3, 3
        self.var_m = tk.StringVar(value="3")
        self.var_n = tk.StringVar(value="3")
        self.var_nombre = tk.StringVar(value="Nuevo problema de transporte")
        self.var_descripcion = tk.StringVar()
        self.var_unidad = tk.StringVar(value="unidades")
        self.var_moneda = tk.StringVar(value="$")
        self.var_ejemplo = tk.StringVar()
        self.nombres_o, self.ofertas, self.nombres_d, self.demandas, self.costos = [], [], [], [], []
        self.campos = {}
        self._pendiente = None
        self._crear_barra()
        self.marco = MarcoDesplazable(self)
        self.marco.pack(fill="both", expand=True)
        self._crear_contenido(self.marco.interior)
        self._redimensionar(3, 3)

    # ------------------------------------------------------------ estructura
    def _crear_barra(self):
        barra = tk.Frame(self, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
        barra.pack(fill="x", pady=(0, 2))
        interior = tk.Frame(barra, bg=COLORES["superficie"])
        interior.pack(fill="x", padx=14, pady=10)
        # El botón Resolver se coloca primero para que siempre quede visible
        ttk.Button(interior, text="Resolver con Vogel  ►", style="Primario.TButton",
                   command=lambda: self._llamar("resolver")).pack(side="right")
        etiqueta(interior, "Ejemplos precargados:", "base_negrita").pack(side="left")
        self.combo_ejemplos = ttk.Combobox(interior, textvariable=self.var_ejemplo, state="readonly", width=40)
        self.combo_ejemplos.pack(side="left", padx=(8, 6))
        ttk.Button(interior, text="Cargar ejemplo", style="Chico.TButton",
                   command=lambda: self._llamar("cargar_ejemplo", self.combo_ejemplos.current())).pack(side="left")
        ttk.Separator(interior, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(interior, text="Abrir…", style="Chico.TButton",
                   command=lambda: self._llamar("abrir_archivo")).pack(side="left", padx=2)
        ttk.Button(interior, text="Guardar…", style="Chico.TButton",
                   command=lambda: self._llamar("guardar_archivo")).pack(side="left", padx=2)
        ttk.Button(interior, text="Limpiar", style="Chico.TButton",
                   command=lambda: self._llamar("limpiar")).pack(side="left", padx=2)

    def _crear_contenido(self, contenedor):
        contenedor.configure(padx=18, pady=14)
        t1 = Tarjeta(contenedor, "1. Datos generales del problema de transporte",
                     "Escriba el nombre, la unidad del producto que se transporta y la moneda del costo. Luego "
                     "el número de orígenes (plantas, bodegas...) y de destinos (clientes, tiendas...).")
        t1.pack(fill="x", pady=(0, 12))
        g = t1.cuerpo
        etiqueta(g, "Nombre del problema").grid(row=0, column=0, sticky="w", pady=4)
        Campo(g, self.var_nombre, ancho=50, alinear="left").grid(row=0, column=1, columnspan=3, sticky="we", pady=4,
                                                                 ipady=4)
        etiqueta(g, "Descripción (opcional)").grid(row=1, column=0, sticky="w", pady=4)
        Campo(g, self.var_descripcion, ancho=50, alinear="left").grid(row=1, column=1, columnspan=3, sticky="we",
                                                                      pady=4, ipady=4)
        etiqueta(g, "Unidad del producto  (ej. cajas, toneladas)").grid(row=2, column=0, sticky="w", pady=4)
        Campo(g, self.var_unidad, ancho=20, alinear="left").grid(row=2, column=1, sticky="w", pady=4, ipady=4)
        etiqueta(g, "Moneda del costo  (ej. COP)").grid(row=2, column=2, sticky="e", padx=(16, 8), pady=4)
        Campo(g, self.var_moneda, ancho=14, alinear="left").grid(row=2, column=3, sticky="w", pady=4, ipady=4)
        etiqueta(g, "Número de orígenes (1 a 8)").grid(row=3, column=0, sticky="w", pady=4)
        self.spin_m = ttk.Spinbox(g, from_=1, to=MAX_ORIGENES, textvariable=self.var_m, width=5, state="readonly",
                                  command=self._aplicar_tamano)
        self.spin_m.grid(row=3, column=1, sticky="w", pady=4)
        etiqueta(g, "Número de destinos (1 a 8)").grid(row=3, column=2, sticky="e", padx=(16, 8), pady=4)
        self.spin_n = ttk.Spinbox(g, from_=1, to=MAX_DESTINOS, textvariable=self.var_n, width=5, state="readonly",
                                  command=self._aplicar_tamano)
        self.spin_n.grid(row=3, column=3, sticky="w", pady=4)
        g.grid_columnconfigure(1, weight=1)
        self.campos[("m",)] = self.spin_m
        self.campos[("n",)] = self.spin_n

        self.tarjeta_tabla = Tarjeta(
            contenedor, "2. Tabla de transporte: costos unitarios, oferta y demanda",
            "Cada casilla del centro es el COSTO de enviar 1 unidad del origen (fila) al destino (columna). "
            "Escriba M si una ruta está prohibida. La oferta es lo máximo que puede enviar cada origen y la "
            "demanda lo que necesita cada destino. Puede estar balanceado o no.")
        self.tarjeta_tabla.pack(fill="x", pady=(0, 12))
        acciones = tk.Frame(self.tarjeta_tabla.cuerpo, bg=COLORES["superficie"])
        acciones.pack(fill="x", pady=(0, 8))
        ttk.Button(acciones, text="Rellenar vacíos con 0", style="Chico.TButton",
                   command=self._rellenar_ceros).pack(side="left")
        self.etiqueta_unidades = etiqueta(acciones, "", "pequena", "texto_suave")
        self.etiqueta_unidades.pack(side="left", padx=10)
        self.rejilla = tk.Frame(self.tarjeta_tabla.cuerpo, bg=COLORES["superficie"])
        self.rejilla.pack(fill="x", anchor="w")
        self.balance = tk.Label(self.tarjeta_tabla.cuerpo, text="", font=FUENTES["base_negrita"], anchor="w",
                                justify="left", padx=12, pady=8, bg=COLORES["info_suave"], fg=COLORES["info"])
        self.balance.pack(fill="x", pady=(12, 0))

        t3 = Tarjeta(contenedor, "Ayuda rápida")
        t3.pack(fill="x", pady=(0, 12))
        for texto in ("• Números: 12 · 2.5 · 2,5 · 3/4 (sin separador de miles: escriba 1250000, no 1.250.000).",
                      "• Si la oferta total es mayor que la demanda se agrega un DESTINO FICTICIO (lo que recibe se "
                      "queda en inventario).",
                      "• Si la demanda total es mayor que la oferta se agrega un ORIGEN FICTICIO (lo que envía es "
                      "demanda insatisfecha).",
                      "• El costo de las rutas ficticias es 0. Una ruta con costo M nunca debería usarse; si el óptimo "
                      "la necesita, el problema es infactible.",
                      "• Vogel da una solución inicial; en la pestaña «6 · MODI» se compara con el óptimo."):
            tk.Label(t3.cuerpo, text=texto, font=FUENTES["base"], bg=COLORES["superficie"], fg=COLORES["texto"],
                     anchor="w", justify="left", wraplength=1100).pack(fill="x", pady=1)

    # ------------------------------------------------------- tamaño variable
    def _aplicar_tamano(self):
        try:
            m = min(MAX_ORIGENES, max(1, int(self.var_m.get())))
            n = min(MAX_DESTINOS, max(1, int(self.var_n.get())))
        except ValueError:
            m, n = self.m, self.n
        self._redimensionar(m, n)

    def _redimensionar(self, m: int, n: int):
        def ajustar(lista, cantidad, crear):
            while len(lista) < cantidad:
                lista.append(crear(len(lista)))
            del lista[cantidad:]

        ajustar(self.nombres_o, m, lambda i: tk.StringVar(value=f"Origen {i + 1}"))
        ajustar(self.ofertas, m, lambda i: tk.StringVar())
        ajustar(self.nombres_d, n, lambda j: tk.StringVar(value=f"Destino {j + 1}"))
        ajustar(self.demandas, n, lambda j: tk.StringVar())
        ajustar(self.costos, m, lambda i: [])
        for fila in self.costos:
            ajustar(fila, n, lambda j: tk.StringVar())
        self.m, self.n = m, n
        self.var_m.set(str(m))
        self.var_n.set(str(n))
        self._construir_rejilla()

    def _construir_rejilla(self):
        for hijo in self.rejilla.winfo_children():
            hijo.destroy()
        self.marco.reiniciar_ancho()                 # la tabla puede volverse más angosta
        for clave in [k for k in self.campos if k[0] not in ("n", "m")]:
            del self.campos[clave]
        g = self.rejilla
        m, n = self.m, self.n
        encabezado = tk.Label(g, text="Origen \\ Destino", font=FUENTES["pequena_negrita"], bg=COLORES["tabla_encabezado"],
                              fg="#FFFFFF", padx=8, pady=6)
        encabezado.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        for j in range(n):
            campo = Campo(g, self.nombres_d[j], ancho=16)
            campo.configure(font=FUENTES["base_negrita"])
            campo.establecer_fondo(COLORES["primario_suave"])
            campo.grid(row=0, column=1 + j, padx=2, pady=2, ipady=5, sticky="we")
            self.campos[("nombre_destino", j)] = campo
        self.etiqueta_oferta = tk.Label(g, text="Oferta", font=FUENTES["pequena_negrita"],
                                        bg=COLORES["tabla_encabezado"], fg="#FFFFFF", padx=8, pady=6)
        self.etiqueta_oferta.grid(row=0, column=1 + n, sticky="nsew", padx=1, pady=1)
        for i in range(m):
            campo = Campo(g, self.nombres_o[i], ancho=18, alinear="left")
            campo.configure(font=FUENTES["base_negrita"])
            campo.establecer_fondo(COLORES["tabla_lateral"])
            campo.grid(row=1 + i, column=0, padx=2, pady=2, ipady=5, sticky="we")
            self.campos[("nombre_origen", i)] = campo
            for j in range(n):
                campo = Campo(g, self.costos[i][j], ancho=16)
                campo.grid(row=1 + i, column=1 + j, padx=2, pady=2, ipady=5, sticky="we")
                self.campos[("costo", i, j)] = campo
            campo = Campo(g, self.ofertas[i], ancho=12)
            campo.establecer_fondo(COLORES["exito_suave"])
            campo.grid(row=1 + i, column=1 + n, padx=2, pady=2, ipady=5, sticky="we")
            self.campos[("oferta", i)] = campo
        self.etiqueta_demanda = tk.Label(g, text="Demanda", font=FUENTES["pequena_negrita"],
                                         bg=COLORES["tabla_encabezado"], fg="#FFFFFF", padx=8, pady=6)
        self.etiqueta_demanda.grid(row=1 + m, column=0, sticky="nsew", padx=1, pady=1)
        for j in range(n):
            campo = Campo(g, self.demandas[j], ancho=16)
            campo.establecer_fondo(COLORES["advertencia_suave"])
            campo.grid(row=1 + m, column=1 + j, padx=2, pady=2, ipady=5, sticky="we")
            self.campos[("demanda", j)] = campo
        self.etiqueta_total = tk.Label(g, text="", font=FUENTES["pequena_negrita"], bg=COLORES["tabla_sub"],
                                       fg=COLORES["texto"], padx=6, pady=6)
        self.etiqueta_total.grid(row=1 + m, column=1 + n, sticky="nsew", padx=1, pady=1)
        variables = [self.var_unidad, self.var_moneda] + self.ofertas + self.demandas + \
                    [v for fila in self.costos for v in fila]
        for variable in variables:
            if not getattr(variable, "_con_traza", False):
                variable.trace_add("write", lambda *_: self._programar_balance())
                variable._con_traza = True
        self._actualizar_balance()

    def _rellenar_ceros(self):
        for variable in self.ofertas + self.demandas + [v for fila in self.costos for v in fila]:
            if variable.get().strip() == "":
                variable.set("0")

    # ------------------------------------------------------ balance en vivo
    def _programar_balance(self):
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(250, self._actualizar_balance)

    def _actualizar_balance(self):
        self._pendiente = None
        unidad = self.var_unidad.get().strip() or "unidades"
        moneda = self.var_moneda.get().strip() or "$"
        self.etiqueta_unidades.configure(text=f"Costos en {moneda} por {unidad}  ·  oferta y demanda en {unidad}")
        if self.etiqueta_oferta.winfo_exists():
            self.etiqueta_oferta.configure(text=f"Oferta\n({unidad})")
            self.etiqueta_demanda.configure(text=f"Demanda\n({unidad})")

        def suma(variables):
            total = 0
            for v in variables:
                try:
                    total += convertir_numero(v.get())
                except ValueError:
                    return None
            return total

        oferta, demanda = suma(self.ofertas), suma(self.demandas)
        if oferta is None or demanda is None:
            self.etiqueta_total.configure(text="—")
            self.balance.configure(text="Complete la oferta y la demanda para ver si el problema está balanceado.",
                                   bg=COLORES["info_suave"], fg=COLORES["info"])
            return
        self.etiqueta_total.configure(text=f"{FORMATO.num(oferta)} / {FORMATO.num(demanda)}")
        if oferta == demanda:
            texto = (f"BALANCEADO: oferta total = demanda total = {FORMATO.num(oferta)} {unidad}.")
            fondo, color = COLORES["exito_suave"], COLORES["exito"]
        elif oferta > demanda:
            texto = (f"DESBALANCEADO: oferta total {FORMATO.num(oferta)} > demanda total {FORMATO.num(demanda)}. Al "
                     f"resolver se agregará un DESTINO FICTICIO con demanda {FORMATO.num(oferta - demanda)} {unidad}.")
            fondo, color = COLORES["advertencia_suave"], COLORES["advertencia"]
        else:
            texto = (f"DESBALANCEADO: demanda total {FORMATO.num(demanda)} > oferta total {FORMATO.num(oferta)}. Al "
                     f"resolver se agregará un ORIGEN FICTICIO con oferta {FORMATO.num(demanda - oferta)} {unidad}.")
            fondo, color = COLORES["advertencia_suave"], COLORES["advertencia"]
        self.balance.configure(text=texto, bg=fondo, fg=color)

    # ----------------------------------------------- API para el controlador
    def _llamar(self, metodo, *args):
        if self.controlador is not None:
            getattr(self.controlador, metodo)(*args)

    def establecer_ejemplos(self, titulos):
        self.combo_ejemplos.configure(values=list(titulos))
        if titulos:
            self.combo_ejemplos.current(0)

    def obtener_datos(self) -> dict:
        return {
            "tipo": "transporte",
            "titulo": self.var_nombre.get().strip(),
            "nombre": self.var_nombre.get().strip(),
            "descripcion": self.var_descripcion.get().strip(),
            "unidad_producto": self.var_unidad.get().strip(),
            "unidad_costo": self.var_moneda.get().strip(),
            "origenes": [{"nombre": self.nombres_o[i].get(), "oferta": self.ofertas[i].get()} for i in range(self.m)],
            "destinos": [{"nombre": self.nombres_d[j].get(), "demanda": self.demandas[j].get()} for j in range(self.n)],
            "costos": [[self.costos[i][j].get() for j in range(self.n)] for i in range(self.m)],
        }

    def cargar_datos(self, datos: dict) -> None:
        origenes = list(datos.get("origenes") or [])[:MAX_ORIGENES]
        destinos = list(datos.get("destinos") or [])[:MAX_DESTINOS]
        self._redimensionar(max(1, len(origenes)), max(1, len(destinos)))
        texto = lambda v: "" if v is None else str(v)
        self.var_nombre.set(texto(datos.get("nombre") or datos.get("titulo")))
        self.var_descripcion.set(texto(datos.get("descripcion")))
        self.var_unidad.set(texto(datos.get("unidad_producto")))
        self.var_moneda.set(texto(datos.get("unidad_costo")))
        for i, o in enumerate(origenes):
            self.nombres_o[i].set(texto(o.get("nombre")))
            self.ofertas[i].set(texto(o.get("oferta")))
        for j, d in enumerate(destinos):
            self.nombres_d[j].set(texto(d.get("nombre")))
            self.demandas[j].set(texto(d.get("demanda")))
        costos = list(datos.get("costos") or [])
        for i in range(self.m):
            fila = list(costos[i]) if i < len(costos) else []
            for j in range(self.n):
                self.costos[i][j].set(texto(fila[j]) if j < len(fila) else "")
        self.limpiar_errores()
        self.marco.al_inicio()
        self._actualizar_balance()

    def limpiar_formulario(self) -> None:
        self.cargar_datos({"nombre": "Nuevo problema de transporte", "unidad_producto": "unidades",
                           "unidad_costo": "$",
                           "origenes": [{"nombre": f"Origen {i + 1}", "oferta": ""} for i in range(3)],
                           "destinos": [{"nombre": f"Destino {j + 1}", "demanda": ""} for j in range(3)],
                           "costos": [["", "", ""] for _ in range(3)]})

    def marcar_errores(self, campos) -> None:
        self.limpiar_errores()
        primero = None
        for campo in campos:
            widget = self.campos.get(tuple(campo))
            if isinstance(widget, Campo):
                widget.marcar_error()
                primero = primero or widget
        if primero is not None:
            primero.focus_set()

    def limpiar_errores(self) -> None:
        for widget in self.campos.values():
            if isinstance(widget, Campo):
                widget.limpiar_error()
