"""Pruebas del análisis de sensibilidad calculado desde la tabla óptima."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modelo.simplex import AnalizadorSensibilidad, SolverSimplex  # noqa: E402
from tests.test_simplex import problema  # noqa: E402


class PruebasSensibilidad(unittest.TestCase):
    def setUp(self):
        r = SolverSimplex(problema("max", [3, 5], [[1, 0], [0, 2], [3, 2]], [4, 12, 18])).resolver()
        self.s = AnalizadorSensibilidad(r).analizar()

    def test_precios_sombra(self):
        self.assertEqual(self.s.precios_sombra, [0, Fraction(3, 2), 1])

    def test_dualidad(self):
        self.assertEqual(self.s.z_dual, self.s.z)          # Σ b_i·y_i = z*

    def test_rangos_de_c(self):
        c1, c2 = self.s.rangos_costos
        self.assertEqual((c1.minimo, c1.maximo), (0, Fraction(15, 2)))
        self.assertEqual(c2.minimo, 2)
        self.assertIsNone(c2.maximo)                       # +∞

    def test_rangos_de_b(self):
        b1, b2, b3 = self.s.rangos_recursos
        self.assertEqual(b1.minimo, 2)
        self.assertIsNone(b1.maximo)                       # restricción con holgura: +∞
        self.assertEqual((b2.minimo, b2.maximo), (6, 18))
        self.assertEqual((b3.minimo, b3.maximo), (12, 24))
        self.assertFalse(b1.activa)
        self.assertTrue(b2.activa and b3.activa)

    def test_minimizacion(self):
        r = SolverSimplex(problema("min", [1, -3, 2], [[3, -1, 2], [-2, 4, 0], [-4, 3, 8]], [7, 12, 10])).resolver()
        s = AnalizadorSensibilidad(r).analizar()
        self.assertEqual(s.z_dual, r.z)
        self.assertTrue(all(y <= 0 for y in s.precios_sombra))   # en Min con <= los precios sombra son <= 0

    def test_requiere_optimo(self):
        r = SolverSimplex(problema("max", [2, 1], [[1, -1], [2, -1]], [10, 40])).resolver()
        with self.assertRaises(ValueError):
            AnalizadorSensibilidad(r)


if __name__ == "__main__":
    unittest.main()
