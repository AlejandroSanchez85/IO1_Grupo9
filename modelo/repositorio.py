"""
modelo/repositorio.py
=====================
Lectura y escritura de problemas en archivos JSON.

Los datos de los problemas NUNCA van escritos dentro del código: los
ejemplos precargados están en la carpeta ``ejemplos/`` (archivos .json) y
el usuario puede guardar y abrir sus propios problemas.
"""
from __future__ import annotations

import json
from pathlib import Path

from .excepciones import ErrorArchivo

CARPETA_EJEMPLOS = Path(__file__).resolve().parent.parent / "ejemplos"


class RepositorioProblemas:
    """Administra los archivos JSON de problemas (ejemplos y del usuario)."""

    def __init__(self, carpeta_base: Path | None = None):
        self.carpeta_base = Path(carpeta_base) if carpeta_base else CARPETA_EJEMPLOS

    def carpeta(self, tipo: str) -> Path:
        """Carpeta de ejemplos de un tipo: 'simplex' o 'transporte'."""
        return self.carpeta_base / tipo

    def listar_ejemplos(self, tipo: str) -> list[tuple[str, Path]]:
        """Lista (título, ruta) de los ejemplos .json de un tipo, ordenados por nombre."""
        carpeta = self.carpeta(tipo)
        if not carpeta.is_dir():
            return []
        ejemplos = []
        for ruta in sorted(carpeta.glob("*.json")):
            try:
                datos = self.cargar(ruta)
            except ErrorArchivo:
                continue                       # un archivo dañado no detiene el programa
            if datos.get("tipo") not in (None, tipo):
                continue
            titulo = str(datos.get("titulo") or datos.get("nombre") or ruta.stem)
            ejemplos.append((titulo, ruta))
        return ejemplos

    @staticmethod
    def cargar(ruta) -> dict:
        """Lee un archivo JSON y devuelve un diccionario con los datos."""
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            raise ErrorArchivo(f"No se encontró el archivo:\n{ruta}")
        except json.JSONDecodeError as error:
            raise ErrorArchivo(f"El archivo no es un JSON válido (línea {error.lineno}):\n{ruta}")
        except (OSError, UnicodeDecodeError) as error:
            raise ErrorArchivo(f"No se pudo leer el archivo:\n{ruta}\n{error}")
        if not isinstance(datos, dict):
            raise ErrorArchivo("El archivo no contiene un problema válido (se esperaba un objeto JSON).")
        return datos

    @staticmethod
    def guardar(ruta, datos: dict) -> None:
        """Guarda los datos del problema en un archivo JSON (UTF-8, legible)."""
        try:
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
        except OSError as error:
            raise ErrorArchivo(f"No se pudo guardar el archivo:\n{ruta}\n{error}")
