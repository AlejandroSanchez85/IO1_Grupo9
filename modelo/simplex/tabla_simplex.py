"""
modelo/simplex/tabla_simplex.py
===============================
Una TABLA SIMPLEX en el formato Cj – Zj:

    Base | Cb | x1 ... xn  s1 ... sm | b (solución)
    -----+----+----------------------+-------------
     ... | .. |   coeficientes aij   |    bi
    -----+----+----------------------+-------------
      Zj      |  Zj = Σ Cb_i · a_ij  |  z = Σ Cb_i · b_i
    Cj − Zj   |      Cj − Zj         |

Todos los valores son fracciones exactas (``Fraction``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction


@dataclass
class TablaSimplex:
    simbolos: list[str]                 # nombres de las columnas (x1..xn, s1..sm)
    cj: list[Fraction]                  # coeficiente de cada columna en z
    base: list[int]                     # índice de la columna básica de cada fila
    matriz: list[list[Fraction]]        # coeficientes de las restricciones
    b: list[Fraction]                   # lado derecho (valor de las variables básicas)
    cb: list[Fraction] = field(init=False)
    zj: list[Fraction] = field(init=False)
    cj_menos_zj: list[Fraction] = field(init=False)
    z: Fraction = field(init=False)

    def __post_init__(self):
        self.recalcular()

    # Cálculo de los renglones Zj y Cj − Zj y del valor de z
    def recalcular(self) -> None:
        self.cb = [self.cj[k] for k in self.base]
        columnas = len(self.cj)
        self.zj = [sum((self.cb[i] * self.matriz[i][j] for i in range(self.m)), Fraction(0))
                   for j in range(columnas)]
        self.cj_menos_zj = [self.cj[j] - self.zj[j] for j in range(columnas)]
        self.z = sum((self.cb[i] * self.b[i] for i in range(self.m)), Fraction(0))

    @property
    def m(self) -> int:
        return len(self.base)

    @property
    def columnas(self) -> int:
        return len(self.cj)

    def es_basica(self, j: int) -> bool:
        return j in self.base

    def fila_de(self, j: int) -> int | None:
        """Fila donde la columna j es básica (o None si es no básica)."""
        return self.base.index(j) if j in self.base else None

    def valor(self, j: int) -> Fraction:
        """Valor de la variable de la columna j en la solución básica actual."""
        fila = self.fila_de(j)
        return self.b[fila] if fila is not None else Fraction(0)

    def solucion(self) -> list[Fraction]:
        return [self.valor(j) for j in range(self.columnas)]

    def es_degenerada(self) -> bool:
        """Una solución básica es degenerada si alguna variable básica vale 0."""
        return any(valor == 0 for valor in self.b)

    def copia(self) -> "TablaSimplex":
        return TablaSimplex(list(self.simbolos), list(self.cj), list(self.base),
                            [list(fila) for fila in self.matriz], list(self.b))

    def pivotear(self, fila: int, columna: int) -> tuple["TablaSimplex", list[Fraction]]:
        """Operaciones de Gauss-Jordan sobre el elemento pivote.

        1) Fila pivote nueva = fila pivote / elemento pivote.
        2) Cada otra fila nueva = fila − (su coeficiente en la columna pivote) × fila pivote nueva.

        Devuelve la nueva tabla y los factores usados en cada fila (para mostrar
        las operaciones en el paso a paso).
        """
        pivote = self.matriz[fila][columna]
        if pivote == 0:
            raise ValueError("El elemento pivote no puede ser cero")
        nueva_matriz = [list(f) for f in self.matriz]
        nuevo_b = list(self.b)
        factores: list[Fraction] = [Fraction(0)] * self.m

        # Paso 1: dividir la fila pivote entre el elemento pivote
        nueva_matriz[fila] = [valor / pivote for valor in self.matriz[fila]]
        nuevo_b[fila] = self.b[fila] / pivote
        factores[fila] = pivote

        # Paso 2: hacer cero el resto de la columna pivote
        for i in range(self.m):
            if i == fila:
                continue
            factor = self.matriz[i][columna]
            factores[i] = factor
            if factor != 0:
                nueva_matriz[i] = [self.matriz[i][j] - factor * nueva_matriz[fila][j]
                                   for j in range(self.columnas)]
                nuevo_b[i] = self.b[i] - factor * nuevo_b[fila]

        nueva_base = list(self.base)
        nueva_base[fila] = columna
        return TablaSimplex(list(self.simbolos), list(self.cj), nueva_base, nueva_matriz, nuevo_b), factores
