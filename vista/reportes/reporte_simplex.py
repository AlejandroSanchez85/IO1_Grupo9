"""
vista/reportes/reporte_simplex.py
=================================
Reporte completo del Simplex (texto y HTML): modelo, todas las tablas con
su explicación, solución final, casos especiales y sensibilidad.
"""
from __future__ import annotations

import html

from ..explicaciones import textos_sensibilidad as TSe
from ..explicaciones import textos_simplex as TS
from .utilidades import (avisos_html, bloques_a_html, bloques_a_texto, documento_html, encabezado_texto,
                         seccion_texto, tabla_html, tabla_texto)


def _iteraciones(resultado):
    elementos = list(resultado.iteraciones)
    if resultado.iteracion_alternativa is not None:
        elementos.append(resultado.iteracion_alternativa)
    return elementos


def _filas_sensibilidad(s, fmt):
    p = s.problema
    recursos = [["Restricción", "Holgura", "Estado", f"Precio sombra ({p.unidad_z}/unidad)", "b actual",
                 "Disminución", "Aumento", "b mín", "b máx", "Unidad"]]
    for rr in s.rangos_recursos:
        recursos.append([rr.nombre, fmt.num(rr.holgura), "Activa" if rr.activa else "No activa",
                         fmt.num(rr.precio_sombra), fmt.num(rr.valor_actual), fmt.cambio(rr.disminucion),
                         fmt.cambio(rr.aumento), fmt.limite_inferior(rr.minimo), fmt.limite_superior(rr.maximo),
                         rr.unidad])
    variables = [["Variable", "Nombre", "Valor", "Costo reducido", "c actual", "Disminución", "Aumento", "c mín",
                  "c máx", "Tipo"]]
    for rc in s.rangos_costos:
        variables.append([rc.simbolo, rc.nombre, fmt.num(rc.valor_variable), fmt.num(rc.costo_reducido),
                          fmt.num(rc.valor_actual), fmt.cambio(rc.disminucion), fmt.cambio(rc.aumento),
                          fmt.limite_inferior(rc.minimo), fmt.limite_superior(rc.maximo),
                          "Básica" if rc.es_basica else "No básica"])
    return recursos, variables


def texto_simplex(resultado, sensibilidad, fmt) -> str:
    p = resultado.problema
    partes = [encabezado_texto(f"REPORTE · MÉTODO SIMPLEX ({'MAXIMIZAR' if p.es_max else 'MINIMIZAR'}) · {p.nombre}")]
    partes.append(seccion_texto("1. Modelo matemático"))
    partes.append(bloques_a_texto(TS.bloques_modelo(p, fmt)))
    partes.append(seccion_texto("2. Paso a paso (todas las tablas)"))
    for k, it in enumerate(_iteraciones(resultado)):
        indice = min(k, len(resultado.iteraciones) - 1)
        datos = TS.datos_tabla(resultado, indice, fmt, it)
        filas = [list(f) for f in datos["filas"]]
        if it.columna_entra is not None and it.fila_sale is not None:
            fila, col = 2 + it.fila_sale, 2 + it.columna_entra
            filas[fila][col] = f"[{filas[fila][col]}]"
        partes.append(f"\n{TS.titulo_iteracion(resultado, indice, it)}\n")
        partes.append(tabla_texto(filas, filas_encabezado=2))
        if it.columna_entra is not None and it.fila_sale is not None:
            partes.append("   [ ] = elemento pivote\n")
        partes.append(bloques_a_texto(TS.bloques_iteracion(resultado, indice, fmt, it)))
    partes.append(seccion_texto("3. Resultado final y casos especiales"))
    if resultado.es_optimo:
        partes.append(TS.texto_plan(resultado, fmt) + "\n")
        partes.append(bloques_a_texto(TS.bloques_resumen_optimo(resultado, fmt)))
        partes.append("\n" + bloques_a_texto(TS.bloques_comprobacion(resultado, fmt)))
    for caso in resultado.casos:
        partes.append(f"\n[{caso.nivel.upper()}] {caso.titulo}\n    {caso.mensaje}\n")
    if sensibilidad is not None:
        partes.append(seccion_texto("4. Análisis de sensibilidad"))
        recursos, variables = _filas_sensibilidad(sensibilidad, fmt)
        partes.append("Precios sombra y rangos de b_i\n" + tabla_texto(recursos))
        partes.append("\nCostos reducidos y rangos de c_j\n" + tabla_texto(variables))
        partes.append("\n" + bloques_a_texto(TSe.bloques_interpretacion(sensibilidad, fmt)))
        partes.append("\n" + bloques_a_texto(TSe.bloques_calculos(sensibilidad, fmt)))
        for caso in sensibilidad.casos:
            partes.append(f"\n[{caso.nivel.upper()}] {caso.titulo}\n    {caso.mensaje}\n")
    return "".join(partes)


def html_simplex(resultado, sensibilidad, fmt) -> str:
    p = resultado.problema
    cuerpo = ["<h2>1. Modelo matemático</h2>", bloques_a_html(TS.bloques_modelo(p, fmt)),
              "<h2>2. Resultado y casos especiales</h2>"]
    if resultado.es_optimo:
        cuerpo.append(f'<div class="aviso exito"><b>Solución óptima</b><span>{html.escape(TS.texto_plan(resultado, fmt))}'
                      f'</span></div>')
    cuerpo.append(avisos_html(resultado.casos))
    cuerpo.append("<h2>3. Paso a paso (todas las tablas)</h2>")
    for k, it in enumerate(_iteraciones(resultado)):
        indice = min(k, len(resultado.iteraciones) - 1)
        datos = TS.datos_tabla(resultado, indice, fmt, it)
        cuerpo.append(f"<h3>{html.escape(TS.titulo_iteracion(resultado, indice, it))}</h3>")
        cuerpo.append(tabla_html(datos["filas"], datos["estilos"], datos["filas_encabezado"],
                                 datos["columnas_encabezado"], datos["estilos_fila"]))
        cuerpo.append(bloques_a_html(TS.bloques_iteracion(resultado, indice, fmt, it)[1:]))
    if resultado.es_optimo:
        cuerpo.append("<h2>4. Comprobación</h2>")
        cuerpo.append(bloques_a_html(TS.bloques_comprobacion(resultado, fmt)))
    if sensibilidad is not None:
        recursos, variables = _filas_sensibilidad(sensibilidad, fmt)
        cuerpo.append("<h2>5. Análisis de sensibilidad</h2>")
        cuerpo.append(avisos_html(sensibilidad.casos))
        cuerpo.append("<h3>Precios sombra y rangos de b_i</h3>" + tabla_html(recursos))
        cuerpo.append("<h3>Costos reducidos y rangos de c_j</h3>" + tabla_html(variables))
        cuerpo.append(bloques_a_html(TSe.bloques_interpretacion(sensibilidad, fmt)))
        cuerpo.append(bloques_a_html(TSe.bloques_calculos(sensibilidad, fmt)))
    return documento_html(f"Método Simplex — {p.nombre}", "\n".join(cuerpo))
