"""Pruebas del método de Vogel y de la prueba de optimalidad MODI."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modelo import RepositorioProblemas  # noqa: E402
from modelo.caso_especial import DEGENERACION, DESBALANCE, EMPATE, INFACTIBLE  # noqa: E402
from modelo.transporte import OptimizadorMODI, SolverVogel, ValidadorTransporte  # noqa: E402


def transporte(oferta, demanda, costos):
    datos = {"origenes": [{"nombre": f"O{i + 1}", "oferta": str(s)} for i, s in enumerate(oferta)],
             "destinos": [{"nombre": f"D{j + 1}", "demanda": str(d)} for j, d in enumerate(demanda)],
             "costos": [[str(c) for c in fila] for fila in costos]}
    return SolverVogel(ValidadorTransporte().validar(datos)).resolver()


CLASICO = ([15, 25, 10], [5, 15, 15, 15], [[10, 2, 20, 11], [12, 7, 9, 20], [4, 14, 16, 18]])


class PruebasVogel(unittest.TestCase):
    def verificar_base(self, r):
        """La solución debe ser factible y tener m + n − 1 variables básicas."""
        self.assertEqual(len(r.asignaciones), r.m + r.n - 1)
        for i in range(r.m):
            self.assertEqual(sum(x for (a, _), x in r.asignaciones.items() if a == i), r.oferta[i])
        for j in range(r.n):
            self.assertEqual(sum(x for (_, b), x in r.asignaciones.items() if b == j), r.demanda[j])

    def test_problema_clasico(self):
        r = transporte(*CLASICO)
        self.assertEqual(r.costo_total, 475)            # costo inicial de Vogel
        self.verificar_base(r)
        primer_paso = r.pasos[0]
        self.assertEqual(primer_paso.penalizaciones_filas[0].penalizacion, 8)    # fila 1: 10 - 2
        self.assertEqual(primer_paso.penalizaciones_columnas[0].penalizacion, 6)  # columna 1: 10 - 4

    def test_modi_llega_al_optimo(self):
        r = transporte(*CLASICO)
        modi = OptimizadorMODI(r).resolver()
        self.assertEqual(modi.estado, "optimo")
        self.assertEqual(modi.costo_optimo, 435)
        self.assertTrue(modi.costo_optimo <= r.costo_total)

    def test_sobra_oferta_agrega_destino_ficticio(self):
        r = transporte([120, 80, 100], [90, 110, 60], [[8, 6, 10], [9, 12, 13], [14, 9, 16]])
        self.assertEqual(r.ficticio, "destino")
        self.assertEqual(r.demanda[-1], 40)
        self.assertIn(DESBALANCE, [c.tipo for c in r.casos])
        self.verificar_base(r)

    def test_falta_oferta_agrega_origen_ficticio(self):
        r = transporte([70, 50, 60], [60, 70, 40, 50], [[5, 8, 6, 7], [6, 4, 9, 5], [7, 6, 5, 8]])
        self.assertEqual(r.ficticio, "origen")
        self.assertEqual(r.oferta[-1], 40)
        self.verificar_base(r)

    def test_empates_y_degeneracion(self):
        r = transporte([20, 30, 25], [20, 30, 25], [[2, 3, 4], [3, 2, 1], [4, 1, 2]])
        tipos = [c.tipo for c in r.casos]
        self.assertIn(EMPATE, tipos)
        self.assertIn(DEGENERACION, tipos)
        self.assertTrue(r.celdas_cero)
        self.verificar_base(r)

    def test_infactible_por_rutas_prohibidas(self):
        r = transporte([30, 40, 30], [30, 30, 40], [[4, 6, 5], [3, 5, "M"], [6, 2, "M"]])
        modi = OptimizadorMODI(r).resolver()
        self.assertIn(INFACTIBLE, [c.tipo for c in modi.casos])

    def test_ejemplos_precargados(self):
        repositorio = RepositorioProblemas()
        ejemplos = repositorio.listar_ejemplos("transporte")
        self.assertGreaterEqual(len(ejemplos), 3)
        for _, ruta in ejemplos:
            with self.subTest(ejemplo=ruta.name):
                r = SolverVogel(ValidadorTransporte().validar(repositorio.cargar(ruta))).resolver()
                self.verificar_base(r)
                modi = OptimizadorMODI(r).resolver()
                self.assertTrue(modi.costo_optimo <= r.costo_total)


if __name__ == "__main__":
    unittest.main()
