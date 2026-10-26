"""
Paquete VISTA todo lo que se ve en pantalla.
No contiene la matemática de los métodos (está en modelo/).
"""
from .formato import FORMATO, FormatoNumeros
from .simplex import VistaSimplex
from .tema import COLORES, FUENTES, aplicar_tema
from .ventana_principal import VentanaPrincipal
from .vista_ayuda import VistaAyuda
from .vista_inicio import VistaInicio

__all__ = ["FORMATO", "FormatoNumeros", "COLORES", "FUENTES", "aplicar_tema", "VentanaPrincipal", "VistaInicio",
           "VistaSimplex", "VistaAyuda"]
