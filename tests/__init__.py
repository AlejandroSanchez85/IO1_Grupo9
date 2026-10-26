"""Pruebas automáticas del proyecto (unittest). Ejecutar: python -m unittest discover -s tests -v"""
import sys
from pathlib import Path

# Permite importar los paquetes del proyecto (modelo, vista, controlador) desde cualquier carpeta
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
