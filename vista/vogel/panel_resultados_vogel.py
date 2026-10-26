"""
vista/vogel/panel_resultados_vogel.py
=====================================
* PanelPlanteamientoVogel: modelo, balanceo y tabla de costos (paso 0).
* PanelSolucionVogel: avisos, tabla final, envíos con nombres y unidades y
  costo total.
* PanelModi: prueba de optimalidad MODI paso a paso y comparación del costo
  de Vogel con el costo óptimo.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..componentes import (Aviso, FilaFlexible, Leyenda, MarcoDesplazable, TablaCanvas, TablaTransporteCanvas,
                           Tarjeta, TextoRico, etiqueta, mostrar_avisos, tabla_desplazable, tarjeta_dato)
from ..explicaciones import textos_transporte as TT
from ..formato import FORMATO
from ..tema import COLORES


class PanelPlanteamientoVogel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.area = MarcoDesplazable(self, horizontal=False)
        self.area.pack(fill="both", expand=True)
        tk.Label(self.area.interior, text="Resuelva un problema para ver el planteamiento.", bg=COLORES["fondo"],
                 fg=COLORES["texto_suave"]).pack(pady=40)

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.mostrar(self.resultado)

    def mostrar(self, resultado) -> None:
        self.resultado = resultado
        self.area.limpiar()
        contenedor = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=18, pady=14)
        p = resultado.problema
        tarjeta = Tarjeta(contenedor, f"Tabla de costos unitarios ({p.unidad_costo} por {p.unidad_producto})",
                          "Ya incluye el origen o destino ficticio si el problema estaba desbalanceado.")
        tarjeta.pack(fill="x", pady=(0, 12))
        datos = TT.datos_tabla_final(resultado, FORMATO)
        datos["asignaciones"] = {}
        tabla_desplazable(tarjeta.cuerpo, TablaTransporteCanvas, **datos)
        tarjeta = Tarjeta(contenedor, "Modelo y balanceo")
        tarjeta.pack(fill="x", pady=(0, 12))
        texto = TextoRico(tarjeta.cuerpo, alto=24)
        texto.pack(fill="x")
        texto.mostrar(TT.bloques_planteamiento(resultado, FORMATO))


class PanelSolucionVogel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.modi = None
        self.area = MarcoDesplazable(self, horizontal=False)
        self.area.pack(fill="both", expand=True)
        tk.Label(self.area.interior, text="Resuelva un problema para ver la solución.", bg=COLORES["fondo"],
                 fg=COLORES["texto_suave"]).pack(pady=40)

    def refrescar(self) -> None:
        if self.resultado is not None:
            self.mostrar(self.resultado, self.modi)

    def mostrar(self, resultado, modi=None) -> None:
        self.resultado, self.modi = resultado, modi
        self.area.limpiar()
        r, p = resultado, resultado.problema
        u = p.unidad_producto
        contenedor = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=18, pady=14)
        Aviso(contenedor, "exito", "Solución inicial obtenida con el método de Vogel",
              f"Costo total de transporte = {FORMATO.num(r.costo_total)} {p.unidad_costo}, con "
              f"{sum(1 for x in r.asignaciones.values() if x > 0)} rutas usadas.").pack(fill="x", pady=(0, 8))
        mostrar_avisos(contenedor, r.casos)

        fila = FilaFlexible(contenedor)
        fila.pack(fill="x", pady=(4, 2))
        enviado = sum((x for (i, j), x in r.asignaciones.items() if not r.es_fila_ficticia(i)
                       and not r.es_columna_ficticia(j)), 0)
        datos = [("Costo Vogel", FORMATO.num(r.costo_total), "exito",
                  f"{p.unidad_costo} · solución inicial (no siempre óptima)"),
                 ("Pasos de Vogel", str(len(r.pasos)), "primario", f"{r.m} × {r.n} → m + n − 1 = {r.m + r.n - 1} básicas"),
                 ("Unidades enviadas", FORMATO.num(enviado), "secundario",
                  f"{u} · sin contar orígenes/destinos ficticios"),
                 ("Degeneración", "Sí" if r.es_degenerada else "No", "advertencia" if r.es_degenerada else "exito",
                  f"{len(r.celdas_cero)} básica(s) en 0")]
        if modi is not None and modi.rutas_prohibidas_usadas:
            datos.append(("Óptimo (MODI)", "Infactible", "error", "Incluso el óptimo usa rutas prohibidas (M)"))
        elif modi is not None:
            datos.append(("Óptimo (MODI)", FORMATO.num(modi.costo_optimo),
                          "exito" if modi.vogel_es_optimo else "advertencia",
                          f"{p.unidad_costo} · " + ("Vogel ya era óptimo" if modi.vogel_es_optimo else
                                                    f"ahorro posible: {FORMATO.num(modi.ahorro)}")))
        for titulo, valor, color, detalle in datos:
            fila.agregar(tarjeta_dato(fila, titulo, valor, color, detalle))

        tarjeta = Tarjeta(contenedor, "Tabla final de Vogel",
                          "En el centro de cada celda está la cantidad asignada; en la esquina, el costo unitario.")
        tarjeta.pack(fill="x", pady=(0, 12))
        tabla_desplazable(tarjeta.cuerpo, TablaTransporteCanvas, **TT.datos_tabla_final(r, FORMATO))

        tarjeta = Tarjeta(contenedor, "Plan de envíos (resultado con nombres y unidades)")
        tarjeta.pack(fill="x", pady=(0, 12))
        filas = [["Origen", "Destino", f"Cantidad ({u})", f"Costo unitario ({p.unidad_costo}/{u})",
                  f"Costo de la ruta ({p.unidad_costo})", "Observación"]]
        estilos = {}
        for k, (i, j, x, costo) in enumerate(r.envios(), start=1):
            nota = ""
            if r.es_fila_ficticia(i):
                nota = "Demanda insatisfecha"
            elif r.es_columna_ficticia(j):
                nota = "Queda en inventario"
            elif r.costos[i][j].tiene_m:
                nota = "RUTA PROHIBIDA"
                estilos[(k, 5)] = {"bg": COLORES["error_suave"], "fg": COLORES["error"], "negrita": True}
            filas.append([r.origenes[i], r.destinos[j], FORMATO.num(x), FORMATO.num(r.costos[i][j]), FORMATO.num(costo),
                          nota])
        for (i, j) in r.celdas_cero:
            filas.append([r.origenes[i], r.destinos[j], "0", FORMATO.num(r.costos[i][j]), "0", "Básica en 0 (degeneración)"])
            estilos[(len(filas) - 1, 5)] = {"fg": COLORES["advertencia"], "negrita": True}
        filas.append(["TOTAL", "", FORMATO.num(sum((x for (_, _, x, _) in r.envios()), 0)), "",
                      FORMATO.num(r.costo_total), ""])
        estilos[(len(filas) - 1, 4)] = {"bg": COLORES["exito"], "fg": "#FFFFFF", "negrita": True}
        tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, alinear={0: "w", 1: "w", 5: "w"}, estilos=estilos)

        tarjeta = Tarjeta(contenedor, "Cálculo del costo total")
        tarjeta.pack(fill="x", pady=(0, 12))
        texto = TextoRico(tarjeta.cuerpo, alto=12, fondo=COLORES["superficie_alt"])
        texto.pack(fill="x")
        texto.mostrar(TT.bloques_resultado(r, FORMATO))


class PanelModi(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORES["fondo"])
        self.resultado = None
        self.modi = None
        self.indice = 0
        barra = tk.Frame(self, bg=COLORES["superficie"], highlightbackground=COLORES["borde"], highlightthickness=1)
        barra.pack(fill="x")
        caja = tk.Frame(barra, bg=COLORES["superficie"])
        caja.pack(fill="x", padx=12, pady=8)
        etiqueta(caja, "Prueba de optimalidad MODI (u-v)", "h3").pack(side="left")
        self.boton_anterior = ttk.Button(caja, text="◄ Anterior", style="Chico.TButton",
                                         command=lambda: self.ir(self.indice - 1))
        self.boton_anterior.pack(side="left", padx=(16, 4))
        self.selector = ttk.Combobox(caja, state="readonly", width=40)
        self.selector.pack(side="left", padx=4)
        self.selector.bind("<<ComboboxSelected>>", lambda e: self.ir(self.selector.current()))
        self.boton_siguiente = ttk.Button(caja, text="Siguiente ►", style="Chico.TButton",
                                          command=lambda: self.ir(self.indice + 1))
        self.boton_siguiente.pack(side="left", padx=4)
        self.etiqueta_estado = etiqueta(caja, "", "base_negrita", "primario")
        self.etiqueta_estado.pack(side="right")
        Leyenda(barra, [(COLORES["asignada"], "Celda básica (asignación)"),
                        (COLORES["info_suave"], "u_i y v_j"), (COLORES["ciclo"], "Ciclo + / −"),
                        (COLORES["error"], "d_ij negativo (mejora)"),
                        (COLORES["alternativo_texto"], "d_ij = 0 (óptimo alternativo)")]).pack(fill="x", padx=14,
                                                                                            pady=(0, 8))
        self.area = MarcoDesplazable(self, horizontal=False)
        self.area.pack(fill="both", expand=True)
        tk.Label(self.area.interior, text="Resuelva un problema para ver la prueba de optimalidad.",
                 bg=COLORES["fondo"], fg=COLORES["texto_suave"]).pack(pady=40)

    def refrescar(self) -> None:
        if self.modi is not None:
            self.ir(self.indice)

    def mostrar(self, resultado, modi) -> None:
        self.resultado, self.modi = resultado, modi
        nombres = []
        for it in modi.iteraciones:
            estado = "ÓPTIMA" if it.es_optima else "no óptima"
            nombres.append(f"Iteración {it.numero} — costo {FORMATO.num(it.costo)} — {estado}")
        self.selector.configure(values=nombres)
        self.ir(0)

    def ir(self, indice: int) -> None:
        if self.modi is None:
            return
        r, modi = self.resultado, self.modi
        p = r.problema
        indice = max(0, min(indice, len(modi.iteraciones) - 1))
        self.indice = indice
        self.selector.current(indice)
        self.boton_anterior.configure(state="normal" if indice > 0 else "disabled")
        self.boton_siguiente.configure(state="normal" if indice < len(modi.iteraciones) - 1 else "disabled")
        self.etiqueta_estado.configure(text=f"Iteración {indice + 1} de {len(modi.iteraciones)}")
        self.area.limpiar()
        contenedor = tk.Frame(self.area.interior, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=18, pady=14)

        # Comparación Vogel vs óptimo
        tarjeta = Tarjeta(contenedor, "Comparación: costo de Vogel vs. costo óptimo",
                          "Vogel solo da una solución inicial. MODI comprueba si es óptima "
)
        tarjeta.pack(fill="x", pady=(0, 12))
        fila = FilaFlexible(tarjeta.cuerpo)
        fila.pack(fill="x")
        diferencia = modi.ahorro
        porcentaje = ""
        if not modi.costo_optimo.tiene_m and not diferencia.tiene_m and modi.costo_optimo.c != 0:
            porcentaje = f"{float(diferencia.c / modi.costo_optimo.c) * 100:.2f} % sobre el óptimo"
        for titulo, valor, color, detalle in [
                (f"Costo Vogel ({p.unidad_costo})", FORMATO.num(modi.costo_inicial), "primario", "Solución inicial"),
                (f"Costo óptimo ({p.unidad_costo})", FORMATO.num(modi.costo_optimo), "exito",
                 f"{len(modi.iteraciones) - 1} mejora(s) con MODI"),
                (f"Diferencia ({p.unidad_costo})", FORMATO.num(diferencia),
                 "error" if modi.rutas_prohibidas_usadas else ("exito" if modi.vogel_es_optimo else "advertencia"),
                 "Problema INFACTIBLE (usa rutas M)" if modi.rutas_prohibidas_usadas else
                 ("Vogel ya era óptimo" if modi.vogel_es_optimo else porcentaje))]:
            fila.agregar(tarjeta_dato(fila, titulo, valor, color, detalle))
        caja = tk.Frame(tarjeta.cuerpo, bg=COLORES["superficie"])
        caja.pack(fill="x", pady=(10, 0))
        mostrar_avisos(caja, modi.casos)

        tarjeta = Tarjeta(contenedor, f"Tabla de la iteración {modi.iteraciones[indice].numero}",
                          "Celdas básicas con su asignación; en las no básicas se muestra d_ij = c_ij − u_i − v_j.")
        tarjeta.pack(fill="x", pady=(0, 12))
        tabla_desplazable(tarjeta.cuerpo, TablaTransporteCanvas, **TT.datos_tabla_modi(r, modi, indice, FORMATO))
        tarjeta = Tarjeta(contenedor, "Explicación de la iteración")
        tarjeta.pack(fill="x", pady=(0, 12))
        texto = TextoRico(tarjeta.cuerpo, alto=22)
        texto.pack(fill="x")
        texto.mostrar(TT.bloques_modi(r, modi, indice, FORMATO))

        if indice == len(modi.iteraciones) - 1:
            tarjeta = Tarjeta(contenedor, "Distribución óptima (MODI)")
            tarjeta.pack(fill="x", pady=(0, 12))
            u = p.unidad_producto
            filas = [["Origen", "Destino", f"Cantidad ({u})", f"Costo ({p.unidad_costo})"]]
            for (i, j), x in sorted(modi.asignaciones.items()):
                if x > 0:
                    filas.append([r.origenes[i], r.destinos[j], FORMATO.num(x), FORMATO.num(r.costos[i][j] * x)])
            filas.append(["TOTAL", "", "", FORMATO.num(modi.costo_optimo)])
            tabla_desplazable(tarjeta.cuerpo, TablaCanvas, filas, alinear={0: "w", 1: "w"},
                              estilos={(len(filas) - 1, 3): {"bg": COLORES["exito"], "fg": "#FFFFFF", "negrita": True}})
