"""Pruebas del método Simplex (maximizar y minimizar) y de sus casos especiales."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modelo import RepositorioProblemas  # noqa: E402
from modelo.caso_especial import DEGENERACION, NO_ACOTADO, OPTIMOS_ALTERNATIVOS  # noqa: E402
from modelo.simplex import SolverSimplex, ValidadorPL  # noqa: E402


def problema(sentido, c, A, b):
    datos = {"sentido": sentido,
             "variables": [{"nombre": f"V{j + 1}", "unidad": "u", "c": str(v)} for j, v in enumerate(c)],
             "restricciones": [{"nombre": f"R{i + 1}", "unidad": "u", "a": [str(x) for x in fila], "b": str(b[i])}
                               for i, fila in enumerate(A)]}
    return ValidadorPL().validar(datos)


def resolver(sentido, c, A, b):
    return SolverSimplex(problema(sentido, c, A, b)).resolver()


class PruebasSimplex(unittest.TestCase):
    def test_maximizar_clasico(self):
        # Max z = 3x1 + 5x2 ; x1 <= 4 ; 2x2 <= 12 ; 3x1 + 2x2 <= 18  ->  x = (2, 6), z = 36
        r = resolver("max", [3, 5], [[1, 0], [0, 2], [3, 2]], [4, 12, 18])
        self.assertEqual(r.estado, "optimo")
        self.assertEqual(r.z, 36)
        self.assertEqual(r.valores_variables(), [2, 6])
        self.assertEqual(r.numero_pivoteos, 2)
        primera = r.iteraciones[0]
        self.assertEqual(primera.tabla.simbolos[primera.columna_entra], "x2")   # entra x2 (mayor Cj - Zj)
        self.assertEqual(primera.tabla.simbolos[primera.tabla.base[primera.fila_sale]], "s2")  # sale s2
        self.assertEqual(primera.pivote, 2)

    def test_minimizar(self):
        # Min z = x1 - 3x2 + 2x3  ->  x = (4, 5, 0), z = -11
        r = resolver("min", [1, -3, 2], [[3, -1, 2], [-2, 4, 0], [-4, 3, 8]], [7, 12, 10])
        self.assertEqual(r.estado, "optimo")
        self.assertEqual(r.z, -11)
        self.assertEqual(r.valores_variables(), [4, 5, 0])

    def test_minimizar_con_costos_positivos_da_origen(self):
        r = resolver("min", [2, 3], [[1, 1], [2, 1]], [10, 15])
        self.assertEqual(r.z, 0)
        self.assertEqual(r.valores_variables(), [0, 0])
        self.assertEqual(len(r.iteraciones), 1)

    def test_no_acotado(self):
        r = resolver("max", [2, 1], [[1, -1], [2, -1]], [10, 40])
        self.assertEqual(r.estado, "no_acotado")
        self.assertIsNone(r.z)
        self.assertIn(NO_ACOTADO, [c.tipo for c in r.casos])

    def test_optimos_alternativos(self):
        r = resolver("max", [2, 4], [[1, 2], [1, 1]], [5, 4])
        self.assertEqual(r.z, 10)
        self.assertIn(OPTIMOS_ALTERNATIVOS, [c.tipo for c in r.casos])
        alternativa = r.solucion_alternativa()
        self.assertIsNotNone(alternativa)
        self.assertNotEqual(alternativa, r.valores_variables())
        self.assertEqual(2 * alternativa[0] + 4 * alternativa[1], 10)          # misma z

    def test_degeneracion(self):
        r = resolver("max", [3, 9], [[1, 4], [1, 2]], [8, 4])
        self.assertEqual(r.z, 18)
        self.assertIn(DEGENERACION, [c.tipo for c in r.casos])
        self.assertTrue(any(it.empate_salida for it in r.iteraciones))

    def test_solucion_cumple_restricciones(self):
        c, A, b = [5, 4, 3], [[2, 3, 1], [4, 1, 2], [3, 4, 2]], [5, 11, 8]
        r = resolver("max", c, A, b)
        x = r.valores_variables()
        self.assertEqual(r.z, 13)
        for fila, limite in zip(A, b):
            self.assertLessEqual(sum(Fraction(a) * v for a, v in zip(fila, x)), limite)

    def test_ejemplos_precargados(self):
        repositorio = RepositorioProblemas()
        esperados = {"01": ("optimo", 86000), "02": ("optimo", -11), "03": ("no_acotado", None),
                     "04": ("optimo", 10), "05": ("optimo", 18), "06": ("optimo", 820)}
        ejemplos = repositorio.listar_ejemplos("simplex")
        self.assertGreaterEqual(len(ejemplos), 3)
        for _, ruta in ejemplos:
            clave = ruta.name[:2]
            if clave not in esperados:
                continue
            with self.subTest(ejemplo=ruta.name):
                r = SolverSimplex(ValidadorPL().validar(repositorio.cargar(ruta))).resolver()
                self.assertEqual((r.estado, r.z), esperados[clave])

    def test_tamano_maximo_8x8(self):
        c = [11, 8, 13, 15, 4, 9, 7, 13]
        A = [[0, 4, 1, 0, 4, 2, 3, 0], [1, 1, 1, 2, 2, 2, 2, 1], [1, 0, 4, 2, 1, 2, 0, 3], [0, 2, 4, 2, 2, 1, 1, 4],
             [0, 4, 1, 1, 2, 3, 1, 2], [4, 2, 0, 4, 2, 2, 0, 1], [0, 0, 1, 2, 0, 3, 0, 1], [1, 4, 1, 0, 1, 0, 2, 2]]
        b = [100, 190, 120, 170, 80, 100, 80, 150]
        r = resolver("max", c, A, b)
        self.assertEqual(r.z, 820)


if __name__ == "__main__":
    unittest.main()
