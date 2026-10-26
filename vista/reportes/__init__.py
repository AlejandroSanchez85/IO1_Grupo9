"""Generación de reportes en texto y HTML (para el informe)."""
from .reporte_simplex import html_simplex, texto_simplex
from .reporte_vogel import html_vogel, texto_vogel

__all__ = ["texto_simplex", "html_simplex", "texto_vogel", "html_vogel"]
