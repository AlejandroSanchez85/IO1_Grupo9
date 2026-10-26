"""
vista/simplex/panel_resultados_simplex.py
=========================================
Paneles de resultados del Simplex:
* PanelModeloSimplex: modelo matemático y forma estándar.
* PanelSolucionSimplex: avisos de casos especiales, resultado final con
  nombres y unidades, uso de recursos y comprobación.
* PanelSensibilidad: precios sombra, costos reducidos y rangos de c_j y b_i.
"""
from __future__ import annotations

import tkinter as tk

from ..componentes import (Aviso, FilaFlexible, MarcoDesplazable, TablaCanvas, Tarjeta, TextoRico, mostrar_avisos,
                           tabla_desplazable, tarjeta_dato)
from ..explicaciones import textos_sensibilidad as TSe
from ..explicaciones import textos_simplex as TS
from ..formato import FORMATO
from ..tema import COLORES, FUENTES


class PanelModeloSimplex(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.problema = None
        self.texto = TextoRico(self, alto=30)
        self.texto.pack(fill="both", expand=True, padx=16, pady=12)
        self.texto.mostrar([("Resuelva un problema para ver aquí su modelo matemático y su forma estándar.\n",
                             ("suave",))])

    def mostrar(self, problema) -> None:
        self.problema = problema
        self.texto.mostrar(TS.bloques_modelo(problema, FORMATO))

    def refrescar(self) -> None:
        if self.problema is not None:
            self.mostrar(self.problema)


class PanelSolucionSimplex(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.area = MarcoDesplazable(self, horizontal=False)
        self.area.pack(fill="both", expand=True)
        tk.Label(self.area.interior, text="Resuelva un problema para ver la solución.", font=FUENTES["subtitulo"],
                 bg=COLORES["fondo"], fg=COLORES["texto_suave"]).pack(pady=40)

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.mostrar(self.resultado)

    def mostrar(self, resultado) -> None:
        self.resultado = resultado
        self.area.limpiar()
        p = resultado.problema
        contenedor = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=18, pady=14)

        # Avisos de casos especiales
        if resultado.es_optimo:
            Aviso(contenedor, "exito", "Solución ÓPTIMA encontrada",
                  TS.texto_plan(resultado, FORMATO)).pack(fill="x", pady=(0, 8))
        mostrar_avisos(contenedor, resultado.casos)

        # Datos clave
        fila = FilaFlexible(contenedor)
        fila.pack(fill="x", pady=(4, 2))
        if resultado.es_optimo:
            z_texto, color = FORMATO.num(resultado.z), "exito"
        elif resultado.estado == "no_acotado":
            z_texto, color = ("+∞" if p.es_max else "−∞"), "error"
        else:
            z_texto, color = "—", "advertencia"
        datos = [(f"z {'máximo' if p.es_max else 'mínimo'} ({p.unidad_z})", z_texto, color, p.descripcion_z),
                 ("Iteraciones (pivoteos)", str(resultado.numero_pivoteos), "primario",
                  f"{len(resultado.iteraciones)} tablas generadas"),
                 ("Estado", {"optimo": "Óptimo", "no_acotado": "No acotado"}.get(resultado.estado, "Detenido"),
                  color, "Método Simplex " + ("maximizando" if p.es_max else "minimizando")),
                 ("Tamaño", f"{p.n} × {p.m}", "secundario", f"{p.n} variables, {p.m} restricciones; "
                                                          f"tiempo {resultado.tiempo_ms:.1f} ms")]
        for titulo, valor, col, detalle in datos:
            fila.agregar(tarjeta_dato(fila, titulo, valor, col, detalle))

        if resultado.estado == "no_acotado":
            k = resultado.columna_no_acotada
            tarjeta = Tarjeta(contenedor, "Diagnóstico del problema no acotado")
            tarjeta.pack(fill="x", pady=(0, 12))
            tk.Label(tarjeta.cuerpo, text=(
                f"La variable {TS.etiqueta_columna(p, k)} puede aumentar sin límite porque ningún coeficiente de su "
                f"columna es positivo en la última tabla. Revise las restricciones del problema: probablemente "
                f"falta un límite de capacidad, de mercado o de presupuesto."), font=FUENTES["base"],
                     bg=COLORES["superficie"], justify="left", anchor="w", wraplength=900).pack(fill="x")
            return

        if not resultado.es_optimo:
            return
        t = resultado.tabla_final
        # Tabla de variables
        tarjeta = Tarjeta(contenedor, "Plan óptimo: variables de decisión",
                          "Resultado final con los nombres y unidades del problema.")
        tarjeta.pack(fill="x", pady=(0, 12))
        filas = [["Variable", "Nombre", "Valor óptimo", "Unidad", "c_j", f"Aporte a z = c_j·x_j ({p.unidad_z})",
                  "¿Básica?"]]
        estilos = {}
        for j, v in enumerate(p.variables):
            valor = t.valor(j)
            filas.append([v.simbolo, v.nombre, FORMATO.num_doble(valor), v.unidad, FORMATO.num(v.coeficiente),
                          FORMATO.num(v.coeficiente * valor), "Sí" if t.es_basica(j) else "No"])
            if valor > 0:
                estilos[(j + 1, 2)] = {"bg": COLORES["optimo"], "negrita": True}
        filas.append(["z*", p.descripcion_z, FORMATO.num_doble(t.z), p.unidad_z, "", FORMATO.num(t.z), ""])
        estilos[(len(filas) - 1, 2)] = {"bg": COLORES["exito"], "fg": "#FFFFFF", "negrita": True}
        tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, alinear={1: "w", 3: "w"}, estilos=estilos)

        # Tabla de restricciones
        tarjeta = Tarjeta(contenedor, "Uso de los recursos (restricciones)",
                          "Holgura = lo que sobra del recurso. Una restricción con holgura 0 está ACTIVA "
                          "(es un cuello de botella).")
        tarjeta.pack(fill="x", pady=(0, 12))
        filas = [["Restricción", "Usado", "Disponible (b)", "Holgura (s)", "Unidad", "% de uso", "Estado"]]
        estilos = {}
        for i, r in enumerate(p.restricciones):
            holgura = t.valor(p.n + i)
            usado = r.lado_derecho - holgura
            porcentaje = f"{float(usado / r.lado_derecho) * 100:.1f} %" if r.lado_derecho != 0 else "—"
            activa = holgura == 0
            filas.append([r.nombre, FORMATO.num(usado), FORMATO.num(r.lado_derecho), FORMATO.num(holgura), r.unidad,
                          porcentaje, "ACTIVA (sin holgura)" if activa else "Con holgura"])
            estilos[(i + 1, 6)] = ({"bg": COLORES["advertencia_suave"], "fg": COLORES["advertencia"], "negrita": True}
                                   if activa else {"fg": COLORES["exito"]})
        tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, alinear={0: "w", 4: "w"}, estilos=estilos)

        # Solución alternativa
        alternativa = resultado.solucion_alternativa()
        if alternativa is not None:
            tarjeta = Tarjeta(contenedor, "Óptimos alternativos: otra solución con el mismo z",
                              "Cualquier combinación λ·S1 + (1 − λ)·S2 con 0 ≤ λ ≤ 1 también es óptima.")
            tarjeta.pack(fill="x", pady=(0, 12))
            filas = [["Variable", "Nombre", "Solución 1 (S1)", "Solución 2 (S2)", "Unidad"]]
            for j, v in enumerate(p.variables):
                filas.append([v.simbolo, v.nombre, FORMATO.num(t.valor(j)), FORMATO.num(alternativa[j]), v.unidad])
            filas.append(["z", p.descripcion_z, FORMATO.num(t.z), FORMATO.num(resultado.iteracion_alternativa.tabla.z),
                          p.unidad_z])
            tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, alinear={1: "w", 4: "w"},
                              estilos_columna={3: {"bg": COLORES["alternativo"]}})

        # Comprobación
        tarjeta = Tarjeta(contenedor, "Comprobación de la solución")
        tarjeta.pack(fill="x", pady=(0, 12))
        texto = TextoRico(tarjeta.cuerpo, alto=min(4 + p.m, 12), fondo=COLORES["superficie_alt"])
        texto.pack(fill="x")
        texto.mostrar(TS.bloques_comprobacion(resultado, FORMATO))


class PanelSensibilidad(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.sensibilidad = None
        self.area = MarcoDesplazable(self, horizontal=False)
        self.area.pack(fill="both", expand=True)
        self.mostrar_mensaje("Resuelva un problema con solución óptima para ver el análisis de sensibilidad.")

    def mostrar_mensaje(self, mensaje: str, nivel: str = "info") -> None:
        self.sensibilidad = None
        self.area.limpiar()
        caja = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        caja.pack(fill="x", padx=18, pady=18)
        Aviso(caja, nivel, "Análisis de sensibilidad", mensaje).pack(fill="x")

    def refrescar(self) -> None:
        if self.sensibilidad is not None:
            self.mostrar(self.sensibilidad)

    def mostrar(self, s) -> None:
        self.sensibilidad = s
        self.area.limpiar()
        p = s.problema
        contenedor = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=18, pady=14)
        mostrar_avisos(contenedor, s.casos)

        # 1) Precios sombra y rangos de b_i
        tarjeta = Tarjeta(contenedor, "Precios sombra y rango de cada b_i (lado derecho)",
                          "Precio sombra y_i = cambio de z por cada unidad adicional del recurso i. Es válido "
                          "mientras b_i esté dentro de su rango.")
        tarjeta.pack(fill="x", pady=(0, 12))
        filas = [["Restricción", "Holgura", "Estado", f"Precio sombra y_i\n({p.unidad_z} por unidad)", "b_i actual",
                  "Disminución\npermitida", "Aumento\npermitido", "b_i mínimo", "b_i máximo", "Unidad"]]
        estilos = {}
        for k, rr in enumerate(s.rangos_recursos, start=1):
            filas.append([rr.nombre, FORMATO.num(rr.holgura), "Activa" if rr.activa else "No activa",
                          FORMATO.num(rr.precio_sombra), FORMATO.num(rr.valor_actual), FORMATO.cambio(rr.disminucion),
                          FORMATO.cambio(rr.aumento), FORMATO.limite_inferior(rr.minimo),
                          FORMATO.limite_superior(rr.maximo), rr.unidad])
            if rr.activa:
                estilos[(k, 2)] = {"bg": COLORES["advertencia_suave"], "fg": COLORES["advertencia"], "negrita": True}
            if rr.precio_sombra != 0:
                estilos[(k, 3)] = {"bg": COLORES["primario_suave"], "fg": COLORES["primario_texto"], "negrita": True}
            for col, valor in ((5, rr.disminucion), (6, rr.aumento), (7, rr.minimo), (8, rr.maximo)):
                if valor is None:
                    estilos[(k, col)] = {"fg": COLORES["info"], "negrita": True}
        tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, alinear={0: "w", 9: "w"}, estilos=estilos)

        # 2) Costos reducidos y rangos de c_j
        tarjeta = Tarjeta(contenedor, "Costos reducidos y rango de cada c_j (coeficiente de z)",
                          "Mientras c_j esté dentro de su rango, el plan óptimo (los valores de las variables) "
                          "no cambia; solo cambia el valor de z.")
        tarjeta.pack(fill="x", pady=(0, 12))
        filas = [["Variable", "Nombre", "Valor óptimo", "Costo reducido\n(Cj − Zj)", "c_j actual",
                  "Disminución\npermitida", "Aumento\npermitido", "c_j mínimo", "c_j máximo", "Tipo"]]
        estilos = {}
        for k, rc in enumerate(s.rangos_costos, start=1):
            filas.append([rc.simbolo, rc.nombre, FORMATO.num(rc.valor_variable), FORMATO.num(rc.costo_reducido),
                          FORMATO.num(rc.valor_actual), FORMATO.cambio(rc.disminucion), FORMATO.cambio(rc.aumento),
                          FORMATO.limite_inferior(rc.minimo), FORMATO.limite_superior(rc.maximo),
                          "Básica" if rc.es_basica else "No básica"])
            for col, valor in ((5, rc.disminucion), (6, rc.aumento), (7, rc.minimo), (8, rc.maximo)):
                if valor is None:
                    estilos[(k, col)] = {"fg": COLORES["info"], "negrita": True}
        tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, alinear={1: "w"}, estilos=estilos)

        # 3) Matriz B^-1
        tarjeta = Tarjeta(contenedor, "Matriz B^-1 (columnas de las holguras en la tabla óptima)",
                          "y = Cb · B^-1 (precios sombra)   ·   x_B = B^-1 · b (valores de las básicas)")
        tarjeta.pack(fill="x", pady=(0, 12))
        filas = [["Básica", "Cb"] + [f"s{i + 1}" for i in range(p.m)] + ["x_B"]]
        for k in range(p.m):
            filas.append([s.simbolos_base[k], FORMATO.num(s.cb[k])] + [FORMATO.num(v) for v in s.binv[k]]
                         + [FORMATO.num(s.xb[k])])
        filas.append(["y = Cb·B^-1", ""] + [FORMATO.num(y) for y in s.precios_sombra] + [""])
        tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, columnas_encabezado=2,
                          estilos_fila={p.m + 1: {"bg": COLORES["primario_suave"], "negrita": True}})

        # 4) Interpretación y cálculos
        tarjeta = Tarjeta(contenedor, "Interpretación y detalle de los cálculos")
        tarjeta.pack(fill="x", pady=(0, 12))
        texto = TextoRico(tarjeta.cuerpo, alto=26)
        texto.pack(fill="both", expand=True)
        texto.mostrar(TSe.bloques_interpretacion(s, FORMATO) + [("\n", ())] + TSe.bloques_calculos(s, FORMATO))
