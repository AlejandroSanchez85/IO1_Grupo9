"""
modelo/numeros.py
=================
Utilidades numéricas del MODELO (no dependen de la interfaz gráfica).

* ``convertir_numero(texto)``: convierte lo que escribe el usuario en un
  número EXACTO (``fractions.Fraction``). Acepta enteros, decimales con
  punto o con coma, fracciones (``3/4``) y notación científica (``1e3``).
* ``ValorM``: número de la forma ``a·M + b`` donde M es un número "muy
  grande". Se usa en transporte para las rutas prohibidas (costo M).
* ``texto_numero(x)``: texto corto de un número para mensajes del modelo.

Se trabaja con fracciones exactas (librería estándar de Python, NO es un
solver) para que los empates, la degeneración y los óptimos alternativos
se detecten sin errores de redondeo (por ejemplo 0.1 + 0.2 = 3/10 exacto).
"""
from __future__ import annotations

import math
import re
from fractions import Fraction
from functools import total_ordering

# Número decimal simple: 12 | -3.5 | .5 | 5. | 1e3 | 2.5E-2
_PATRON_DECIMAL = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


def _decimal(texto: str) -> Fraction:
    """Convierte un texto decimal (ya normalizado con punto) en Fraction."""
    if not _PATRON_DECIMAL.match(texto):
        raise ValueError("no es un número válido")
    return Fraction(texto)


def convertir_numero(valor) -> Fraction:
    """Convierte ``valor`` (texto o número) en una fracción exacta.

    Lanza ``ValueError`` con un motivo claro (en español) si no es posible.
    """
    if isinstance(valor, bool):                      # True/False no son datos válidos
        raise ValueError("no es un número válido")
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor)
    if isinstance(valor, float):
        if math.isnan(valor) or math.isinf(valor):
            raise ValueError("no es un número finito")
        return Fraction(repr(valor))                 # repr evita basura binaria: 0.1 -> 1/10
    if valor is None:
        raise ValueError("está vacío")

    texto = str(valor).strip().replace("\u2212", "-")  # signo menos tipográfico (−)
    if texto == "":
        raise ValueError("está vacío")
    texto = texto.replace(" ", "")
    if "," in texto and "." in texto:
        raise ValueError("mezcla coma y punto; use un solo separador decimal y "
                         "no use separador de miles (escriba 1250000, no 1.250.000)")
    if texto.count(",") > 1 or texto.count(".") > 1:
        raise ValueError("tiene más de un separador; no use separador de miles "
                         "(escriba 1250000, no 1.250.000)")
    texto = texto.replace(",", ".")

    if "/" in texto:                                 # fracción a/b
        partes = texto.split("/")
        if len(partes) != 2 or partes[0] == "" or partes[1] == "":
            raise ValueError("no es una fracción válida (use el formato a/b, ej. 3/4)")
        numerador = _decimal(partes[0])
        denominador = _decimal(partes[1])
        if denominador == 0:
            raise ValueError("tiene una división por cero")
        return numerador / denominador
    return _decimal(texto)


def es_numero(valor) -> bool:
    """True si ``valor`` puede convertirse en número."""
    try:
        convertir_numero(valor)
        return True
    except ValueError:
        return False


def texto_numero(x) -> str:
    """Texto corto para mensajes del modelo: 5 | 5/2 (2.5) | -1/3 (-0.3333)."""
    if isinstance(x, ValorM):
        return str(x)
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    decimal = f"{float(x):.4f}".rstrip("0").rstrip(".")
    return f"{x.numerator}/{x.denominator} (≈{decimal})"


@total_ordering
class ValorM:
    """Número de la forma ``m·M + c`` con M "infinitamente grande".

    Se compara de forma lexicográfica: primero el coeficiente de M y luego
    la constante. Así ``M - 1000 > 999999`` y ``2M > M + 5``.
    Se usa para representar costos de rutas prohibidas en transporte.
    """

    __slots__ = ("c", "m")

    def __init__(self, c=0, m=0):
        self.c = Fraction(c)    # parte constante
        self.m = Fraction(m)    # coeficiente de M

    # ---------------------------------------------------------- conversión
    @staticmethod
    def de(valor) -> "ValorM":
        """Convierte int/Fraction/ValorM en ValorM."""
        if isinstance(valor, ValorM):
            return valor
        if isinstance(valor, (int, Fraction)) and not isinstance(valor, bool):
            return ValorM(valor, 0)
        raise TypeError(f"No se puede convertir {valor!r} en ValorM")

    @staticmethod
    def _es_compatible(valor) -> bool:
        return isinstance(valor, (ValorM, int, Fraction)) and not isinstance(valor, bool)

    @property
    def tiene_m(self) -> bool:
        return self.m != 0

    # ---------------------------------------------------------- aritmética
    def __add__(self, otro):
        if not self._es_compatible(otro):
            return NotImplemented
        otro = ValorM.de(otro)
        return ValorM(self.c + otro.c, self.m + otro.m)

    __radd__ = __add__

    def __sub__(self, otro):
        if not self._es_compatible(otro):
            return NotImplemented
        otro = ValorM.de(otro)
        return ValorM(self.c - otro.c, self.m - otro.m)

    def __rsub__(self, otro):
        if not self._es_compatible(otro):
            return NotImplemented
        return ValorM.de(otro) - self

    def __neg__(self):
        return ValorM(-self.c, -self.m)

    def __abs__(self):
        return -self if self < 0 else ValorM(self.c, self.m)

    def __mul__(self, escalar):
        if isinstance(escalar, ValorM):
            if escalar.m == 0:
                escalar = escalar.c
            elif self.m == 0:
                return escalar * self.c
            else:
                raise TypeError("No se puede multiplicar M por M")
        if not self._es_compatible(escalar):
            return NotImplemented
        escalar = Fraction(escalar)
        return ValorM(self.c * escalar, self.m * escalar)

    __rmul__ = __mul__

    # --------------------------------------------------------- comparación
    def __eq__(self, otro):
        if not self._es_compatible(otro):
            return NotImplemented
        otro = ValorM.de(otro)
        return self.m == otro.m and self.c == otro.c

    def __lt__(self, otro):
        if not self._es_compatible(otro):
            return NotImplemented
        otro = ValorM.de(otro)
        return (self.m, self.c) < (otro.m, otro.c)

    def __hash__(self):
        return hash((self.m, self.c))

    # -------------------------------------------------------------- texto
    def __repr__(self):
        return f"ValorM(c={self.c}, m={self.m})"

    def __str__(self):
        return formatear_valor_m(self, lambda f: str(f))


def formatear_valor_m(valor: ValorM, fmt) -> str:
    """Escribe ``a·M + b`` de forma legible usando ``fmt`` para los números."""
    if valor.m == 0:
        return fmt(valor.c)
    if valor.m == 1:
        parte_m = "M"
    elif valor.m == -1:
        parte_m = "-M"
    else:
        parte_m = f"{fmt(valor.m)}M"
    if valor.c == 0:
        return parte_m
    signo = "+" if valor.c > 0 else "-"
    return f"{parte_m} {signo} {fmt(abs(valor.c))}"


def convertir_costo(valor) -> ValorM:
    """Convierte un costo de transporte. Acepta números o la letra M (ruta prohibida)."""
    if isinstance(valor, ValorM):
        return valor
    texto = "" if valor is None else str(valor).strip()
    if texto.upper() == "M":
        return ValorM(0, 1)
    return ValorM(convertir_numero(valor), 0)
