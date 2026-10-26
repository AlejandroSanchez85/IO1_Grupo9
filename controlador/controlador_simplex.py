"""
controlador/controlador_simplex.py
==================================
CONTROLADOR del Simplex recibe las acciones de la vista
(resolver, cargar ejemplo, abrir, guardar, limpiar), llama al modelo y le
pide a la vista que muestre los resultados o los errores.
"""
from __future__ import annotations

import traceback
from pathlib import Path

from modelo import ErrorArchivo, ErrorValidacion, RepositorioProblemas
from modelo.simplex import AnalizadorSensibilidad, SolverSimplex, ValidadorPL


class ControladorSimplex:
    TIPO = "simplex"

    def __init__(self, vista, repositorio: RepositorioProblemas):
        self.vista = vista
        self.repositorio = repositorio
        self.validador = ValidadorPL()
        self.ejemplos: list = []
        vista.establecer_controlador(self)
        self.recargar_ejemplos()

    def recargar_ejemplos(self) -> None:
        self.ejemplos = self.repositorio.listar_ejemplos(self.TIPO)
        self.vista.panel_datos.establecer_ejemplos([titulo for titulo, _ in self.ejemplos])

    # ------------------------------------------------------------ resolver
    def resolver(self) -> None:
        datos = self.vista.panel_datos.obtener_datos()
        # 1) Validación de los datos ingresados
        try:
            problema = self.validador.validar(datos)
        except ErrorValidacion as error:
            self.vista.mostrar_errores(error.errores)
            return
        # 2) Método Simplex y análisis de sensibilidad (modelo)
        try:
            resultado = SolverSimplex(problema).resolver()
            sensibilidad = AnalizadorSensibilidad(resultado).analizar() if resultado.es_optimo else None
        except Exception:                                  # error inesperado: se informa sin cerrar
            self.vista.mostrar_mensaje("Error inesperado",
                                       "Ocurrió un error al resolver. Detalle técnico:\n\n" + traceback.format_exc(),
                                       "error")
            return
        # 3) Mostrar resultados
        self.vista.panel_datos.limpiar_errores()
        self.vista.mostrar_resultado(resultado, sensibilidad)
        self.vista.avisar_casos(resultado)

    # ---------------------------------------------------- ejemplos y archivos
    def cargar_ejemplo(self, indice) -> None:
        if indice is None or not 0 <= indice < len(self.ejemplos):
            self.vista.mostrar_mensaje("Ejemplos", "Seleccione primero un ejemplo de la lista.", "advertencia")
            return
        self._cargar_ruta(self.ejemplos[indice][1])

    def abrir_archivo(self) -> None:
        ruta = self.vista.pedir_archivo_abrir(self.repositorio.carpeta(self.TIPO))
        if ruta:
            self._cargar_ruta(ruta)

    def _cargar_ruta(self, ruta) -> None:
        try:
            datos = self.repositorio.cargar(ruta)
        except ErrorArchivo as error:
            self.vista.mostrar_mensaje("Archivo", str(error), "error")
            return
        if datos.get("tipo") not in (None, self.TIPO):
            self.vista.mostrar_mensaje("Archivo", "Este archivo es de un problema de TRANSPORTE, no de Programación Lineal.", "advertencia")
            return
        self.vista.panel_datos.cargar_datos(datos)
        self.vista.seleccionar_datos()
        self.vista.marcar_datos_nuevos()

    def guardar_archivo(self) -> None:
        datos = self.vista.panel_datos.obtener_datos()
        nombre = "".join(c if c.isalnum() else "_" for c in (datos.get("nombre") or "problema"))[:40] + ".json"
        ruta = self.vista.pedir_archivo_guardar(self.repositorio.carpeta(self.TIPO), nombre)
        if not ruta:
            return
        try:
            self.repositorio.guardar(ruta, datos)
        except ErrorArchivo as error:
            self.vista.mostrar_mensaje("Archivo", str(error), "error")
            return
        if Path(ruta).resolve().parent == self.repositorio.carpeta(self.TIPO).resolve():
            self.recargar_ejemplos()
        self.vista.mostrar_mensaje("Archivo", f"Problema guardado en:\n{ruta}")

    def limpiar(self) -> None:
        if self.vista.confirmar("Limpiar", "¿Desea borrar todos los datos del formulario?"):
            self.vista.panel_datos.limpiar_formulario()
            self.vista.marcar_datos_nuevos()
