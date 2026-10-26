"""
vista/reportes/reporte_vogel.py
===============================
Reporte completo de Vogel (texto y HTML): planteamiento, balanceo, cada
paso con penalizaciones, tabla final, costo total, casos especiales y la
prueba de optimalidad MODI.
"""
from __future__ import annotations

from ..explicaciones import textos_transporte as TT
from .utilidades import (avisos_html, bloques_a_html, bloques_a_texto, documento_html, encabezado_texto,
                         seccion_texto, tabla_texto, tabla_transporte_html)


def _tabla_transporte_texto(d: dict) -> str:
    """Tabla de transporte en texto: cada celda muestra 'asignación (costo)'."""
    encabezado = ["Origen \\ Destino"] + list(d["destinos"]) + ["Oferta"]
    tiene_penal = d.get("penal_filas") is not None and d.get("penal_filas") != {}
    if tiene_penal:
        encabezado.append("Penalización")
    if d.get("u") is not None:
        encabezado.append("u_i")
    filas = [encabezado]
    for i, origen in enumerate(d["origenes"]):
        fila = [origen]
        for j in range(len(d["destinos"])):
            centro = (d.get("asignaciones") or {}).get((i, j), (d.get("reducidos") or {}).get((i, j), ""))
            marca = "*" if d.get("celda_elegida") == (i, j) else ""
            fila.append(f"{marca}{centro} ({d['costos'][i][j]})" if centro != "" else f"({d['costos'][i][j]})")
        fila.append(d["oferta"][i] if d.get("oferta") else "")
        if tiene_penal:
            fila.append(d["penal_filas"].get(i, ""))
        if d.get("u") is not None:
            fila.append(d["u"][i])
        filas.append(fila)
    fila = ["Demanda"] + list(d.get("demanda") or [""] * len(d["destinos"])) + [d.get("total") or ""]
    filas.append(fila)
    if tiene_penal:
        filas.append(["Penalización"] + [d["penal_columnas"].get(j, "") for j in range(len(d["destinos"]))] + [""])
    if d.get("v") is not None:
        filas.append(["v_j"] + list(d["v"]) + [""])
    return tabla_texto(filas)


def texto_vogel(resultado, modi, fmt) -> str:
    p = resultado.problema
    partes = [encabezado_texto(f"REPORTE · MÉTODO DE VOGEL · {p.nombre}")]
    partes.append(seccion_texto("1. Planteamiento y balanceo"))
    partes.append(bloques_a_texto(TT.bloques_planteamiento(resultado, fmt)))
    partes.append("\nTabla de costos (" + p.unidad_costo + " por " + p.unidad_producto + ")\n")
    partes.append(_tabla_transporte_texto({**TT.datos_tabla_final(resultado, fmt), "asignaciones": {}}))
    partes.append(seccion_texto("2. Paso a paso de Vogel"))
    for k in range(len(resultado.pasos)):
        partes.append("\n" + _tabla_transporte_texto(TT.datos_tabla_paso(resultado, k, fmt)))
        partes.append("   * = celda escogida en este paso; formato: asignación (costo unitario)\n")
        partes.append(bloques_a_texto(TT.bloques_paso(resultado, k, fmt)))
    partes.append(seccion_texto("3. Tabla final y costo total"))
    partes.append(_tabla_transporte_texto(TT.datos_tabla_final(resultado, fmt)))
    partes.append(bloques_a_texto(TT.bloques_resultado(resultado, fmt)))
    for caso in resultado.casos:
        partes.append(f"\n[{caso.nivel.upper()}] {caso.titulo}\n    {caso.mensaje}\n")
    if modi is not None:
        partes.append(seccion_texto("4. Prueba de optimalidad (MODI) y comparación con el óptimo"))
        for k in range(len(modi.iteraciones)):
            partes.append("\n" + _tabla_transporte_texto(TT.datos_tabla_modi(resultado, modi, k, fmt)))
            partes.append(bloques_a_texto(TT.bloques_modi(resultado, modi, k, fmt)))
        partes.append(f"\nCosto con Vogel = {fmt.num(modi.costo_inicial)} {p.unidad_costo}\n"
                      f"Costo óptimo (MODI) = {fmt.num(modi.costo_optimo)} {p.unidad_costo}\n"
                      f"Diferencia = {fmt.num(modi.ahorro)} {p.unidad_costo}\n")
        for caso in modi.casos:
            partes.append(f"\n[{caso.nivel.upper()}] {caso.titulo}\n    {caso.mensaje}\n")
    return "".join(partes)


def html_vogel(resultado, modi, fmt) -> str:
    p = resultado.problema
    cuerpo = ["<h2>1. Planteamiento y balanceo</h2>", bloques_a_html(TT.bloques_planteamiento(resultado, fmt)),
              tabla_transporte_html({**TT.datos_tabla_final(resultado, fmt), "asignaciones": {}}),
              "<h2>2. Resultado y casos especiales</h2>", avisos_html(resultado.casos),
              tabla_transporte_html(TT.datos_tabla_final(resultado, fmt)),
              bloques_a_html(TT.bloques_resultado(resultado, fmt)), "<h2>3. Paso a paso de Vogel</h2>"]
    for k in range(len(resultado.pasos)):
        cuerpo.append(f"<h3>{TT.titulo_paso(resultado, k)}</h3>")
        cuerpo.append(tabla_transporte_html(TT.datos_tabla_paso(resultado, k, fmt)))
        cuerpo.append(bloques_a_html(TT.bloques_paso(resultado, k, fmt)[1:]))
    if modi is not None:
        cuerpo.append("<h2>4. Prueba de optimalidad (MODI)</h2>")
        cuerpo.append(avisos_html(modi.casos))
        for k in range(len(modi.iteraciones)):
            cuerpo.append(tabla_transporte_html(TT.datos_tabla_modi(resultado, modi, k, fmt)))
            cuerpo.append(bloques_a_html(TT.bloques_modi(resultado, modi, k, fmt)))
    return documento_html(f"Método de Vogel — {p.nombre}", "\n".join(cuerpo))
