"""Pantallas (vista) del método Simplex."""
from .panel_datos_simplex import PanelDatosSimplex
from .panel_iteraciones_simplex import PanelIteracionesSimplex, PanelTodasTablasSimplex
from .panel_resultados_simplex import PanelModeloSimplex, PanelSensibilidad, PanelSolucionSimplex
from .vista_simplex import VistaSimplex

__all__ = ["VistaSimplex", "PanelDatosSimplex", "PanelIteracionesSimplex", "PanelTodasTablasSimplex",
           "PanelModeloSimplex", "PanelSolucionSimplex", "PanelSensibilidad"]
