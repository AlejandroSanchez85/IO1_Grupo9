"""Pantallas (vista) del método de Vogel y de la prueba MODI."""
from .panel_datos_vogel import PanelDatosVogel
from .panel_pasos_vogel import PanelPasosVogel, PanelTodosPasosVogel
from .panel_resultados_vogel import PanelModi, PanelPlanteamientoVogel, PanelSolucionVogel
from .vista_vogel import VistaVogel

__all__ = ["VistaVogel", "PanelDatosVogel", "PanelPasosVogel", "PanelTodosPasosVogel", "PanelPlanteamientoVogel",
           "PanelSolucionVogel", "PanelModi"]
