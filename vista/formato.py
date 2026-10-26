"""
vista/formato.py
================
Formato de los números que se MUESTRAN en pantalla y en los reportes.

El modelo calcula con fracciones exactas; aquí se decide cómo verlas:
modo "fraccion" (5/3) o modo "decimal" (1.6667). El usuario cambia el modo
desde la barra lateral y todas las pantallas se vuelven a dibujar.
"""
from __future__ import annotations

from fractions import Fraction

from modelo.numeros import ValorM, formatear_valor_m

MODO_FRACCION = "fraccion"
MODO_DECIMAL = "decimal"


class FormatoNumeros:
    def __init__(self):
        self.modo = MODO_FRACCION
        self.decimales = 4
        self._oyentes = []

    # ----------------------------------------------------- cambio de modo
    def suscribir(self, funcion) -> None:
        """Registra una función que se llama cuando cambia el modo."""
        self._oyentes.append(funcion)

    def cambiar_modo(self, modo: str) -> None:
        if modo not in (MODO_FRACCION, MODO_DECIMAL) or modo == self.modo:
            return
        self.modo = modo
        for funcion in list(self._oyentes):
            funcion()

    # ------------------------------------------------------------ números
    def _fraccion(self, x) -> str:
        x = Fraction(x)
        if x.denominator == 1:
            return str(x.numerator)
        if self.modo == MODO_FRACCION and x.denominator <= 9999:
            return f"{x.numerator}/{x.denominator}"
        return self._decimal(x)

    def _decimal(self, x: Fraction) -> str:
        valor = float(x)
        if valor != 0 and abs(valor) < 10 ** (-self.decimales):
            return f"{valor:.3g}"
        texto = f"{valor:.{self.decimales}f}".rstrip("0").rstrip(".")
        return "0" if texto in ("-0", "") else texto

    def num(self, x) -> str:
        """Texto de un número (Fraction, int, ValorM). None -> '—'."""
        if x is None:
            return "—"
        if isinstance(x, ValorM):
            return formatear_valor_m(x, self._fraccion)
        return self._fraccion(x)

    def decimal(self, x) -> str:
        """Siempre en decimal (útil para aproximaciones entre paréntesis)."""
        if x is None:
            return "—"
        if isinstance(x, ValorM):
            return formatear_valor_m(x, lambda f: self._decimal(Fraction(f)))
        return self._decimal(Fraction(x))

    def num_doble(self, x) -> str:
        """Fracción y, si no es entera, su valor decimal: 5/3 (≈1.6667)."""
        if x is None:
            return "—"
        if isinstance(x, ValorM) or Fraction(x).denominator == 1 or self.modo == MODO_DECIMAL:
            return self.num(x)
        return f"{self.num(x)} (≈{self._decimal(Fraction(x))})"

    def par(self, x) -> str:
        """Número entre paréntesis si es negativo (para fórmulas: 3·(−2))."""
        texto = self.num(x)
        return f"({texto})" if texto.startswith("-") else texto

    def limite_inferior(self, x) -> str:
        return "-∞" if x is None else self.num(x)

    def limite_superior(self, x) -> str:
        return "+∞" if x is None else self.num(x)

    def cambio(self, x) -> str:
        """Aumento o disminución permitida (None = infinito)."""
        return "∞" if x is None else self.num(x)

    def vector(self, valores, separar_ultimo: bool = True) -> str:
        """[a, b, c | d] para mostrar filas de la tabla en las operaciones."""
        textos = [self.num(v) for v in valores]
        if separar_ultimo and len(textos) > 1:
            return "[" + ", ".join(textos[:-1]) + " | " + textos[-1] + "]"
        return "[" + ", ".join(textos) + "]"


FORMATO = FormatoNumeros()
