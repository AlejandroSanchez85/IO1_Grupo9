"""Pruebas de la conversión de números escritos por el usuario y de la clase ValorM (costo M)."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modelo.numeros import ValorM, convertir_costo, convertir_numero  # noqa: E402


class PruebasConversion(unittest.TestCase):
    def test_formatos_validos(self):
        self.assertEqual(convertir_numero("12"), 12)
        self.assertEqual(convertir_numero(" -7 "), -7)
        self.assertEqual(convertir_numero("2,5"), Fraction(5, 2))
        self.assertEqual(convertir_numero("2.5"), Fraction(5, 2))
        self.assertEqual(convertir_numero("3/4"), Fraction(3, 4))
        self.assertEqual(convertir_numero("1e3"), 1000)
        self.assertEqual(convertir_numero("−3"), -3)          # signo menos tipográfico
        self.assertEqual(convertir_numero(0.1), Fraction(1, 10))
        self.assertEqual(convertir_numero("0.1") + convertir_numero("0.2"), Fraction(3, 10))

    def test_formatos_invalidos(self):
        for texto in ("", "   ", "abc", "1.250.000", "1,5.2", "3/0", "inf", "nan", "2/", "1e", "--3"):
            with self.subTest(texto=texto):
                with self.assertRaises(ValueError):
                    convertir_numero(texto)


class PruebasValorM(unittest.TestCase):
    def test_orden_lexicografico(self):
        M = ValorM(0, 1)
        self.assertTrue(M > 10 ** 9)
        self.assertTrue(M - 5 < M)
        self.assertTrue(2 * M > M + 1000)
        self.assertEqual((M + 3) - (M - 2), 5)

    def test_convertir_costo(self):
        self.assertTrue(convertir_costo("M").tiene_m)
        self.assertTrue(convertir_costo("m").tiene_m)
        self.assertEqual(convertir_costo("7"), 7)
        with self.assertRaises(ValueError):
            convertir_costo("X")


if __name__ == "__main__":
    unittest.main()
