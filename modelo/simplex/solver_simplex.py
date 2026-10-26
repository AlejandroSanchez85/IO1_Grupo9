"""
modelo/simplex/solver_simplex.py
================================
MÉTODO SIMPLEX (maximizar o minimizar) con restricciones <=, programado
desde cero (sin SciPy, PuLP, OR-Tools ni ningún otro solver).

Pasos del método (cada paso está marcado en el código):

  PASO 1. Forma estándar: se suma una variable de holgura s_i a cada
          restricción (a_i·x + s_i = b_i). La base inicial son las holguras.
  PASO 2. Prueba de optimalidad con el renglón Cj − Zj:
            - Maximizar: la tabla es óptima si todos los Cj − Zj <= 0.
            - Minimizar: la tabla es óptima si todos los Cj − Zj >= 0.
  PASO 3. Variable que ENTRA: la de mayor Cj − Zj positivo (max) o la de
          Cj − Zj más negativo (min). Empates: se elige la de menor índice.
  PASO 4. Variable que SALE: prueba de la razón mínima b_i / a_ik (solo
          a_ik > 0). Si no hay a_ik > 0 el problema es NO ACOTADO.
          Empates (degeneración): se elige la básica de menor índice.
  PASO 5. Pivoteo de Gauss-Jordan sobre el elemento pivote; volver al PASO 2.
  PASO 6. Casos especiales: no acotado, óptimos alternativos (Cj − Zj = 0 en
          una variable no básica), degeneración (básica = 0) y ciclaje
          (si una base se repite se cambia a la regla de Bland).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from fractions import Fraction

from ..caso_especial import (CICLAJE, DEGENERACION, EMPATE, INFORMATIVO, NIVEL_ADVERTENCIA,
                             NIVEL_ERROR, NIVEL_INFO, NO_ACOTADO, OPTIMOS_ALTERNATIVOS,
                             CasoEspecial)
from ..numeros import texto_numero
from .problema_pl import ProblemaPL
from .tabla_simplex import TablaSimplex

# Estado de cada iteración (tabla)
CONTINUA = "continua"          # no es óptima: se hace un pivoteo
OPTIMA = "optima"              # cumple la prueba de optimalidad
NO_ACOTADA = "no_acotada"      # la variable que entra no tiene a_ik > 0
ALTERNATIVA = "alternativa"    # tabla de una solución óptima alternativa
LIMITE = "limite"              # se alcanzó el máximo de iteraciones

# Estado final del problema
ESTADO_OPTIMO = "optimo"
ESTADO_NO_ACOTADO = "no_acotado"
ESTADO_LIMITE = "limite_iteraciones"


@dataclass
class IteracionSimplex:
    """Una tabla del método con toda la información de la decisión tomada."""
    numero: int
    tabla: TablaSimplex
    estado: str
    columna_entra: int | None = None          # variable que entra
    fila_sale: int | None = None              # fila de la variable que sale
    pivote: Fraction | None = None            # elemento pivote
    razones: list = field(default_factory=list)            # b_i / a_ik (None si a_ik <= 0)
    candidatos_entrada: list[int] = field(default_factory=list)
    empate_entrada: list[int] = field(default_factory=list)
    empate_salida: list[int] = field(default_factory=list)
    regla: str = "dantzig"                    # "dantzig" (normal) o "bland" (anti-ciclaje)
    factores: list[Fraction] = field(default_factory=list)  # factores de las operaciones de fila
    pivoteo_degenerado: bool = False          # razón mínima = 0 -> z no cambia
    columnas_cero: list[int] = field(default_factory=list)  # no básicas con Cj − Zj = 0 (en la óptima)

    @property
    def hay_pivoteo(self) -> bool:
        return self.columna_entra is not None and self.fila_sale is not None


@dataclass
class ResultadoSimplex:
    problema: ProblemaPL
    iteraciones: list[IteracionSimplex]
    estado: str
    casos: list[CasoEspecial]
    iteracion_alternativa: IteracionSimplex | None = None
    columna_no_acotada: int | None = None
    ciclaje_detectado: bool = False
    tiempo_ms: float = 0.0

    @property
    def es_optimo(self) -> bool:
        return self.estado == ESTADO_OPTIMO

    @property
    def tabla_final(self) -> TablaSimplex:
        return self.iteraciones[-1].tabla

    @property
    def numero_pivoteos(self) -> int:
        return sum(1 for it in self.iteraciones if it.estado == CONTINUA)

    @property
    def z(self) -> Fraction | None:
        return self.tabla_final.z if self.es_optimo else None

    def valores_variables(self, tabla: TablaSimplex | None = None) -> list[Fraction]:
        tabla = tabla or self.tabla_final
        return [tabla.valor(j) for j in range(self.problema.n)]

    def valores_holguras(self, tabla: TablaSimplex | None = None) -> list[Fraction]:
        tabla = tabla or self.tabla_final
        n = self.problema.n
        return [tabla.valor(n + i) for i in range(self.problema.m)]

    def solucion_alternativa(self) -> list[Fraction] | None:
        if self.iteracion_alternativa is None:
            return None
        return self.valores_variables(self.iteracion_alternativa.tabla)


class SolverSimplex:
    """Resuelve un ``ProblemaPL`` con el método Simplex tabular."""

    MAX_ITERACIONES = 100

    def __init__(self, problema: ProblemaPL):
        self.problema = problema

    # ------------------------------------------------------------------ util
    def _mejora(self, valor: Fraction) -> bool:
        """True si un Cj − Zj con este valor mejora z (criterio de entrada)."""
        return valor > 0 if self.problema.es_max else valor < 0

    def _etiqueta_columna(self, j: int) -> str:
        p = self.problema
        if j < p.n:
            return p.variables[j].etiqueta
        return f"s{j - p.n + 1} (holgura de {p.restricciones[j - p.n].nombre})"

    def _texto_solucion(self, tabla: TablaSimplex) -> str:
        p = self.problema
        partes = [f"{v.nombre} = {texto_numero(tabla.valor(j))}" for j, v in enumerate(p.variables)]
        return ", ".join(partes) + f"  (z = {texto_numero(tabla.z)})"

    # ------------------------------------------------------- PASO 1: forma estándar
    def tabla_inicial(self) -> TablaSimplex:
        p = self.problema
        n, m = p.n, p.m
        cj = list(p.c) + [Fraction(0)] * m                    # las holguras no aportan a z
        matriz = []
        for i, restriccion in enumerate(p.restricciones):
            holguras = [Fraction(1) if k == i else Fraction(0) for k in range(m)]
            matriz.append(list(restriccion.coeficientes) + holguras)
        base = [n + i for i in range(m)]                       # base inicial: s1 ... sm
        return TablaSimplex(p.simbolos_columnas(), cj, base, matriz, list(p.b))

    # ------------------------------------------------------------- resolver
    def resolver(self) -> ResultadoSimplex:
        inicio = time.perf_counter()
        tabla = self.tabla_inicial()
        iteraciones: list[IteracionSimplex] = []
        regla = "dantzig"
        bases_vistas = {tuple(sorted(tabla.base))}
        ciclaje = False
        estado = ESTADO_LIMITE
        columna_no_acotada = None
        numero = 0

        while True:
            # PASO 2: prueba de optimalidad (renglón Cj − Zj)
            candidatos = [j for j in range(tabla.columnas)
                          if not tabla.es_basica(j) and self._mejora(tabla.cj_menos_zj[j])]
            if not candidatos:
                columnas_cero = [j for j in range(tabla.columnas)
                                 if not tabla.es_basica(j) and tabla.cj_menos_zj[j] == 0]
                iteraciones.append(IteracionSimplex(numero, tabla, OPTIMA, regla=regla,
                                                    columnas_cero=columnas_cero))
                estado = ESTADO_OPTIMO
                break
            if numero >= self.MAX_ITERACIONES:
                iteraciones.append(IteracionSimplex(numero, tabla, LIMITE, regla=regla,
                                                    candidatos_entrada=candidatos))
                estado = ESTADO_LIMITE
                break

            # PASO 3: variable que entra
            if regla == "bland":
                entra = min(candidatos)                        # regla de Bland: menor índice
                empate_entrada = []
            else:
                mejor = max(abs(tabla.cj_menos_zj[j]) for j in candidatos)
                empatadas = [j for j in candidatos if abs(tabla.cj_menos_zj[j]) == mejor]
                entra = empatadas[0]                           # empate: menor índice
                empate_entrada = empatadas if len(empatadas) > 1 else []

            # PASO 4: prueba de la razón mínima b_i / a_ik con a_ik > 0
            razones = [tabla.b[i] / tabla.matriz[i][entra] if tabla.matriz[i][entra] > 0 else None
                       for i in range(tabla.m)]
            validas = [i for i, r in enumerate(razones) if r is not None]
            if not validas:                                    # no hay a_ik > 0 -> NO ACOTADO
                iteraciones.append(IteracionSimplex(numero, tabla, NO_ACOTADA, columna_entra=entra,
                                                    razones=razones, candidatos_entrada=candidatos,
                                                    empate_entrada=empate_entrada, regla=regla))
                estado = ESTADO_NO_ACOTADO
                columna_no_acotada = entra
                break
            minima = min(razones[i] for i in validas)
            empatadas_salida = [i for i in validas if razones[i] == minima]
            sale = min(empatadas_salida, key=lambda i: tabla.base[i])  # empate: básica de menor índice
            pivote = tabla.matriz[sale][entra]

            # PASO 5: pivoteo de Gauss-Jordan
            nueva, factores = tabla.pivotear(sale, entra)
            iteraciones.append(IteracionSimplex(
                numero, tabla, CONTINUA, entra, sale, pivote, razones, candidatos, empate_entrada,
                empatadas_salida if len(empatadas_salida) > 1 else [], regla, factores,
                pivoteo_degenerado=(minima == 0)))
            tabla = nueva
            numero += 1

            # Control de ciclaje: si una base se repite se cambia a la regla de Bland
            clave = tuple(sorted(tabla.base))
            if clave in bases_vistas and regla != "bland":
                ciclaje = True
                regla = "bland"
            bases_vistas.add(clave)

        resultado = ResultadoSimplex(self.problema, iteraciones, estado, [],
                                     columna_no_acotada=columna_no_acotada, ciclaje_detectado=ciclaje)
        # PASO 6: casos especiales
        self._detectar_casos_especiales(resultado)
        resultado.tiempo_ms = (time.perf_counter() - inicio) * 1000
        return resultado

    # ------------------------------------------------- PASO 6: casos especiales
    def _detectar_casos_especiales(self, resultado: ResultadoSimplex) -> None:
        p = self.problema
        casos = resultado.casos
        ultima = resultado.iteraciones[-1]

        # a) Problema no acotado
        if resultado.estado == ESTADO_NO_ACOTADO:
            k = resultado.columna_no_acotada
            direccion = "aumentar" if p.es_max else "disminuir"
            infinito = "+∞" if p.es_max else "−∞"
            casos.append(CasoEspecial(
                NO_ACOTADO, "Problema NO ACOTADO",
                f"La variable que debería entrar, {self._etiqueta_columna(k)}, no tiene coeficientes "
                f"positivos en su columna: ninguna restricción la limita. Puede crecer sin fin y z puede "
                f"{direccion} indefinidamente (z → {infinito}). No existe una solución óptima finita. "
                f"Revise si falta una restricción (capacidad, demanda, presupuesto...).",
                NIVEL_ERROR))

        if resultado.estado == ESTADO_LIMITE:
            casos.append(CasoEspecial(
                INFORMATIVO, "Límite de iteraciones",
                f"Se alcanzó el máximo de {self.MAX_ITERACIONES} iteraciones sin llegar al óptimo.",
                NIVEL_ERROR))

        # b) Óptimos alternativos: Cj − Zj = 0 en alguna variable no básica
        if resultado.estado == ESTADO_OPTIMO and ultima.columnas_cero:
            self._analizar_optimos_alternativos(resultado, ultima)

        # c) Degeneración: alguna variable básica vale 0 o hubo empate en la razón mínima
        tablas_degeneradas = [it.numero for it in resultado.iteraciones if it.tabla.es_degenerada()]
        empates_razon = [it.numero for it in resultado.iteraciones if it.empate_salida]
        if tablas_degeneradas or empates_razon:
            partes = []
            if empates_razon:
                partes.append("hubo empate en la razón mínima en la(s) iteración(es) "
                              + ", ".join(str(k) for k in empates_razon))
            if tablas_degeneradas:
                partes.append("al menos una variable básica vale 0 en la(s) tabla(s) "
                              + ", ".join(str(k) for k in tablas_degeneradas))
            mensaje = ("Solución DEGENERADA: " + "; ".join(partes) + ". Un pivoteo con razón 0 no "
                       "cambia z. El programa usa una regla de desempate fija (y la regla de Bland si "
                       "detecta ciclaje), así que el método siempre termina.")
            if resultado.estado == ESTADO_OPTIMO and resultado.tabla_final.es_degenerada():
                mensaje += (" Como la tabla óptima es degenerada, los precios sombra pueden no ser "
                            "únicos y algún rango de sensibilidad puede tener amplitud 0 en un lado.")
            casos.append(CasoEspecial(DEGENERACION, "Degeneración", mensaje, NIVEL_ADVERTENCIA))

        # d) Ciclaje
        if resultado.ciclaje_detectado:
            casos.append(CasoEspecial(
                CICLAJE, "Ciclaje detectado",
                "Una base se repitió (ciclaje por degeneración). A partir de ese momento se aplicó la "
                "regla de Bland (entra y sale la variable de menor índice) para garantizar que el "
                "método termine.", NIVEL_ADVERTENCIA))

        # e) Empates en la variable que entra (informativo)
        for it in resultado.iteraciones:
            if it.empate_entrada:
                nombres = ", ".join(it.tabla.simbolos[j] for j in it.empate_entrada)
                casos.append(CasoEspecial(
                    EMPATE, f"Empate en la variable que entra (iteración {it.numero})",
                    f"Las variables {nombres} empatan con el mismo |Cj − Zj|. Se eligió la de menor "
                    f"índice ({it.tabla.simbolos[it.columna_entra]}). La elección no cambia el valor "
                    f"óptimo, solo el camino.", NIVEL_INFO))

        # f) Avisos informativos
        if all(c == 0 for c in p.c):
            casos.append(CasoEspecial(
                INFORMATIVO, "Todos los coeficientes de z son 0",
                "Cualquier punto factible da z = 0: todos son óptimos.", NIVEL_INFO))
        elif resultado.estado == ESTADO_OPTIMO and len(resultado.iteraciones) == 1:
            casos.append(CasoEspecial(
                INFORMATIVO, "La tabla inicial ya es óptima",
                "Ninguna variable mejora z al entrar a la base, por eso la solución óptima es dejar "
                "todas las variables de decisión en 0. "
                + ("(Al minimizar con restricciones ≤ y coeficientes ≥ 0, no hacer nada es lo más barato.)"
                   if not p.es_max else ""), NIVEL_INFO))

    def _analizar_optimos_alternativos(self, resultado: ResultadoSimplex, ultima: IteracionSimplex):
        """Busca otra solución óptima haciendo entrar una no básica con Cj − Zj = 0."""
        tabla = ultima.tabla
        for k in ultima.columnas_cero:
            razones = [tabla.b[i] / tabla.matriz[i][k] if tabla.matriz[i][k] > 0 else None
                       for i in range(tabla.m)]
            validas = [i for i, r in enumerate(razones) if r is not None]
            if not validas:
                resultado.casos.append(CasoEspecial(
                    OPTIMOS_ALTERNATIVOS, "Óptimos alternativos (infinitos, conjunto no acotado)",
                    f"La variable no básica {self._etiqueta_columna(k)} tiene Cj − Zj = 0 y su columna "
                    f"no tiene coeficientes positivos: puede crecer sin límite SIN cambiar z. Hay "
                    f"infinitas soluciones óptimas con z = {texto_numero(tabla.z)}.", NIVEL_ADVERTENCIA))
                return
            minima = min(razones[i] for i in validas)
            if minima == 0:
                continue                      # pivoteo degenerado: llevaría al mismo punto
            empatadas = [i for i in validas if razones[i] == minima]
            sale = min(empatadas, key=lambda i: tabla.base[i])
            nueva, factores = tabla.pivotear(sale, k)
            # Se guarda la información del pivoteo en la tabla óptima para explicarlo
            ultima.columna_entra, ultima.fila_sale = k, sale
            ultima.pivote, ultima.razones, ultima.factores = tabla.matriz[sale][k], razones, factores
            resultado.iteracion_alternativa = IteracionSimplex(ultima.numero + 1, nueva, ALTERNATIVA)
            resultado.casos.append(CasoEspecial(
                OPTIMOS_ALTERNATIVOS, "Óptimos ALTERNATIVOS (soluciones múltiples)",
                f"La variable no básica {self._etiqueta_columna(k)} tiene Cj − Zj = 0: si entra a la "
                f"base, z no cambia. Solución 1: {self._texto_solucion(tabla)}. Solución 2: "
                f"{self._texto_solucion(nueva)}. Cualquier punto del segmento λ·S1 + (1 − λ)·S2, con "
                f"0 ≤ λ ≤ 1, también es óptimo. La empresa puede escoger la que más le convenga.",
                NIVEL_ADVERTENCIA))
            return
        resultado.casos.append(CasoEspecial(
            OPTIMOS_ALTERNATIVOS, "Cj − Zj = 0 en una variable no básica (caso degenerado)",
            "Hay variables no básicas con Cj − Zj = 0, pero por la degeneración el cambio de base no "
            "mueve la solución (la razón mínima es 0): desde esta tabla no se obtiene otro punto óptimo "
            "distinto.", NIVEL_INFO))
