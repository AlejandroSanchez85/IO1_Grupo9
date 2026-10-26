"""
modelo/caso_especial.py
=======================
Representa un caso especial detectado por un método (no acotado, óptimos
alternativos, degeneración, desbalance, empates, ruta prohibida, etc.).
La vista lo muestra como un aviso de color con un mensaje claro.
"""
from __future__ import annotations

from dataclasses import dataclass

# Tipos de caso especial
NO_ACOTADO = "no_acotado"
OPTIMOS_ALTERNATIVOS = "optimos_alternativos"
DEGENERACION = "degeneracion"
EMPATE = "empate"
CICLAJE = "ciclaje"
DESBALANCE = "desbalance"
RUTA_PROHIBIDA = "ruta_prohibida"
INFACTIBLE = "infactible"
INFORMATIVO = "informativo"

# Niveles (color del aviso en la vista)
NIVEL_ERROR = "error"
NIVEL_ADVERTENCIA = "advertencia"
NIVEL_INFO = "info"
NIVEL_EXITO = "exito"


@dataclass(frozen=True)
class CasoEspecial:
    tipo: str
    titulo: str
    mensaje: str
    nivel: str = NIVEL_ADVERTENCIA
