"""
modelo/simplex/problema_pl.py
=============================
Clases que describen un problema de Programación Lineal (PL):

    Max (o Min) z = c1·x1 + c2·x2 + ... + cn·xn
    sujeto a        ai1·x1 + ... + ain·xn <= bi      (i = 1..m)
                    xj >= 0

Cada variable y cada restricción tiene NOMBRE y UNIDAD para que los
resultados se expliquen con el lenguaje del problema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction


@dataclass
class VariableDecision:
    simbolo: str            # x1, x2, ...
    nombre: str             # p. ej. "Mesas"
    unidad: str             # p. ej. "mesas/semana"
    coeficiente: Fraction   # cj: aporte a z por cada unidad de la variable

    @property
    def etiqueta(self) -> str:
        """Texto corto: 'x1 (Mesas)'."""
        return f"{self.simbolo} ({self.nombre})" if self.nombre != self.simbolo else self.simbolo


@dataclass
class Restriccion:
    simbolo: str                    # R1, R2, ...
    nombre: str                     # p. ej. "Horas de carpintería"
    unidad: str                     # p. ej. "horas/semana"
    coeficientes: list[Fraction]    # ai1 ... ain
    lado_derecho: Fraction          # bi (disponibilidad del recurso)
    signo: str = "<="               # este método trabaja con restricciones <=

    @property
    def etiqueta(self) -> str:
        return f"{self.simbolo} ({self.nombre})" if self.nombre != self.simbolo else self.simbolo


@dataclass
class ProblemaPL:
    nombre: str
    sentido: str                    # "max" o "min"
    unidad_z: str                   # p. ej. "COP/semana"
    descripcion_z: str              # p. ej. "Utilidad semanal"
    variables: list[VariableDecision]
    restricciones: list[Restriccion]
    descripcion: str = ""
    datos_originales: dict = field(default_factory=dict, repr=False)

    @property
    def n(self) -> int:
        """Número de variables de decisión."""
        return len(self.variables)

    @property
    def m(self) -> int:
        """Número de restricciones."""
        return len(self.restricciones)

    @property
    def es_max(self) -> bool:
        return self.sentido == "max"

    @property
    def c(self) -> list[Fraction]:
        return [v.coeficiente for v in self.variables]

    @property
    def A(self) -> list[list[Fraction]]:
        return [list(r.coeficientes) for r in self.restricciones]

    @property
    def b(self) -> list[Fraction]:
        return [r.lado_derecho for r in self.restricciones]

    def simbolos_columnas(self) -> list[str]:
        """Símbolos de todas las columnas de la tabla: x1..xn, s1..sm."""
        return [v.simbolo for v in self.variables] + [f"s{i + 1}" for i in range(self.m)]

    def nombres_columnas(self) -> list[str]:
        """Nombre descriptivo de cada columna (las holguras se asocian a su restricción)."""
        return ([v.nombre for v in self.variables]
                + [f"Holgura {r.nombre}" for r in self.restricciones])

    def unidades_columnas(self) -> list[str]:
        return [v.unidad for v in self.variables] + [r.unidad for r in self.restricciones]
