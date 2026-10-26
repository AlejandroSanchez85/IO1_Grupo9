"""Componentes visuales reutilizables (tablas, gráficas, tarjetas, avisos...)."""
from .graficas import DiagramaRed, GraficoBarras, GraficoLineas, escala_bonita, texto_compacto
from .tabla_canvas import TablaCanvas
from .tabla_transporte import TablaTransporteCanvas
from .widgets import (Aviso, Campo, DesplazableHorizontal, FilaFlexible, Leyenda, MarcoDesplazable, Tarjeta,
                      TextoRico, dibujar_icono, etiqueta, instalar_rueda_global, mostrar_avisos, tabla_desplazable,
                      tarjeta_dato)

__all__ = [
    "DiagramaRed", "GraficoBarras", "GraficoLineas", "escala_bonita", "texto_compacto", "TablaCanvas",
    "TablaTransporteCanvas", "Aviso", "Campo", "Leyenda", "MarcoDesplazable", "Tarjeta", "TextoRico",
    "dibujar_icono", "etiqueta", "instalar_rueda_global", "mostrar_avisos", "tarjeta_dato",
    "DesplazableHorizontal", "FilaFlexible", "tabla_desplazable",
]
