"""
controlador/controlador_vogel.py
================================
CONTROLADOR del método de Vogel: valida los datos, aplica Vogel y la prueba
de optimalidad MODI (modelo) y pide a la vista que muestre todo.
"""
from __future__ import annotations

import traceback
from pathlib import Path

from modelo import ErrorArchivo, ErrorValidacion, RepositorioProblemas
from modelo.transporte import OptimizadorMODI, SolverVogel, ValidadorTransporte


class ControladorVogel:
    TIPO = "transporte"

    def __init__(self, vista, repositorio: RepositorioProblemas):
        self.vista = vista
        self.repositorio = repositorio
        self.validador = ValidadorTransporte()
        self.ejemplos: list = []
        vista.establecer_controlador(self)
        self.recargar_ejemplos()

    def recargar_ejemplos(self) -> None:
        self.ejemplos = self.repositorio.listar_ejemplos(self.TIPO)
        self.vista.panel_datos.establecer_ejemplos([titulo for titulo, _ in self.ejemplos])

    # ------------------------------------------------------------ resolver
    def resolver(self) -> None:
        datos = self.vista.panel_datos.obtener_datos()
        # 1) Validación
        try:
            problema = self.validador.validar(datos)
        except ErrorValidacion as error:
            self.vista.mostrar_errores(error.errores)
            return
        # 2) Vogel (solución inicial) y MODI (comparación con el óptimo)
        try:
            resultado = SolverVogel(problema).resolver()
            modi = OptimizadorMODI(resultado).resolver()
        except Exception:
            self.vista.mostrar_mensaje("Error inesperado",
                                       "Ocurrió un error al resolver. Detalle técnico:\n\n" + traceback.format_exc(),
                                       "error")
            return
        # 3) Mostrar
        self.vista.panel_datos.limpiar_errores()
        self.vista.mostrar_resultado(resultado, modi)
        self.vista.avisar_casos(resultado, modi)

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
            self.vista.mostrar_mensaje("Archivo", "Este archivo es de un problema de PROGRAMACIÓN LINEAL. Ábralo en "
                                                  "la sección «Simplex».", "advertencia")
            return
        self.vista.panel_datos.cargar_datos(datos)
        self.vista.seleccionar_datos()
        self.vista.marcar_datos_nuevos()

    def guardar_archivo(self) -> None:
        datos = self.vista.panel_datos.obtener_datos()
        nombre = "".join(c if c.isalnum() else "_" for c in (datos.get("nombre") or "transporte"))[:40] + ".json"
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
