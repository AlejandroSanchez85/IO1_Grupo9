"""
modelo/transporte/validador_transporte.py
=========================================
VALIDACIÓN de los datos de un problema de transporte.

Formato del diccionario::

    {
      "nombre": "...", "descripcion": "...",
      "unidad_producto": "cajas", "unidad_costo": "COP",
      "origenes": [{"nombre": "Planta 1", "oferta": "300"}, ...],
      "destinos": [{"nombre": "Tienda A", "demanda": "200"}, ...],
      "costos": [["8", "6", "M"], ...]        # M = ruta prohibida
    }
"""
from __future__ import annotations

from fractions import Fraction

from ..excepciones import ErrorValidacion
from ..numeros import convertir_costo, convertir_numero
from .problema_transporte import ProblemaTransporte

MAX_ORIGENES = 8
MAX_DESTINOS = 8


class ValidadorTransporte:
    """Convierte y valida los datos de entrada de un problema de transporte."""

    def validar(self, datos: dict) -> ProblemaTransporte:
        errores: list[tuple[str, object]] = []
        origenes_crudos = datos.get("origenes") or []
        destinos_crudos = datos.get("destinos") or []
        m, n = len(origenes_crudos), len(destinos_crudos)

        # 1) Tamaño: hasta 8 orígenes × 8 destinos
        if not 1 <= m <= MAX_ORIGENES:
            errores.append((f"El número de orígenes debe estar entre 1 y {MAX_ORIGENES} "
                            f"(se recibieron {m}).", ("m",)))
        if not 1 <= n <= MAX_DESTINOS:
            errores.append((f"El número de destinos debe estar entre 1 y {MAX_DESTINOS} "
                            f"(se recibieron {n}).", ("n",)))
        if errores:
            raise ErrorValidacion(errores)

        # 2) Nombres y ofertas de los orígenes
        origenes, oferta = [], []
        for i, crudo in enumerate(origenes_crudos):
            nombre = str(crudo.get("nombre", "")).strip() or f"Origen {i + 1}"
            origenes.append(nombre)
            valor = self._numero(crudo.get("oferta"), f"la oferta de «{nombre}»", ("oferta", i), errores)
            if valor is not None and valor < 0:
                errores.append((f"La oferta de «{nombre}» es negativa. Una oferta (capacidad) no "
                                f"puede ser menor que 0.", ("oferta", i)))
            oferta.append(valor)

        # 3) Nombres y demandas de los destinos
        destinos, demanda = [], []
        for j, crudo in enumerate(destinos_crudos):
            nombre = str(crudo.get("nombre", "")).strip() or f"Destino {j + 1}"
            destinos.append(nombre)
            valor = self._numero(crudo.get("demanda"), f"la demanda de «{nombre}»", ("demanda", j), errores)
            if valor is not None and valor < 0:
                errores.append((f"La demanda de «{nombre}» es negativa. Una demanda no puede ser "
                                f"menor que 0.", ("demanda", j)))
            demanda.append(valor)

        self._repetidos(origenes, "orígenes", "nombre_origen", errores)
        self._repetidos(destinos, "destinos", "nombre_destino", errores)

        # 4) Matriz de costos unitarios (número >= 0 o M)
        costos_crudos = datos.get("costos") or []
        costos = []
        for i in range(m):
            fila_cruda = list(costos_crudos[i]) if i < len(costos_crudos) else []
            fila_cruda = (fila_cruda + [""] * n)[:n]
            fila = []
            for j, texto in enumerate(fila_cruda):
                descripcion = f"el costo de «{origenes[i]}» a «{destinos[j]}»"
                try:
                    costo = convertir_costo(texto)
                    if costo.m < 0 or (costo.m == 0 and costo.c < 0):
                        errores.append((f"En {descripcion} el valor es negativo. Un costo de "
                                        f"transporte no puede ser negativo.", ("costo", i, j)))
                    fila.append(costo)
                except ValueError as error:
                    mostrado = "" if texto is None else str(texto).strip()
                    if mostrado == "":
                        errores.append((f"Falta {descripcion}: la casilla está vacía (escriba un "
                                        f"número, o M si la ruta está prohibida).", ("costo", i, j)))
                    else:
                        errores.append((f"En {descripcion} el valor «{mostrado}» {error} "
                                        f"(o escriba M si la ruta está prohibida).", ("costo", i, j)))
                    fila.append(None)
            costos.append(fila)

        # 5) Datos imposibles a nivel global
        if not errores:
            if sum(oferta, Fraction(0)) == 0:
                errores.append(("La oferta total es 0: no hay nada que transportar.", ("oferta", 0)))
            if sum(demanda, Fraction(0)) == 0:
                errores.append(("La demanda total es 0: no hay nada que transportar.", ("demanda", 0)))
        if errores:
            raise ErrorValidacion(errores)

        return ProblemaTransporte(
            nombre=str(datos.get("nombre", "")).strip() or "Problema de transporte",
            unidad_producto=str(datos.get("unidad_producto", "")).strip() or "unidades",
            unidad_costo=str(datos.get("unidad_costo", "")).strip() or "$",
            origenes=origenes, destinos=destinos, oferta=oferta, demanda=demanda, costos=costos,
            descripcion=str(datos.get("descripcion", "")).strip(), datos_originales=dict(datos))

    # ------------------------------------------------------------- auxiliares
    @staticmethod
    def _numero(texto, descripcion, campo, errores):
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
    def _repetidos(nombres, que, clave, errores):
        vistos = set()
        for k, nombre in enumerate(nombres):
            llave = nombre.strip().lower()
            if llave in vistos:
                errores.append((f"Hay dos {que} con el mismo nombre «{nombre}». Use nombres distintos.",
                                (clave, k)))
            vistos.add(llave)
