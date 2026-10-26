"""
Paquete MODELO

Contiene la lógica matemática de los métodos, programada desde cero y SIN
librerías que resuelvan el problema (no se usa SciPy, PuLP, OR-Tools, etc.).
No depende de la interfaz gráfica: puede probarse solo (carpeta tests/).
"""
from .caso_especial import CasoEspecial
from .excepciones import ErrorArchivo, ErrorValidacion
from .numeros import ValorM, convertir_costo, convertir_numero, texto_numero
from .repositorio import RepositorioProblemas
from .simplex import (AnalizadorSensibilidad, ProblemaPL, ResultadoSensibilidad, ResultadoSimplex,
                      SolverSimplex, ValidadorPL)

__all__ = [
    "CasoEspecial", "ErrorArchivo", "ErrorValidacion", "ValorM", "convertir_numero",
    "convertir_costo", "texto_numero", "RepositorioProblemas", "ProblemaPL", "ValidadorPL",
    "SolverSimplex", "ResultadoSimplex", "AnalizadorSensibilidad", "ResultadoSensibilidad",
]
