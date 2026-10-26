"""
Paquete CONTROLADOR recibe las acciones del usuario desde
la vista, usa el modelo para resolver y devuelve los resultados a la vista.
"""
from .controlador_principal import ControladorPrincipal
from .controlador_simplex import ControladorSimplex

__all__ = ["ControladorPrincipal", "ControladorSimplex"]
