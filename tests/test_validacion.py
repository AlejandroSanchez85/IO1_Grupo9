"""Pruebas de la validación de datos: campos vacíos, texto en vez de números y datos imposibles."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modelo import ErrorValidacion  # noqa: E402
from modelo.simplex import ValidadorPL  # noqa: E402
from modelo.transporte import ValidadorTransporte  # noqa: E402


def datos_pl(**cambios):
    datos = {"sentido": "max", "variables": [{"nombre": "A", "c": "3"}, {"nombre": "B", "c": "5"}],
             "restricciones": [{"nombre": "R1", "a": ["1", "0"], "b": "4"},
                               {"nombre": "R2", "a": ["0", "2"], "b": "12"}]}
    datos.update(cambios)
    return datos


class PruebasValidacionPL(unittest.TestCase):
    def campos_con_error(self, datos):
        with self.assertRaises(ErrorValidacion) as contexto:
            ValidadorPL().validar(datos)
        return contexto.exception.campos

    def test_datos_correctos(self):
        p = ValidadorPL().validar(datos_pl())
        self.assertEqual((p.n, p.m), (2, 2))

    def test_campo_vacio_y_texto(self):
        datos = datos_pl()
        datos["variables"][0]["c"] = ""
        datos["restricciones"][1]["a"][0] = "abc"
        campos = self.campos_con_error(datos)
        self.assertIn(("c", 0), campos)
        self.assertIn(("a", 1, 0), campos)

    def test_b_negativo(self):
        datos = datos_pl()
        datos["restricciones"][0]["b"] = "-4"
        self.assertIn(("b", 0), self.campos_con_error(datos))

    def test_tamano_maximo(self):
        datos = datos_pl(variables=[{"nombre": f"V{k}", "c": "1"} for k in range(9)])
        self.assertIn(("n",), self.campos_con_error(datos))

    def test_nombres_repetidos(self):
        datos = datos_pl()
        datos["variables"][1]["nombre"] = "a"
        self.assertIn(("nombre_var", 1), self.campos_con_error(datos))

    def test_signo_no_permitido(self):
        datos = datos_pl()
        datos["restricciones"][0]["signo"] = ">="
        self.assertIn(("signo", 0), self.campos_con_error(datos))


class PruebasValidacionTransporte(unittest.TestCase):
    def base(self):
        return {"origenes": [{"nombre": "O1", "oferta": "10"}, {"nombre": "O2", "oferta": "20"}],
                "destinos": [{"nombre": "D1", "demanda": "15"}, {"nombre": "D2", "demanda": "15"}],
                "costos": [["4", "6"], ["5", "M"]]}

    def test_datos_correctos(self):
        p = ValidadorTransporte().validar(self.base())
        self.assertTrue(p.esta_balanceado)
        self.assertEqual(p.rutas_prohibidas(), [(1, 1)])

    def test_errores(self):
        datos = self.base()
        datos["origenes"][0]["oferta"] = "-1"
        datos["destinos"][1]["demanda"] = ""
        datos["costos"][0][1] = "x"
        with self.assertRaises(ErrorValidacion) as contexto:
            ValidadorTransporte().validar(datos)
        campos = contexto.exception.campos
        self.assertIn(("oferta", 0), campos)
        self.assertIn(("demanda", 1), campos)
        self.assertIn(("costo", 0, 1), campos)

    def test_oferta_total_cero(self):
        datos = self.base()
        datos["origenes"][0]["oferta"] = "0"
        datos["origenes"][1]["oferta"] = "0"
        with self.assertRaises(ErrorValidacion):
            ValidadorTransporte().validar(datos)


if __name__ == "__main__":
    unittest.main()
