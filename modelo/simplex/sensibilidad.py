"""
modelo/simplex/sensibilidad.py
==============================
ANÁLISIS DE SENSIBILIDAD calculado desde la TABLA ÓPTIMA del Simplex.

Como la base inicial son las holguras, en la tabla óptima las columnas de
s1..sm contienen la matriz inversa de la base, B^-1.

  1. Precio sombra de la restricción i:   y_i = Zj de la columna s_i
                                          (y = Cb · B^-1)
     Indica cuánto cambia z si b_i aumenta en 1 unidad.
  2. Costo reducido de x_j:              Cj − Zj (0 si x_j es básica).
  3. Rango de cada c_j (optimalidad): intervalo de c_j en el que la base
     actual sigue siendo óptima (las cantidades x* no cambian).
       - x_j NO básica:  Max: c_j <= Zj    |  Min: c_j >= Zj
       - x_j básica en la fila r: con Δ = cambio de c_j, cada no básica l
         debe seguir cumpliendo la prueba de optimalidad:
             (Cl − Zl) − Δ · a_rl  <= 0  (Max)   ó   >= 0  (Min)
  4. Rango de cada b_i (factibilidad): intervalo de b_i en el que la base
     sigue siendo factible y el precio sombra sigue siendo válido:
             x_B + Δ · (columna i de B^-1) >= 0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

from ..caso_especial import (DEGENERACION, INFORMATIVO, NIVEL_ADVERTENCIA, NIVEL_INFO,
                             OPTIMOS_ALTERNATIVOS, CasoEspecial)
from .problema_pl import ProblemaPL
from .solver_simplex import ResultadoSimplex
from .tabla_simplex import TablaSimplex

INFERIOR = "inferior"     # el cociente limita la disminución
SUPERIOR = "superior"     # el cociente limita el aumento
NINGUNO = "ninguno"       # el coeficiente es 0: no limita


@dataclass
class CalculoRango:
    """Un cociente usado para calcular un rango (se muestra en el paso a paso)."""
    referencia: str           # columna (rango de c_j) o variable básica (rango de b_i)
    numerador: Fraction
    denominador: Fraction
    cociente: Fraction | None
    tipo: str


@dataclass
class RangoCosto:
    """Rango de optimalidad del coeficiente c_j de una variable de decisión."""
    indice: int
    simbolo: str
    nombre: str
    unidad: str
    valor_actual: Fraction
    es_basica: bool
    valor_variable: Fraction
    costo_reducido: Fraction
    disminucion: Fraction | None          # None = puede disminuir sin límite (∞)
    aumento: Fraction | None              # None = puede aumentar sin límite (∞)
    calculos: list[CalculoRango] = field(default_factory=list)

    @property
    def minimo(self) -> Fraction | None:
        return None if self.disminucion is None else self.valor_actual - self.disminucion

    @property
    def maximo(self) -> Fraction | None:
        return None if self.aumento is None else self.valor_actual + self.aumento


@dataclass
class RangoRecurso:
    """Precio sombra y rango de factibilidad del lado derecho b_i."""
    indice: int
    simbolo: str
    nombre: str
    unidad: str
    valor_actual: Fraction
    holgura: Fraction
    precio_sombra: Fraction
    disminucion: Fraction | None
    aumento: Fraction | None
    calculos: list[CalculoRango] = field(default_factory=list)

    @property
    def usado(self) -> Fraction:
        return self.valor_actual - self.holgura

    @property
    def activa(self) -> bool:
        """Restricción activa = sin holgura (el recurso se usa completo)."""
        return self.holgura == 0

    @property
    def minimo(self) -> Fraction | None:
        return None if self.disminucion is None else self.valor_actual - self.disminucion

    @property
    def maximo(self) -> Fraction | None:
        return None if self.aumento is None else self.valor_actual + self.aumento


@dataclass
class ResultadoSensibilidad:
    problema: ProblemaPL
    tabla: TablaSimplex
    binv: list[list[Fraction]]            # B^-1 (columnas de las holguras en la tabla óptima)
    simbolos_base: list[str]
    cb: list[Fraction]
    xb: list[Fraction]
    precios_sombra: list[Fraction]
    rangos_costos: list[RangoCosto]
    rangos_recursos: list[RangoRecurso]
    z: Fraction
    z_dual: Fraction                      # Σ b_i · y_i (debe ser igual a z)
    casos: list[CasoEspecial] = field(default_factory=list)


class AnalizadorSensibilidad:
    """Calcula el análisis de sensibilidad de un ``ResultadoSimplex`` óptimo."""

    def __init__(self, resultado: ResultadoSimplex):
        if not resultado.es_optimo:
            raise ValueError("El análisis de sensibilidad requiere una solución óptima.")
        self.resultado = resultado
        self.problema = resultado.problema
        self.tabla = resultado.tabla_final           # primera tabla óptima encontrada

    def analizar(self) -> ResultadoSensibilidad:
        p, t = self.problema, self.tabla
        n, m = p.n, p.m
        es_max = p.es_max

        # 1) Matriz B^-1 = columnas de las holguras en la tabla óptima
        binv = [[t.matriz[i][n + k] for k in range(m)] for i in range(m)]

        # 2) Precios sombra: y_i = Zj de la columna s_i  (y = Cb · B^-1)
        precios = [t.zj[n + i] for i in range(m)]

        # 3) Rangos de los coeficientes c_j
        no_basicas = [l for l in range(t.columnas) if not t.es_basica(l)]
        rangos_costos = []
        for j, variable in enumerate(p.variables):
            d_j = t.cj_menos_zj[j]
            calculos: list[CalculoRango] = []
            fila = t.fila_de(j)
            if fila is None:
                # x_j no básica: solo cambia su propio Cj − Zj
                if es_max:          # se necesita Cj − Zj <= 0  ->  c_j <= Zj
                    disminucion, aumento = None, -d_j
                else:               # se necesita Cj − Zj >= 0  ->  c_j >= Zj
                    disminucion, aumento = d_j, None
                calculos.append(CalculoRango(t.simbolos[j], d_j, Fraction(1), d_j, NINGUNO))
            else:
                # x_j básica en la fila r: revisar cada columna no básica l
                cotas_disminucion, cotas_aumento = [], []
                for l in no_basicas:
                    a = t.matriz[fila][l]
                    d = t.cj_menos_zj[l]
                    if a == 0:
                        calculos.append(CalculoRango(t.simbolos[l], d, a, None, NINGUNO))
                        continue
                    cociente = d / a
                    # Max: d − Δa <= 0 ;  Min: d − Δa >= 0
                    limita_aumento = (a < 0) if es_max else (a > 0)
                    if limita_aumento:
                        cotas_aumento.append(abs(cociente))
                        calculos.append(CalculoRango(t.simbolos[l], d, a, cociente, SUPERIOR))
                    else:
                        cotas_disminucion.append(abs(cociente))
                        calculos.append(CalculoRango(t.simbolos[l], d, a, cociente, INFERIOR))
                disminucion = min(cotas_disminucion) if cotas_disminucion else None
                aumento = min(cotas_aumento) if cotas_aumento else None
            rangos_costos.append(RangoCosto(
                j, variable.simbolo, variable.nombre, variable.unidad, variable.coeficiente,
                fila is not None, t.valor(j), d_j, disminucion, aumento, calculos))

        # 4) Rangos de los lados derechos b_i (columna i de B^-1)
        rangos_recursos = []
        for i, restriccion in enumerate(p.restricciones):
            calculos = []
            cotas_disminucion, cotas_aumento = [], []
            for k in range(m):
                beta = binv[k][i]
                xb = t.b[k]
                referencia = t.simbolos[t.base[k]]
                if beta == 0:
                    calculos.append(CalculoRango(referencia, xb, beta, None, NINGUNO))
                    continue
                cociente = -xb / beta                 # x_Bk + Δ·β_k >= 0
                if beta > 0:
                    cotas_disminucion.append(xb / beta)
                    calculos.append(CalculoRango(referencia, xb, beta, cociente, INFERIOR))
                else:
                    cotas_aumento.append(xb / -beta)
                    calculos.append(CalculoRango(referencia, xb, beta, cociente, SUPERIOR))
            rangos_recursos.append(RangoRecurso(
                i, restriccion.simbolo, restriccion.nombre, restriccion.unidad,
                restriccion.lado_derecho, t.valor(n + i), precios[i],
                min(cotas_disminucion) if cotas_disminucion else None,
                min(cotas_aumento) if cotas_aumento else None, calculos))

        z_dual = sum((p.b[i] * precios[i] for i in range(m)), Fraction(0))
        resultado = ResultadoSensibilidad(
            p, t, binv, [t.simbolos[k] for k in t.base], list(t.cb), list(t.b), precios,
            rangos_costos, rangos_recursos, t.z, z_dual)
        self._casos_especiales(resultado)
        return resultado

    # ------------------------------------------------------- casos especiales
    def _casos_especiales(self, r: ResultadoSensibilidad) -> None:
        infinitos = [f"c de {rc.nombre}" for rc in r.rangos_costos if rc.disminucion is None or rc.aumento is None]
        infinitos += [f"b de {rr.nombre}" for rr in r.rangos_recursos if rr.disminucion is None or rr.aumento is None]
        if infinitos:
            r.casos.append(CasoEspecial(
                INFORMATIVO, "Rangos infinitos",
                "Tienen un límite infinito (∞): " + "; ".join(infinitos) + ". Significa que ese dato "
                "puede subir (o bajar) tanto como se quiera sin cambiar la base óptima.", NIVEL_INFO))
        activas = [rr.nombre for rr in r.rangos_recursos if rr.activa]
        if activas:
            r.casos.append(CasoEspecial(
                INFORMATIVO, "Restricciones sin holgura (activas)",
                "Se usan por completo: " + ", ".join(activas) + ". Son los cuellos de botella: "
                "sus precios sombra indican cuánto mejoraría z con una unidad más.", NIVEL_INFO))
        if r.tabla.es_degenerada():
            r.casos.append(CasoEspecial(
                DEGENERACION, "Solución óptima degenerada",
                "Una variable básica vale 0. Los precios sombra pueden no ser únicos y algún rango de "
                "b_i tiene amplitud 0 hacia un lado.", NIVEL_ADVERTENCIA))
        no_basicas_cero = [j for j in range(r.tabla.columnas)
                           if not r.tabla.es_basica(j) and r.tabla.cj_menos_zj[j] == 0]
        if no_basicas_cero:
            r.casos.append(CasoEspecial(
                OPTIMOS_ALTERNATIVOS, "Hay óptimos alternativos",
                "Alguna variable no básica tiene Cj − Zj = 0; por eso algún rango de c_j tiene "
                "amplitud 0 hacia un lado (cualquier cambio en esa dirección cambia la solución).",
                NIVEL_ADVERTENCIA))
