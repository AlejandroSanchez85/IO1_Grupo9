"""
vista/simplex/panel_datos_simplex.py
====================================
Pantalla de INGRESO DE DATOS del Simplex. El usuario escribe:
  * nombre del problema, objetivo (max/min), qué mide z y su unidad,
  * número de variables y de restricciones (1 a 8),
  * nombre, unidad y coeficiente c_j de cada variable,
  * nombre, coeficientes a_ij, lado derecho b_i y unidad de cada restricción.

La vista NO valida ni calcula: entrega los textos al controlador.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..componentes import Campo, MarcoDesplazable, Tarjeta, TextoRico, etiqueta
from ..explicaciones.textos_simplex import expresion_lineal
from ..formato import FORMATO
from ..tema import COLORES, FUENTES
from modelo.numeros import convertir_numero

MAX_N = 8
MAX_M = 8


class PanelDatosSimplex(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.controlador = None
        self.n, self.m = 2, 2
        self.var_n = tk.StringVar(value="2")
        self.var_m = tk.StringVar(value="2")
        self.var_nombre = tk.StringVar(value="Nuevo problema de PL")
        self.var_descripcion = tk.StringVar()
        self.var_sentido = tk.StringVar(value="max")
        self.var_desc_z = tk.StringVar(value="Utilidad")
        self.var_unidad_z = tk.StringVar(value="$")
        self.var_ejemplo = tk.StringVar()
        self.nombres_var, self.unidades_var, self.coef_c = [], [], []
        self.nombres_res, self.unidades_res, self.coef_a, self.lado_b = [], [], [], []
        self.campos = {}
        self._vista_previa_pendiente = None
        self._crear_barra()
        self.marco = MarcoDesplazable(self)
        self.marco.pack(fill="both", expand=True)
        self._crear_contenido(self.marco.interior)
        self._redimensionar(2, 2)

    # ------------------------------------------------------------ estructura
    def _crear_barra(self):
        barra = tk.Frame(self, bg=COLORES["superficie"], highlightbackground=COLORES["borde"],
                         highlightthickness=1)
        barra.pack(fill="x", padx=0, pady=(0, 2))
        interior = tk.Frame(barra, bg=COLORES["superficie"])
        interior.pack(fill="x", padx=14, pady=10)
        # El botón Resolver se coloca primero para que siempre quede visible
        ttk.Button(interior, text="Resolver con Simplex  ►", style="Primario.TButton",
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
        # Tarjeta 1: datos generales
        t1 = Tarjeta(contenedor, "1. Datos generales del problema",
                     "Escriba el nombre, el objetivo y el tamaño. Puede cambiar el tamaño en cualquier momento "
                     "sin perder lo que ya escribió.")
        t1.pack(fill="x", pady=(0, 12))
        g = t1.cuerpo
        etiqueta(g, "Nombre del problema").grid(row=0, column=0, sticky="w", pady=4)
        Campo(g, self.var_nombre, ancho=50, alinear="left").grid(row=0, column=1, columnspan=3, sticky="we",
                                                                 pady=4, ipady=4)
        etiqueta(g, "Descripción (opcional)").grid(row=1, column=0, sticky="w", pady=4)
        Campo(g, self.var_descripcion, ancho=50, alinear="left").grid(row=1, column=1, columnspan=3,
                                                                      sticky="we", pady=4, ipady=4)
        etiqueta(g, "Objetivo").grid(row=2, column=0, sticky="w", pady=4)
        caja = tk.Frame(g, bg=COLORES["superficie"])
        caja.grid(row=2, column=1, sticky="w", pady=4)
        ttk.Radiobutton(caja, text="Maximizar z", value="max", variable=self.var_sentido,
                        command=self._programar_vista_previa).pack(side="left", padx=(0, 14))
        ttk.Radiobutton(caja, text="Minimizar z", value="min", variable=self.var_sentido,
                        command=self._programar_vista_previa).pack(side="left")
        etiqueta(g, "¿Qué mide z?  (ej. Utilidad semanal)").grid(row=3, column=0, sticky="w", pady=4)
        Campo(g, self.var_desc_z, ancho=26, alinear="left").grid(row=3, column=1, sticky="w", pady=4, ipady=4)
        etiqueta(g, "Unidad de z  (ej. COP/semana)").grid(row=3, column=2, sticky="e", padx=(16, 8), pady=4)
        Campo(g, self.var_unidad_z, ancho=18, alinear="left").grid(row=3, column=3, sticky="w", pady=4, ipady=4)
        etiqueta(g, "Número de variables (1 a 8)").grid(row=4, column=0, sticky="w", pady=4)
        self.spin_n = ttk.Spinbox(g, from_=1, to=MAX_N, textvariable=self.var_n, width=5, state="readonly",
                                  command=self._aplicar_tamano)
        self.spin_n.grid(row=4, column=1, sticky="w", pady=4)
        etiqueta(g, "Número de restricciones (1 a 8)").grid(row=4, column=2, sticky="e", padx=(16, 8), pady=4)
        self.spin_m = ttk.Spinbox(g, from_=1, to=MAX_M, textvariable=self.var_m, width=5, state="readonly",
                                  command=self._aplicar_tamano)
        self.spin_m.grid(row=4, column=3, sticky="w", pady=4)
        g.grid_columnconfigure(1, weight=1)
        self.campos[("n",)] = self.spin_n
        self.campos[("m",)] = self.spin_m

        # Tarjeta 2: modelo
        self.tarjeta_modelo = Tarjeta(
            contenedor, "2. Modelo: variables, función objetivo y restricciones (todas ≤)",
            "c_j = aporte a z por cada unidad de la variable (unidad de z por unidad de la variable). "
            "a_ij = cantidad del recurso i que usa 1 unidad de la variable j. b_i = cantidad disponible del "
            "recurso i. Escriba 0 si la variable no usa ese recurso.")
        self.tarjeta_modelo.pack(fill="x", pady=(0, 12))
        acciones = tk.Frame(self.tarjeta_modelo.cuerpo, bg=COLORES["superficie"])
        acciones.pack(fill="x", pady=(0, 8))
        ttk.Button(acciones, text="Rellenar vacíos con 0", style="Chico.TButton",
                   command=self._rellenar_ceros).pack(side="left")
        etiqueta(acciones, "  Números: 12 · 2.5 · 2,5 · 3/4 · 1e3  (sin separador de miles)", "pequena",
                 "texto_suave").pack(side="left", padx=8)
        self.rejilla = tk.Frame(self.tarjeta_modelo.cuerpo, bg=COLORES["superficie"])
        self.rejilla.pack(fill="x", anchor="w")

        # Tarjeta 3: vista previa
        t3 = Tarjeta(contenedor, "3. Vista previa del modelo matemático",
                     "Se actualiza mientras escribe. Revísela antes de resolver.")
        t3.pack(fill="x", pady=(0, 12))
        self.vista_previa = TextoRico(t3.cuerpo, alto=12, fondo=COLORES["superficie_alt"])
        self.vista_previa.pack(fill="x")

    # ------------------------------------------------------- tamaño variable
    def _aplicar_tamano(self):
        try:
            n = min(MAX_N, max(1, int(self.var_n.get())))
            m = min(MAX_M, max(1, int(self.var_m.get())))
        except ValueError:
            n, m = self.n, self.m
        self._redimensionar(n, m)

    def _redimensionar(self, n: int, m: int):
        def ajustar(lista, cantidad, crear):
            while len(lista) < cantidad:
                lista.append(crear(len(lista)))
            del lista[cantidad:]

        ajustar(self.nombres_var, n, lambda j: tk.StringVar(value=f"Producto {j + 1}"))
        ajustar(self.unidades_var, n, lambda j: tk.StringVar(value="unidades"))
        ajustar(self.coef_c, n, lambda j: tk.StringVar())
        ajustar(self.nombres_res, m, lambda i: tk.StringVar(value=f"Recurso {i + 1}"))
        ajustar(self.unidades_res, m, lambda i: tk.StringVar(value="unidades"))
        ajustar(self.lado_b, m, lambda i: tk.StringVar())
        ajustar(self.coef_a, m, lambda i: [])
        for fila in self.coef_a:
            ajustar(fila, n, lambda j: tk.StringVar())
        self.n, self.m = n, m
        self.var_n.set(str(n))
        self.var_m.set(str(m))
        self._construir_rejilla()
        self._programar_vista_previa()

    def _construir_rejilla(self):
        for hijo in self.rejilla.winfo_children():
            hijo.destroy()
        self.marco.reiniciar_ancho()                 # la tabla puede volverse más angosta
        for clave in [k for k in self.campos if k[0] not in ("n", "m")]:
            del self.campos[clave]
        g = self.rejilla
        fondo = COLORES["superficie"]
        n, m = self.n, self.m

        def rotulo(texto, fila, columna, **kw):
            lbl = tk.Label(g, text=texto, font=FUENTES["pequena_negrita"], bg=fondo, fg=COLORES["texto_suave"],
                           **kw)
            lbl.grid(row=fila, column=columna, padx=3, pady=(6, 2), sticky="w")
            return lbl

        # Encabezado de variables
        rotulo("", 0, 0)
        for j in range(n):
            tk.Label(g, text=f"x{j + 1}", font=FUENTES["h3"], bg=fondo, fg=COLORES["primario"]).grid(
                row=0, column=1 + j, pady=(0, 2))
        filas_var = (("Nombre de la variable", self.nombres_var, "nombre_var", 15, "left"),
                     ("Unidad (ej. sillas/semana)", self.unidades_var, "unidad_var", 15, "left"),
                     ("c_j: aporte a z por unidad", self.coef_c, "c", 15, "center"))
        for f, (texto, variables, clave, ancho, alinear) in enumerate(filas_var, start=1):
            rotulo(texto, f, 0)
            for j in range(n):
                campo = Campo(g, variables[j], ancho=ancho, alinear=alinear)
                campo.grid(row=f, column=1 + j, padx=3, pady=3, ipady=4, sticky="we")
                self.campos[(clave, j)] = campo
        sentido = tk.Label(g, text="", font=FUENTES["pequena"], bg=fondo, fg=COLORES["texto_suave"])
        sentido.grid(row=3, column=1 + n, columnspan=3, sticky="w", padx=6)
        self.etiqueta_unidad_c = sentido

        ttk.Separator(g, orient="horizontal").grid(row=4, column=0, columnspan=n + 4, sticky="we", pady=10)
        rotulo("Nombre de la restricción / recurso", 5, 0)
        self.encabezados_coef = []
        for j in range(n):
            lbl = tk.Label(g, text="", font=FUENTES["pequena_negrita"], bg=fondo, fg=COLORES["primario_texto"],
                           wraplength=110, justify="center")
            lbl.grid(row=5, column=1 + j, padx=3, pady=(6, 2))
            self.encabezados_coef.append(lbl)
        rotulo("", 5, 1 + n)
        rotulo("b_i (disponible)", 5, 2 + n)
        rotulo("Unidad del recurso", 5, 3 + n)
        for i in range(m):
            fila = 6 + i
            campo = Campo(g, self.nombres_res[i], ancho=24, alinear="left")
            campo.grid(row=fila, column=0, padx=3, pady=3, ipady=4, sticky="we")
            self.campos[("nombre_res", i)] = campo
            for j in range(n):
                campo = Campo(g, self.coef_a[i][j], ancho=15)
                campo.grid(row=fila, column=1 + j, padx=3, pady=3, ipady=4, sticky="we")
                self.campos[("a", i, j)] = campo
            tk.Label(g, text="≤", font=FUENTES["h2"], bg=fondo, fg=COLORES["texto"]).grid(row=fila, column=1 + n,
                                                                                        padx=6)
            campo = Campo(g, self.lado_b[i], ancho=12)
            campo.grid(row=fila, column=2 + n, padx=3, pady=3, ipady=4, sticky="we")
            self.campos[("b", i)] = campo
            campo = Campo(g, self.unidades_res[i], ancho=16, alinear="left")
            campo.grid(row=fila, column=3 + n, padx=3, pady=3, ipady=4, sticky="we")
            self.campos[("unidad_res", i)] = campo
        tk.Label(g, text="  " + ", ".join(f"x{j + 1}" for j in range(n)) + " ≥ 0   (no negatividad)",
                 font=FUENTES["base"], bg=fondo, fg=COLORES["texto_suave"]).grid(
            row=6 + m, column=0, columnspan=n + 4, sticky="w", pady=(8, 0))
        for variable in self._todas_las_variables():
            if not getattr(variable, "_con_traza", False):
                variable.trace_add("write", lambda *_: self._programar_vista_previa())
                variable._con_traza = True
        self._actualizar_encabezados()

    def _todas_las_variables(self):
        variables = [self.var_nombre, self.var_descripcion, self.var_desc_z, self.var_unidad_z]
        variables += self.nombres_var + self.unidades_var + self.coef_c + self.nombres_res + self.unidades_res
        variables += self.lado_b + [v for fila in self.coef_a for v in fila]
        return variables

    def _actualizar_encabezados(self):
        for j, lbl in enumerate(getattr(self, "encabezados_coef", [])):
            if lbl.winfo_exists():
                nombre = self.nombres_var[j].get().strip() or f"x{j + 1}"
                lbl.configure(text=f"a_i{j + 1}\n({nombre})")
        if hasattr(self, "etiqueta_unidad_c") and self.etiqueta_unidad_c.winfo_exists():
            self.etiqueta_unidad_c.configure(text=f"← en {self.var_unidad_z.get().strip() or 'unidades de z'} "
                                                  f"por unidad de cada variable")

    def _rellenar_ceros(self):
        for variable in self.coef_c + self.lado_b + [v for fila in self.coef_a for v in fila]:
            if variable.get().strip() == "":
                variable.set("0")

    # --------------------------------------------------------- vista previa
    def _programar_vista_previa(self):
        if self._vista_previa_pendiente is not None:
            self.after_cancel(self._vista_previa_pendiente)
        self._vista_previa_pendiente = self.after(350, self._actualizar_vista_previa)

    def _actualizar_vista_previa(self):
        self._vista_previa_pendiente = None
        self._actualizar_encabezados()
        simbolos = [f"x{j + 1}" for j in range(self.n)]

        def numeros(variables):
            valores = []
            for v in variables:
                try:
                    valores.append(convertir_numero(v.get()))
                except ValueError:
                    return None
            return valores

        sentido = "Maximizar" if self.var_sentido.get() == "max" else "Minimizar"
        bloques = []
        c = numeros(self.coef_c)
        objetivo = expresion_lineal(c, simbolos, FORMATO) if c is not None else "(faltan coeficientes c_j)"
        bloques.append((f"{sentido}  z = {objetivo}   [{self.var_unidad_z.get().strip()}]\n", ("formula",)))
        bloques.append(("Sujeto a:\n", ("negrita",)))
        for i in range(self.m):
            a = numeros(self.coef_a[i])
            b = numeros([self.lado_b[i]])
            izquierda = expresion_lineal(a, simbolos, FORMATO) if a is not None else "(faltan datos)"
            derecha = FORMATO.num(b[0]) if b is not None else "?"
            bloques.append((f"  {izquierda} ≤ {derecha}", ("formula",)))
            bloques.append((f"    ← {self.nombres_res[i].get().strip()} [{self.unidades_res[i].get().strip()}]\n",
                            ("suave",)))
        bloques.append((f"  {', '.join(simbolos)} ≥ 0\n", ("formula",)))
        leyenda = ";  ".join(f"x{j + 1} = {self.nombres_var[j].get().strip()} ({self.unidades_var[j].get().strip()})"
                             for j in range(self.n))
        bloques.append((f"\n{leyenda}\n", ("pequena",)))
        self.vista_previa.mostrar(bloques)

    # ----------------------------------------------------- API para el controlador
    def _llamar(self, metodo, *args):
        if self.controlador is not None:
            getattr(self.controlador, metodo)(*args)

    def establecer_ejemplos(self, titulos):
        self.combo_ejemplos.configure(values=list(titulos))
        if titulos:
            self.combo_ejemplos.current(0)

    def obtener_datos(self) -> dict:
        """Devuelve los textos escritos por el usuario (sin convertir)."""
        return {
            "tipo": "simplex",
            "titulo": self.var_nombre.get().strip(),
            "nombre": self.var_nombre.get().strip(),
            "descripcion": self.var_descripcion.get().strip(),
            "sentido": self.var_sentido.get(),
            "descripcion_z": self.var_desc_z.get().strip(),
            "unidad_z": self.var_unidad_z.get().strip(),
            "variables": [{"nombre": self.nombres_var[j].get(), "unidad": self.unidades_var[j].get(),
                           "c": self.coef_c[j].get()} for j in range(self.n)],
            "restricciones": [{"nombre": self.nombres_res[i].get(), "unidad": self.unidades_res[i].get(),
                               "a": [v.get() for v in self.coef_a[i]], "signo": "<=", "b": self.lado_b[i].get()}
                              for i in range(self.m)],
        }

    def cargar_datos(self, datos: dict) -> None:
        """Llena el formulario con los datos de un ejemplo o archivo."""
        variables = list(datos.get("variables") or [])[:MAX_N]
        restricciones = list(datos.get("restricciones") or [])[:MAX_M]
        self._redimensionar(max(1, len(variables)), max(1, len(restricciones)))
        texto = lambda v: "" if v is None else str(v)
        self.var_nombre.set(texto(datos.get("nombre") or datos.get("titulo")))
        self.var_descripcion.set(texto(datos.get("descripcion")))
        self.var_sentido.set("min" if str(datos.get("sentido", "max")).lower().startswith("min") else "max")
        self.var_desc_z.set(texto(datos.get("descripcion_z")))
        self.var_unidad_z.set(texto(datos.get("unidad_z")))
        for j, v in enumerate(variables):
            self.nombres_var[j].set(texto(v.get("nombre")))
            self.unidades_var[j].set(texto(v.get("unidad")))
            self.coef_c[j].set(texto(v.get("c")))
        for i, r in enumerate(restricciones):
            self.nombres_res[i].set(texto(r.get("nombre")))
            self.unidades_res[i].set(texto(r.get("unidad")))
            self.lado_b[i].set(texto(r.get("b")))
            coeficientes = list(r.get("a") or [])
            for j in range(self.n):
                self.coef_a[i][j].set(texto(coeficientes[j]) if j < len(coeficientes) else "")
        self.limpiar_errores()
        self.marco.al_inicio()
        self._actualizar_vista_previa()

    def limpiar_formulario(self) -> None:
        self.cargar_datos({"nombre": "Nuevo problema de PL", "sentido": "max", "descripcion_z": "Utilidad",
                           "unidad_z": "$",
                           "variables": [{"nombre": f"Producto {j + 1}", "unidad": "unidades", "c": ""}
                                         for j in range(2)],
                           "restricciones": [{"nombre": f"Recurso {i + 1}", "unidad": "unidades",
                                              "a": ["", ""], "b": ""} for i in range(2)]})

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
