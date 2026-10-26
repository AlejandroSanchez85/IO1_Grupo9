"""Componentes visuales reutilizables (tablas, tarjetas, avisos...)."""
from .tabla_canvas import TablaCanvas
from .widgets import (Aviso, Campo, DesplazableHorizontal, FilaFlexible, Leyenda, MarcoDesplazable, Tarjeta,
                      TextoRico, dibujar_icono, etiqueta, instalar_rueda_global, mostrar_avisos, tabla_desplazable,
                      tarjeta_dato)

__all__ = [
    "TablaCanvas",
    "Aviso", "Campo", "Leyenda", "MarcoDesplazable", "Tarjeta", "TextoRico",
    "dibujar_icono", "etiqueta", "instalar_rueda_global", "mostrar_avisos", "tarjeta_dato",
    "DesplazableHorizontal", "FilaFlexible", "tabla_desplazable",
]
