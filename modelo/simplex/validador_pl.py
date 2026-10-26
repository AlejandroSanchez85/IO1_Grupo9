"""
modelo/simplex/validador_pl.py
==============================
VALIDACIÓN de los datos de un problema de PL antes de resolverlo.

Recibe un diccionario con los textos que escribió el usuario (o que vienen
de un archivo JSON) y devuelve un ``ProblemaPL`` listo para el Simplex.
Si hay campos vacíos, texto en vez de números o datos imposibles, lanza
``ErrorValidacion`` con TODOS los errores encontrados (mensajes claros).

Formato del diccionario::

    {
      "nombre": "...", "descripcion": "...",
      "sentido": "max" | "min",
      "unidad_z": "COP/semana", "descripcion_z": "Utilidad",
      "variables": [{"nombre": "Mesas", "unidad": "mesas/semana", "c": "70000"}, ...],
      "restricciones": [{"nombre": "Carpintería", "unidad": "horas/semana",
                         "a": ["4", "3"], "b": "240", "signo": "<="}, ...]
    }
"""
from __future__ import annotations

from ..excepciones import ErrorValidacion
from ..numeros import convertir_numero
from .problema_pl import ProblemaPL, Restriccion, VariableDecision

MAX_VARIABLES = 8
MAX_RESTRICCIONES = 8
SIGNOS_VALIDOS = ("<=", "≤", "=<")


class ValidadorPL:
    """Convierte y valida los datos de entrada de un problema de PL."""

    def validar(self, datos: dict) -> ProblemaPL:
        errores: list[tuple[str, object]] = []

        # 1) Tipo de objetivo -------------------------------------------------
        sentido = str(datos.get("sentido", "max")).strip().lower()
        sentido = {"maximizar": "max", "minimizar": "min"}.get(sentido, sentido)
        if sentido not in ("max", "min"):
            errores.append(("El objetivo debe ser Maximizar o Minimizar.", ("sentido",)))

        variables_crudas = datos.get("variables") or []
        restricciones_crudas = datos.get("restricciones") or []
        n, m = len(variables_crudas), len(restricciones_crudas)

        # 2) Tamaño del problema (hasta 8 variables y 8 restricciones) ----------
        if not 1 <= n <= MAX_VARIABLES:
            errores.append((f"El número de variables debe estar entre 1 y {MAX_VARIABLES} "
                            f"(se recibieron {n}).", ("n",)))
        if not 1 <= m <= MAX_RESTRICCIONES:
            errores.append((f"El número de restricciones debe estar entre 1 y {MAX_RESTRICCIONES} "
                            f"(se recibieron {m}).", ("m",)))
        if errores:
            raise ErrorValidacion(errores)

        # 3) Variables de decisión: nombre, unidad y coeficiente cj -------------
        variables: list[VariableDecision] = []
        for j, cruda in enumerate(variables_crudas):
            simbolo = f"x{j + 1}"
            nombre = str(cruda.get("nombre", "")).strip() or simbolo
            unidad = str(cruda.get("unidad", "")).strip() or "unidades"
            c = self._numero(cruda.get("c"), f"el coeficiente de z (c{j + 1}) de «{nombre}»",
                             ("c", j), errores)
            variables.append(VariableDecision(simbolo, nombre, unidad, c))

        self._revisar_nombres_repetidos([v.nombre for v in variables], "variables", "nombre_var", errores)

        # 4) Restricciones: coeficientes aij, signo y lado derecho bi ------------
        restricciones: list[Restriccion] = []
        for i, cruda in enumerate(restricciones_crudas):
            simbolo = f"R{i + 1}"
            nombre = str(cruda.get("nombre", "")).strip() or simbolo
            unidad = str(cruda.get("unidad", "")).strip() or "unidades"
            signo = str(cruda.get("signo", "<=")).strip()
            if signo not in SIGNOS_VALIDOS:
                errores.append((f"La restricción «{nombre}» tiene el signo «{signo}». El método Simplex "
                                f"de este programa trabaja con restricciones ≤ (según la guía del "
                                f"proyecto). Las restricciones ≥ o = requieren Gran M o Dos Fases.",
                                ("signo", i)))
            coeficientes_crudos = list(cruda.get("a") or [])
            if len(coeficientes_crudos) != n:
                errores.append((f"La restricción «{nombre}» debe tener {n} coeficientes "
                                f"(tiene {len(coeficientes_crudos)}).", ("a", i, 0)))
                coeficientes_crudos = (coeficientes_crudos + [""] * n)[:n]
            coeficientes = []
            for j, texto in enumerate(coeficientes_crudos):
                coeficientes.append(self._numero(
                    texto, f"el coeficiente a{i + 1}{j + 1} (de «{variables[j].nombre}» en «{nombre}»)",
                    ("a", i, j), errores))
            b = self._numero(cruda.get("b"), f"el valor disponible b{i + 1} de «{nombre}»",
                             ("b", i), errores)
            if b is not None and b < 0:
                errores.append((f"El lado derecho b{i + 1} de «{nombre}» es negativo. El Simplex con "
                                f"restricciones ≤ necesita b ≥ 0 para empezar con las holguras como "
                                f"base (origen factible). Revise el dato: una disponibilidad no puede "
                                f"ser negativa.", ("b", i)))
            restricciones.append(Restriccion(simbolo, nombre, unidad, coeficientes, b))

        self._revisar_nombres_repetidos([r.nombre for r in restricciones], "restricciones",
                                        "nombre_res", errores)
        if errores:
            raise ErrorValidacion(errores)

        return ProblemaPL(
            nombre=str(datos.get("nombre", "")).strip() or "Problema sin nombre",
            sentido=sentido,
            unidad_z=str(datos.get("unidad_z", "")).strip() or "unidades de z",
            descripcion_z=str(datos.get("descripcion_z", "")).strip() or "Valor de z",
            variables=variables,
            restricciones=restricciones,
            descripcion=str(datos.get("descripcion", "")).strip(),
            datos_originales=dict(datos),
        )

    # ------------------------------------------------------------- auxiliares
    @staticmethod
    def _numero(texto, descripcion: str, campo, errores):
        """Convierte un número; si falla agrega un mensaje claro a ``errores``."""
        try:
            return convertir_numero(texto)
        except ValueError as error:
            mostrado = "" if texto is None else str(texto).strip()
            if mostrado == "":
                errores.append((f"Falta {descripcion}: la casilla está vacía.", campo))
            else:
                errores.append((f"En {descripcion} el valor «{mostrado}» {error}.", campo))
            return None

    @staticmethod
    def _revisar_nombres_repetidos(nombres, que, clave, errores):
        vistos = {}
        for k, nombre in enumerate(nombres):
            llave = nombre.strip().lower()
            if llave in vistos:
                errores.append((f"Hay dos {que} con el mismo nombre «{nombre}». Use nombres distintos "
                                f"para que los resultados no se confundan.", (clave, k)))
            else:
                vistos[llave] = k
