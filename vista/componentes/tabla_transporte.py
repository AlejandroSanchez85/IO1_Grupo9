"""
vista/componentes/tabla_transporte.py
=====================================
Tabla de transporte dibujada como en los libros: el costo unitario va en
una cajita en la esquina de cada celda y la asignación en el centro.
Sirve para Vogel (penalizaciones, líneas tachadas, celda escogida) y para
MODI (u_i, v_j, costos reducidos y el ciclo + − + −).
"""
from __future__ import annotations

import tkinter as tk

from ..tema import COLORES, FUENTES


class TablaTransporteCanvas(tk.Canvas):
    def __init__(self, master, origenes, destinos, costos, asignaciones=None, oferta=None, demanda=None,
                 titulo_oferta="Oferta", titulo_demanda="Demanda", penal_filas=None, penal_columnas=None,
                 titulo_penal="Penalización", penal_resaltada=None, filas_tachadas=(),
                 columnas_tachadas=(), tachada_ahora=None, linea_resaltada=None, celda_elegida=None,
                 fila_ficticia=None, columna_ficticia=None, u=None, v=None, reducidos=None,
                 reducidos_negativos=(), reducidos_cero=(), ciclo=None, prohibidas=(), total=None,
                 esquina="Origen \\ Destino", fondo=None, **kwargs):
        super().__init__(master, bg=fondo or COLORES["superficie"], highlightthickness=0, bd=0, **kwargs)
        self.origenes, self.destinos, self.costos = list(origenes), list(destinos), costos
        self.asignaciones = asignaciones or {}
        self.oferta, self.demanda = oferta, demanda
        self.titulo_oferta, self.titulo_demanda = titulo_oferta, titulo_demanda
        self.penal_filas, self.penal_columnas = penal_filas, penal_columnas
        self.titulo_penal, self.penal_resaltada = titulo_penal, penal_resaltada
        self.filas_tachadas, self.columnas_tachadas = set(filas_tachadas), set(columnas_tachadas)
        self.tachada_ahora, self.linea_resaltada = tachada_ahora, linea_resaltada
        self.celda_elegida = celda_elegida
        self.fila_ficticia, self.columna_ficticia = fila_ficticia, columna_ficticia
        self.u, self.v = u, v
        self.reducidos = reducidos or {}
        self.reducidos_negativos, self.reducidos_cero = set(reducidos_negativos), set(reducidos_cero)
        self.ciclo = ciclo or []
        self.prohibidas = set(prohibidas)
        self.total, self.esquina = total, esquina
        self.dibujar()

    # ---------------------------------------------------------------- medidas
    def _medidas(self):
        f_nombre, f_peq = FUENTES["tabla_negrita"], FUENTES["tabla_pequena"]
        f_asig = FUENTES["asignacion"]
        m, n = len(self.origenes), len(self.destinos)
        ancho_rotulo = max([f_nombre.measure(t) for t in self.origenes + [self.titulo_demanda,
                                                                          self.titulo_penal, "v_j"]]
                           + [f_nombre.measure(self.esquina)]) + 24
        anchos = []
        for j in range(n):
            ancho = f_nombre.measure(self.destinos[j]) + 20
            for i in range(m):
                costo = self.costos[i][j]
                ancho = max(ancho, f_peq.measure(costo) + 12 + f_asig.measure(
                    self.asignaciones.get((i, j), "")) + 34, f_peq.measure(self.reducidos.get((i, j), "")) + 40)
            anchos.append(max(ancho, 86))
        extra = []
        textos_oferta = [self.titulo_oferta] + list(self.oferta or []) + [self.total or ""]
        extra.append(max(f_nombre.measure(t) for t in textos_oferta) + 24)
        if self.penal_filas is not None:
            extra.append(max([f_nombre.measure(self.titulo_penal)]
                             + [f_nombre.measure(t) for t in self.penal_filas.values()]) + 24)
        if self.u is not None:
            extra.append(max([f_nombre.measure("u_i")] + [f_nombre.measure(t) for t in self.u]) + 28)
        alto_caja = f_peq.metrics("linespace") + 4
        alto_celda = alto_caja + f_asig.metrics("linespace") + 14
        alto_encabezado = f_nombre.metrics("linespace") + 16
        return ancho_rotulo, anchos, extra, alto_celda, alto_encabezado, alto_caja

    # ----------------------------------------------------------------- dibujo
    def dibujar(self) -> None:
        self.delete("all")
        c = COLORES
        f_nombre, f_peq = FUENTES["tabla_negrita"], FUENTES["tabla_pequena"]
        m, n = len(self.origenes), len(self.destinos)
        ancho_rotulo, anchos, extra, alto_celda, alto_enc, alto_caja = self._medidas()
        xs = [ancho_rotulo]
        for a in anchos:
            xs.append(xs[-1] + a)
        x_extra = [xs[-1]]
        for a in extra:
            x_extra.append(x_extra[-1] + a)
        ancho_total = x_extra[-1]
        ys = [alto_enc]
        for _ in range(m):
            ys.append(ys[-1] + alto_celda)
        filas_extra = 1 + (1 if self.penal_columnas is not None else 0) + (1 if self.v is not None else 0)
        alto_total = ys[-1] + filas_extra * alto_enc
        enc_bg, enc_fg, rejilla = c["tabla_encabezado"], c["tabla_encabezado_texto"], c["tabla_rejilla"]

        def caja(x0, y0, x1, y1, fondo, texto="", fuente=f_nombre, color=c["texto"], ancla="center"):
            self.create_rectangle(x0, y0, x1, y1, fill=fondo, outline=rejilla)
            if texto:
                tx = x0 + 10 if ancla == "w" else (x0 + x1) / 2
                self.create_text(tx, (y0 + y1) / 2, text=texto, font=fuente, fill=color, anchor=ancla,
                                 tags=("texto",))

        # Encabezado
        caja(0, 0, ancho_rotulo, alto_enc, enc_bg, self.esquina, f_peq, enc_fg)
        for j in range(n):
            fondo = c["primario_texto"] if self.linea_resaltada == ("columna", j) else enc_bg
            caja(xs[j], 0, xs[j + 1], alto_enc, fondo, self.destinos[j], f_nombre, enc_fg)
        titulos_extra = [self.titulo_oferta]
        if self.penal_filas is not None:
            titulos_extra.append(self.titulo_penal)
        if self.u is not None:
            titulos_extra.append("u_i")
        for k, titulo in enumerate(titulos_extra):
            caja(x_extra[k], 0, x_extra[k + 1], alto_enc, enc_bg, titulo, f_nombre, enc_fg)

        # Filas de orígenes
        for i in range(m):
            y0, y1 = ys[i], ys[i + 1]
            tachada = i in self.filas_tachadas
            if self.linea_resaltada == ("fila", i):
                fondo_rotulo = c["linea_elegida"]
            elif i == self.fila_ficticia:
                fondo_rotulo = c["ficticio"]
            else:
                fondo_rotulo = c["tabla_lateral"]
            caja(0, y0, ancho_rotulo, y1, fondo_rotulo, self.origenes[i], f_nombre,
                 c["tachado_texto"] if tachada else c["texto"], "w")
            for j in range(n):
                self._dibujar_celda(i, j, xs[j], y0, xs[j + 1], y1, alto_caja)
            # Columna de oferta / penalización / u
            k = 0
            texto_oferta = self.oferta[i] if self.oferta else ""
            caja(x_extra[k], y0, x_extra[k + 1], y1, c["tachado"] if tachada else c["tabla_lateral"],
                 texto_oferta, f_nombre, c["tachado_texto"] if tachada else c["texto"])
            k += 1
            if self.penal_filas is not None:
                texto = self.penal_filas.get(i, "")
                resaltada = self.penal_resaltada == ("fila", i)
                caja(x_extra[k], y0, x_extra[k + 1], y1, c["primario"] if resaltada else c["primario_suave"],
                     texto, f_nombre, "#FFFFFF" if resaltada else c["primario_texto"])
                k += 1
            if self.u is not None:
                caja(x_extra[k], y0, x_extra[k + 1], y1, c["info_suave"], self.u[i], f_nombre, c["info"])

        # Fila de demanda
        y0, y1 = ys[-1], ys[-1] + alto_enc
        caja(0, y0, ancho_rotulo, y1, c["tabla_sub"], self.titulo_demanda, f_nombre, c["texto"], "w")
        for j in range(n):
            tachada = j in self.columnas_tachadas
            texto = self.demanda[j] if self.demanda else ""
            caja(xs[j], y0, xs[j + 1], y1, c["tachado"] if tachada else c["tabla_lateral"], texto,
                 f_nombre, c["tachado_texto"] if tachada else c["texto"])
        caja(x_extra[0], y0, x_extra[1], y1, c["tabla_sub"], self.total or "", f_nombre, c["texto"])
        for k in range(1, len(extra)):
            caja(x_extra[k], y0, x_extra[k + 1], y1, c["superficie"])
        fila_actual = y1

        # Fila de penalizaciones de columna
        if self.penal_columnas is not None:
            y0, y1 = fila_actual, fila_actual + alto_enc
            caja(0, y0, ancho_rotulo, y1, c["primario_suave"], self.titulo_penal, f_nombre,
                 c["primario_texto"], "w")
            for j in range(n):
                texto = self.penal_columnas.get(j, "")
                resaltada = self.penal_resaltada == ("columna", j)
                caja(xs[j], y0, xs[j + 1], y1, c["primario"] if resaltada else c["primario_suave"], texto,
                     f_nombre, "#FFFFFF" if resaltada else c["primario_texto"])
            for k in range(len(extra)):
                caja(x_extra[k], y0, x_extra[k + 1], y1, c["superficie"])
            fila_actual = y1

        # Fila de v_j (MODI)
        if self.v is not None:
            y0, y1 = fila_actual, fila_actual + alto_enc
            caja(0, y0, ancho_rotulo, y1, c["info_suave"], "v_j", f_nombre, c["info"], "w")
            for j in range(n):
                caja(xs[j], y0, xs[j + 1], y1, c["info_suave"], self.v[j], f_nombre, c["info"])
            for k in range(len(extra)):
                caja(x_extra[k], y0, x_extra[k + 1], y1, c["superficie"])

        # Ciclo de MODI (línea que une las celdas del ciclo)
        if self.ciclo:
            puntos = []
            for (i, j) in self.ciclo + [self.ciclo[0]]:
                puntos += [(xs[j] + xs[j + 1]) / 2, (ys[i] + ys[i + 1]) / 2]
            self.create_line(*puntos, fill=c["ciclo"], width=3, dash=(8, 4))
            for posicion, (i, j) in enumerate(self.ciclo):
                cx, cy = xs[j] + 13, ys[i] + 13
                color = c["ciclo_mas"] if posicion % 2 == 0 else c["ciclo_menos"]
                self.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill=color, outline="#FFFFFF", width=2,
                                 tags=("signo",))
                self.create_text(cx, cy, text="+" if posicion % 2 == 0 else "−", fill="#FFFFFF",
                                 font=FUENTES["tabla_negrita"], tags=("signo",))

        # Línea tachada en este paso (raya roja)
        if self.tachada_ahora is not None:
            tipo, k = self.tachada_ahora
            if tipo == "fila" and k < m:
                yc = (ys[k] + ys[k + 1]) / 2
                self.create_line(6, yc, x_extra[1] - 6, yc, fill=c["ciclo_menos"], width=3)
            elif tipo == "columna" and k < n:
                xc = (xs[k] + xs[k + 1]) / 2
                self.create_line(xc, 6, xc, ys[-1] + alto_enc - 6, fill=c["ciclo_menos"], width=3)

        self.tag_raise("texto")                 # los números quedan encima de las rayas y del ciclo
        self.tag_raise("signo")
        self.configure(width=ancho_total + 1, height=alto_total + 1)

    def _dibujar_celda(self, i, j, x0, y0, x1, y1, alto_caja):
        c = COLORES
        tachada = i in self.filas_tachadas or j in self.columnas_tachadas
        asignacion = self.asignaciones.get((i, j))
        elegida = self.celda_elegida == (i, j)
        if elegida:
            fondo = c["elegida"]
        elif tachada:
            fondo = c["tachado"]
        elif asignacion not in (None, ""):
            fondo = c["asignada"]
        elif self.linea_resaltada in (("fila", i), ("columna", j)):
            fondo = c["linea_elegida"]
        elif (i, j) in self.prohibidas:
            fondo = c["prohibida"]
        elif i == self.fila_ficticia or j == self.columna_ficticia:
            fondo = c["ficticio"]
        else:
            fondo = c["superficie"]
        self.create_rectangle(x0, y0, x1, y1, fill=fondo, outline=c["tabla_rejilla"])
        # Cajita del costo (esquina superior derecha)
        costo = self.costos[i][j]
        f_peq = FUENTES["tabla_pequena"]
        ancho_caja = f_peq.measure(costo) + 12
        self.create_rectangle(x1 - ancho_caja, y0, x1, y0 + alto_caja,
                              fill=c["costo_caja"] if not elegida else "#BBF7D0", outline=c["tabla_rejilla"])
        self.create_text(x1 - ancho_caja / 2, y0 + alto_caja / 2, text=costo, font=f_peq,
                         fill=c["error"] if (i, j) in self.prohibidas else c["texto_suave"], tags=("texto",))
        centro_y = (y0 + alto_caja + y1) / 2
        if asignacion not in (None, ""):
            self.create_text((x0 + x1) / 2, centro_y, text=asignacion, font=FUENTES["asignacion"],
                             fill="#FFFFFF" if elegida else (c["tachado_texto"] if tachada and not elegida
                                                             else c["texto"]), tags=("texto",))
        elif (i, j) in self.reducidos:
            if (i, j) in self.reducidos_negativos:
                color = c["error"]
            elif (i, j) in self.reducidos_cero:
                color = c["alternativo_texto"]
            else:
                color = c["texto_tenue"]
            self.create_text((x0 + x1) / 2, centro_y, text=self.reducidos[(i, j)], font=FUENTES["pequena_negrita"],
                             fill=color, tags=("texto",))
