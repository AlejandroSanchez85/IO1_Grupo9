"""
vista/componentes/graficas.py
=============================
Gráficas dibujadas a mano en un Canvas de Tkinter (sin librerías externas):

* GraficoBarras: barras agrupadas (valores positivos y negativos).
* GraficoLineas: evolución de un valor (por ejemplo z en cada iteración).
* DiagramaRed: red de transporte (orígenes -> destinos con las cantidades).

Todas se vuelven a dibujar solas cuando cambia el tamaño de la ventana.
"""
from __future__ import annotations

import math
import tkinter as tk

from ..tema import COLORES, FUENTES, PALETA_GRAFICAS


def escala_bonita(minimo: float, maximo: float, divisiones: int = 5):
    """Devuelve (inicio, fin, paso) con números "redondos" para el eje."""
    if minimo == maximo:
        if minimo == 0:
            return 0.0, 1.0, 0.2
        minimo, maximo = (0.0, maximo) if maximo > 0 else (minimo, 0.0)
    rango = maximo - minimo
    paso_bruto = rango / divisiones
    exponente = math.floor(math.log10(paso_bruto))
    base = paso_bruto / 10 ** exponente
    for candidato in (1, 2, 2.5, 5, 10):
        if base <= candidato:
            paso = candidato * 10 ** exponente
            break
    inicio = math.floor(minimo / paso + 1e-9) * paso
    fin = math.ceil(maximo / paso - 1e-9) * paso
    return inicio, fin, paso


def texto_compacto(valor: float) -> str:
    """12500000 -> 12.5M ; 2500 -> 2.5k ; 0.25 -> 0.25"""
    absoluto = abs(valor)
    for limite, sufijo in ((1e9, "G"), (1e6, "M"), (1e3, "k")):
        if absoluto >= limite:
            return f"{valor / limite:.2f}".rstrip("0").rstrip(".") + sufijo
    if absoluto >= 100 or valor == int(valor):
        return f"{valor:.0f}"
    return f"{valor:.3f}".rstrip("0").rstrip(".")


def rectangulo_redondeado(canvas, x0, y0, x1, y1, r=10, **kwargs):
    puntos = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1, x1 - r, y1,
              x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return canvas.create_polygon(puntos, smooth=True, **kwargs)


class GraficoBase(tk.Canvas):
    def __init__(self, master, titulo: str = "", subtitulo: str = "", alto: int = 320, **kwargs):
        super().__init__(master, bg=COLORES["superficie"], height=alto, highlightthickness=0, bd=0,
                         **kwargs)
        self.titulo, self.subtitulo = titulo, subtitulo
        self._pendiente = None
        self.bind("<Configure>", self._programar)

    def _programar(self, _evento=None):
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(40, self._redibujar)

    def _redibujar(self):
        self._pendiente = None
        self.delete("all")
        ancho, alto = self.winfo_width(), self.winfo_height()
        if ancho < 80 or alto < 80:
            return
        arriba = 12
        if self.titulo:
            self.create_text(16, arriba, text=self.titulo, anchor="nw", font=FUENTES["h3"],
                             fill=COLORES["texto"])
            arriba += FUENTES["h3"].metrics("linespace") + 2
        if self.subtitulo:
            elemento = self.create_text(16, arriba, text=self.subtitulo, anchor="nw", font=FUENTES["pequena"],
                                        fill=COLORES["texto_suave"], width=ancho - 32)
            caja = self.bbox(elemento)                    # alto real (el texto puede ocupar varias líneas)
            arriba = (caja[3] if caja else arriba + FUENTES["pequena"].metrics("linespace")) + 4
        self.dibujar_contenido(ancho, alto, arriba + 8)

    def dibujar_contenido(self, ancho, alto, arriba):
        raise NotImplementedError


class GraficoBarras(GraficoBase):
    """Barras agrupadas. ``series`` = [(nombre, [valores...], color), ...]."""

    def __init__(self, master, titulo, categorias, series, etiqueta_y: str = "", subtitulo: str = "",
                 formato=None, alto: int = 330, **kwargs):
        self.categorias = list(categorias)
        self.series = [(nombre, [float(v) for v in valores], color) for nombre, valores, color in series]
        self.etiqueta_y = etiqueta_y
        self.formato = formato or texto_compacto
        super().__init__(master, titulo, subtitulo, alto, **kwargs)

    def dibujar_contenido(self, ancho, alto, arriba):
        c, fuente = COLORES, FUENTES["pequena"]
        valores = [v for _, vals, _ in self.series for v in vals]
        if not valores or not self.categorias:
            return
        inicio, fin, paso = escala_bonita(min(0.0, min(valores)), max(0.0, max(valores)))
        etiquetas = []
        marca = inicio
        while marca <= fin + paso / 1000:
            etiquetas.append(marca)
            marca += paso
        if len(self.series) > 1:
            x = ancho - 16
            for nombre, _, color in reversed(self.series):
                x -= fuente.measure(nombre)
                self.create_text(x, arriba + 2, text=nombre, anchor="nw", font=fuente, fill=c["texto_suave"])
                x -= 18
                self.create_rectangle(x, arriba + 3, x + 12, arriba + 15, fill=color, outline=color)
                x -= 14
            arriba += 24
        izquierda = 26 + max(fuente.measure(texto_compacto(e)) for e in etiquetas) + 12
        abajo = alto - 58
        derecha = ancho - 18
        if abajo - arriba < 40:
            return

        def y_de(valor):
            return abajo - (valor - inicio) / (fin - inicio) * (abajo - arriba)

        for e in etiquetas:
            y = y_de(e)
            self.create_line(izquierda, y, derecha, y, fill=c["borde"], dash=(2, 3) if e != 0 else None)
            self.create_text(izquierda - 6, y, text=texto_compacto(e), anchor="e", font=fuente,
                             fill=c["texto_suave"])
        y_cero = y_de(0.0)
        self.create_line(izquierda, y_cero, derecha, y_cero, fill=c["texto_tenue"], width=1)
        if self.etiqueta_y:
            self.create_text(12, (arriba + abajo) / 2, text=self.etiqueta_y, angle=90, font=fuente,
                             fill=c["texto_suave"])
        grupos = len(self.categorias)
        ancho_grupo = (derecha - izquierda) / grupos
        ancho_barra = min(56.0, ancho_grupo * 0.72 / len(self.series))
        for g, categoria in enumerate(self.categorias):
            x_grupo = izquierda + g * ancho_grupo + (ancho_grupo - ancho_barra * len(self.series)) / 2
            for s, (_, vals, color) in enumerate(self.series):
                valor = vals[g]
                x0 = x_grupo + s * ancho_barra
                y_valor = y_de(valor)
                self.create_rectangle(x0 + 2, min(y_valor, y_cero), x0 + ancho_barra - 2, max(y_valor, y_cero),
                                      fill=color, outline="")
                texto = self.formato(valor)
                y_texto = y_valor - 8 if valor >= 0 else y_valor + 8
                self.create_text(x0 + ancho_barra / 2, y_texto, text=texto, font=FUENTES["mini"],
                                 fill=c["texto"])
            self.create_text(izquierda + (g + 0.5) * ancho_grupo, abajo + 8, text=categoria, anchor="n",
                             font=fuente, fill=c["texto"], width=max(40, ancho_grupo - 6), justify="center")


class GraficoLineas(GraficoBase):
    """Línea con puntos: ``etiquetas_x`` y ``valores``."""

    def __init__(self, master, titulo, etiquetas_x, valores, etiqueta_y: str = "", subtitulo: str = "",
                 color: str | None = None, formato=None, alto: int = 300, resaltar_ultimo: bool = True,
                 **kwargs):
        self.etiquetas_x = list(etiquetas_x)
        self.valores = [float(v) for v in valores]
        self.etiqueta_y = etiqueta_y
        self.color = color or PALETA_GRAFICAS[0]
        self.formato = formato or texto_compacto
        self.resaltar_ultimo = resaltar_ultimo
        super().__init__(master, titulo, subtitulo, alto, **kwargs)

    def dibujar_contenido(self, ancho, alto, arriba):
        c, fuente = COLORES, FUENTES["pequena"]
        if not self.valores:
            return
        inicio, fin, paso = escala_bonita(min(self.valores + [0.0]), max(self.valores + [0.0]))
        etiquetas = []
        marca = inicio
        while marca <= fin + paso / 1000:
            etiquetas.append(marca)
            marca += paso
        izquierda = 26 + max(fuente.measure(texto_compacto(e)) for e in etiquetas) + 12
        abajo, derecha = alto - 42, ancho - 30
        if abajo - arriba < 40:
            return

        def y_de(valor):
            return abajo - (valor - inicio) / (fin - inicio) * (abajo - arriba - 10)

        for e in etiquetas:
            y = y_de(e)
            self.create_line(izquierda, y, derecha, y, fill=c["borde"], dash=(2, 3))
            self.create_text(izquierda - 6, y, text=texto_compacto(e), anchor="e", font=fuente,
                             fill=c["texto_suave"])
        if self.etiqueta_y:
            self.create_text(12, (arriba + abajo) / 2, text=self.etiqueta_y, angle=90, font=fuente,
                             fill=c["texto_suave"])
        cantidad = len(self.valores)
        separacion = (derecha - izquierda) / max(1, cantidad - 1) if cantidad > 1 else 0
        puntos = []
        for k, valor in enumerate(self.valores):
            x = izquierda + k * separacion if cantidad > 1 else (izquierda + derecha) / 2
            puntos.append((x, y_de(valor)))
        if len(puntos) > 1:
            area = [puntos[0][0], abajo] + [v for p in puntos for v in p] + [puntos[-1][0], abajo]
            self.create_polygon(area, fill=c["primario_suave"], outline="")
            self.create_line(*[v for p in puntos for v in p], fill=self.color, width=3, smooth=False)
        for k, (x, y) in enumerate(puntos):
            ultimo = self.resaltar_ultimo and k == len(puntos) - 1
            radio = 6 if ultimo else 4
            color = COLORES["elegida"] if ultimo else self.color
            self.create_oval(x - radio, y - radio, x + radio, y + radio, fill=color, outline="#FFFFFF", width=2)
            self.create_text(x, y - 14, text=self.formato(self.valores[k]), font=FUENTES["mini"],
                             fill=c["texto"])
            self.create_text(x, abajo + 10, text=self.etiquetas_x[k], anchor="n", font=fuente,
                             fill=c["texto_suave"])


class DiagramaRed(GraficoBase):
    """Red de transporte: orígenes a la izquierda, destinos a la derecha.

    ``envios`` = [(i, j, cantidad (float), texto de la flecha), ...]
    """

    def __init__(self, master, titulo, origenes, destinos, textos_origen, textos_destino, envios,
                 fila_ficticia=None, columna_ficticia=None, subtitulo: str = "", alto: int = 460, **kwargs):
        self.origenes, self.destinos = list(origenes), list(destinos)
        self.textos_origen, self.textos_destino = list(textos_origen), list(textos_destino)
        self.envios = list(envios)
        self.fila_ficticia, self.columna_ficticia = fila_ficticia, columna_ficticia
        super().__init__(master, titulo, subtitulo, alto, **kwargs)

    def dibujar_contenido(self, ancho, alto, arriba):
        c = COLORES
        f_nombre, f_peq = FUENTES["base_negrita"], FUENTES["pequena"]
        m, n = len(self.origenes), len(self.destinos)
        ancho_nodo = min(220, max([f_nombre.measure(t) for t in self.origenes + self.destinos]
                                  + [f_peq.measure(t) for t in self.textos_origen + self.textos_destino]) + 28)
        alto_nodo = 46
        abajo = alto - 16

        def posiciones(cantidad):
            espacio = (abajo - arriba) / max(cantidad, 1)
            return [arriba + espacio * (k + 0.5) for k in range(cantidad)]

        ys_o, ys_d = posiciones(m), posiciones(n)
        x_o, x_d = 20, ancho - 20 - ancho_nodo
        maximo = max([e[2] for e in self.envios] + [1.0])
        colocadas, etiquetas = [], []
        for k, (i, j, cantidad, texto) in enumerate(self.envios):
            ficticio = i == self.fila_ficticia or j == self.columna_ficticia
            color = c["texto_tenue"] if ficticio else PALETA_GRAFICAS[i % len(PALETA_GRAFICAS)]
            grosor = 1.5 + 7.5 * (cantidad / maximo)
            x0, y0 = x_o + ancho_nodo, ys_o[i]
            x1, y1 = x_d, ys_d[j]
            self.create_line(x0, y0, x1, y1, fill=color, width=grosor, arrow="last",
                             arrowshape=(12, 14, 5), dash=(6, 4) if ficticio else None)
            # Se busca un punto de la flecha donde la etiqueta no tape a otra
            ancho_texto = f_peq.measure(texto) + 12
            mejor = None
            for t in (0.5, 0.36, 0.64, 0.26, 0.74, 0.43, 0.57, 0.2, 0.8):
                tx, ty = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                caja = (tx - ancho_texto / 2 - 3, ty - 12, tx + ancho_texto / 2 + 3, ty + 12)
                choques = sum(1 for o in colocadas
                              if not (caja[2] < o[0] or caja[0] > o[2] or caja[3] < o[1] or caja[1] > o[3]))
                if mejor is None or choques < mejor[0]:
                    mejor = (choques, tx, ty, caja)
                if choques == 0:
                    break
            colocadas.append(mejor[3])
            etiquetas.append((mejor[1], mejor[2], ancho_texto, texto, color))
        for tx, ty, ancho_texto, texto, color in etiquetas:
            rectangulo_redondeado(self, tx - ancho_texto / 2, ty - 10, tx + ancho_texto / 2, ty + 10, r=8,
                                  fill="#FFFFFF", outline=color)
            self.create_text(tx, ty, text=texto, font=f_peq, fill=c["texto"])
        for nodos, ys, x, textos, ficticio, color_base in (
                (self.origenes, ys_o, x_o, self.textos_origen, self.fila_ficticia, c["primario"]),
                (self.destinos, ys_d, x_d, self.textos_destino, self.columna_ficticia, c["secundario"])):
            for k, nombre in enumerate(nodos):
                es_ficticio = k == ficticio
                y = ys[k]
                rectangulo_redondeado(self, x, y - alto_nodo / 2, x + ancho_nodo, y + alto_nodo / 2, r=12,
                                      fill=c["superficie_alt"] if es_ficticio else c["superficie"],
                                      outline=c["texto_tenue"] if es_ficticio else color_base, width=2,
                                      dash=(4, 3) if es_ficticio else None)
                self.create_text(x + ancho_nodo / 2, y - 8, text=nombre, font=f_nombre,
                                 fill=c["texto_suave"] if es_ficticio else c["texto"], width=ancho_nodo - 10)
                self.create_text(x + ancho_nodo / 2, y + 11, text=textos[k], font=f_peq, fill=c["texto_suave"])
