"""
controlador/controlador_principal.py
====================================
Crea la ventana principal, conecta cada vista con su controlador y define
los atajos de teclado.
"""
from __future__ import annotations

from modelo import RepositorioProblemas
from vista import VentanaPrincipal

from .controlador_simplex import ControladorSimplex


class ControladorPrincipal:
    def __init__(self):
        self.ventana = VentanaPrincipal()
        self.repositorio = RepositorioProblemas()
        self.simplex = ControladorSimplex(self.ventana.vista_simplex, self.repositorio)
        raiz = self.ventana.raiz
        raiz.bind_all("<Control-Return>", lambda e: self.resolver_actual())
        raiz.bind_all("<F5>", lambda e: self.resolver_actual())
        raiz.bind_all("<F1>", lambda e: self.ventana.mostrar("ayuda"))

    def resolver_actual(self) -> None:
        if self.ventana.actual == "simplex":
            self.simplex.resolver()


    def iniciar(self) -> None:
        self.ventana.mostrar("inicio")
        self.ventana.iniciar()
