"""
vista/reportes/utilidades.py
============================
Funciones para convertir tablas y explicaciones en texto plano o HTML.
"""
from __future__ import annotations

import html
from datetime import datetime

from ..tema import COLORES


def bloques_a_texto(bloques) -> str:
    return "".join(texto for texto, _ in bloques)


def tabla_texto(filas, filas_encabezado: int = 1) -> str:
    """Tabla en texto con bordes, para el reporte .txt."""
    filas = [[("" if c is None else str(c)).replace("\n", " ") for c in fila] for fila in filas]
    columnas = max(len(f) for f in filas)
    for fila in filas:
        fila.extend([""] * (columnas - len(fila)))
    anchos = [max(len(f[c]) for f in filas) for c in range(columnas)]
    separador = "+" + "+".join("-" * (a + 2) for a in anchos) + "+"
    lineas = [separador]
    for k, fila in enumerate(filas):
        lineas.append("| " + " | ".join(fila[c].center(anchos[c]) for c in range(columnas)) + " |")
        if k == filas_encabezado - 1:
            lineas.append(separador.replace("-", "="))
    lineas.append(separador)
    return "\n".join(lineas) + "\n"


_CLASES = {"titulo": "titulo", "subtitulo": "subtitulo", "negrita": "negrita", "suave": "suave",
           "pequena": "suave", "formula": "formula", "exito": "exito", "error": "error",
           "advertencia": "advertencia", "info": "info", "entra": "entra", "sale": "sale", "pivote": "pivote",
           "resaltado": "resaltado", "alternativo": "alternativo", "vineta": "vineta", "mono": "formula"}


def bloques_a_html(bloques) -> str:
    partes = []
    for texto, etiquetas in bloques:
        if isinstance(etiquetas, str):
            etiquetas = (etiquetas,) if etiquetas else ()
        clases = " ".join(_CLASES[e] for e in etiquetas if e in _CLASES)
        contenido = html.escape(texto)
        partes.append(f'<span class="{clases}">{contenido}</span>' if clases else contenido)
    return f'<div class="explicacion">{"".join(partes)}</div>'


def tabla_html(filas, estilos=None, filas_encabezado: int = 1, columnas_encabezado: int = 1,
               estilos_fila=None, estilos_columna=None) -> str:
    """Tabla HTML con los mismos colores que la TablaCanvas de la pantalla."""
    estilos, estilos_fila, estilos_columna = estilos or {}, estilos_fila or {}, estilos_columna or {}
    lineas = ['<table class="tabla">']
    for r, fila in enumerate(filas):
        lineas.append("<tr>")
        for c, valor in enumerate(fila):
            if r < filas_encabezado:
                estilo = {"bg": COLORES["tabla_encabezado"], "fg": "#FFFFFF", "negrita": True}
            elif c < columnas_encabezado:
                estilo = {"bg": COLORES["tabla_lateral"], "fg": COLORES["texto"], "negrita": True}
            else:
                estilo = {"bg": "#FFFFFF", "fg": COLORES["texto"], "negrita": False}
            if r >= filas_encabezado:
                if c in estilos_columna and c >= columnas_encabezado:
                    estilo.update(estilos_columna[c])
                if r in estilos_fila:
                    estilo.update(estilos_fila[r])
            estilo.update(estilos.get((r, c), {}))
            css = f"background:{estilo['bg']};color:{estilo['fg']};" + ("font-weight:bold;" if estilo.get("negrita") else "")
            texto = html.escape("" if valor is None else str(valor)).replace("\n", "<br>")
            lineas.append(f'<td style="{css}">{texto}</td>')
        lineas.append("</tr>")
    lineas.append("</table>")
    return "\n".join(lineas)


def tabla_transporte_html(d: dict) -> str:
    """Tabla de transporte (costo en la esquina y asignación al centro) en HTML."""
    c = COLORES
    m, n = len(d["origenes"]), len(d["destinos"])
    asignaciones = d.get("asignaciones") or {}
    reducidos = d.get("reducidos") or {}
    penal_f, penal_c = d.get("penal_filas"), d.get("penal_columnas")
    filas_t, columnas_t = set(d.get("filas_tachadas") or ()), set(d.get("columnas_tachadas") or ())
    ciclo = list(d.get("ciclo") or [])
    signos = {celda: ("+" if k % 2 == 0 else "−") for k, celda in enumerate(ciclo)}
    lineas = ['<table class="tabla transporte"><tr><th>Origen \\ Destino</th>']
    lineas += [f"<th>{html.escape(x)}</th>" for x in d["destinos"]] + ["<th>Oferta</th>"]
    if penal_f is not None:
        lineas.append("<th>Penalización</th>")
    if d.get("u") is not None:
        lineas.append("<th>u_i</th>")
    lineas.append("</tr>")
    for i in range(m):
        lineas.append(f'<tr><th class="rotulo">{html.escape(d["origenes"][i])}</th>')
        for j in range(n):
            celda = (i, j)
            if d.get("celda_elegida") == celda:
                fondo, color = c["elegida"], "#FFFFFF"
            elif i in filas_t or j in columnas_t:
                fondo, color = c["tachado"], c["tachado_texto"]
            elif celda in asignaciones:
                fondo, color = c["asignada"], c["texto"]
            elif d.get("linea_resaltada") in (("fila", i), ("columna", j)):
                fondo, color = c["linea_elegida"], c["texto"]
            elif celda in (d.get("prohibidas") or ()):
                fondo, color = c["prohibida"], c["texto"]
            elif i == d.get("fila_ficticia") or j == d.get("columna_ficticia"):
                fondo, color = c["ficticio"], c["texto"]
            else:
                fondo, color = "#FFFFFF", c["texto"]
            centro = asignaciones.get(celda, reducidos.get(celda, ""))
            signo = f'<span class="signo">{signos[celda]}</span>' if celda in signos else ""
            lineas.append(f'<td style="background:{fondo};color:{color}">{signo}<span class="costo">'
                          f'{html.escape(d["costos"][i][j])}</span><div class="asig">{html.escape(centro)}</div></td>')
        oferta = d["oferta"][i] if d.get("oferta") else ""
        lineas.append(f"<td class='lateral'>{html.escape(oferta)}</td>")
        if penal_f is not None:
            resaltada = d.get("penal_resaltada") == ("fila", i)
            lineas.append(f"<td class='{'penal-max' if resaltada else 'penal'}'>{html.escape(penal_f.get(i, ''))}</td>")
        if d.get("u") is not None:
            lineas.append(f"<td class='potencial'>{html.escape(d['u'][i])}</td>")
        lineas.append("</tr>")
    lineas.append("<tr><th class='rotulo'>Demanda</th>")
    for j in range(n):
        lineas.append(f"<td class='lateral'>{html.escape(d['demanda'][j] if d.get('demanda') else '')}</td>")
    lineas.append(f"<td class='lateral'>{html.escape(d.get('total') or '')}</td>")
    if penal_f is not None:
        lineas.append("<td></td>")
    if d.get("u") is not None:
        lineas.append("<td></td>")
    lineas.append("</tr>")
    if penal_c is not None:
        lineas.append("<tr><th class='rotulo'>Penalización</th>")
        for j in range(n):
            resaltada = d.get("penal_resaltada") == ("columna", j)
            lineas.append(f"<td class='{'penal-max' if resaltada else 'penal'}'>{html.escape(penal_c.get(j, ''))}</td>")
        lineas.append("<td></td>" * (1 + (1 if penal_f is not None else 0) + (1 if d.get("u") is not None else 0)))
        lineas.append("</tr>")
    if d.get("v") is not None:
        lineas.append("<tr><th class='rotulo'>v_j</th>")
        lineas += [f"<td class='potencial'>{html.escape(x)}</td>" for x in d["v"]]
        lineas.append("<td></td>" * (1 + (1 if penal_f is not None else 0) + 1))
        lineas.append("</tr>")
    lineas.append("</table>")
    return "\n".join(lineas)


ESTILO_CSS = """
body{font-family:'Segoe UI',Arial,sans-serif;color:#0F172A;background:#F1F5F9;margin:0;padding:24px;}
.hoja{max-width:1200px;margin:auto;background:#fff;padding:28px 36px;border-radius:14px;
      box-shadow:0 2px 10px rgba(15,23,42,.08);}
h1{color:#3730A3;margin:0 0 4px 0;font-size:26px;} h2{color:#1E293B;border-bottom:3px solid #E0E7FF;
padding-bottom:6px;margin-top:34px;} h3{color:#3730A3;margin:22px 0 8px 0;}
.meta{color:#64748B;font-size:13px;margin-bottom:18px;}
table.tabla{border-collapse:collapse;margin:8px 0 14px 0;font-size:13px;}
table.tabla td,table.tabla th{border:1px solid #CBD5E1;padding:6px 10px;text-align:center;white-space:nowrap;}
table.tabla th{background:#1E293B;color:#fff;} table.tabla th.rotulo{background:#F1F5F9;color:#0F172A;text-align:left;}
table.transporte td{position:relative;min-width:72px;height:42px;vertical-align:bottom;}
.costo{position:absolute;top:0;right:0;font-size:11px;background:#F1F5F9;color:#475569;border-left:1px solid #CBD5E1;
       border-bottom:1px solid #CBD5E1;padding:1px 5px;} .asig{font-weight:bold;font-size:15px;padding-top:12px;}
.signo{position:absolute;top:2px;left:4px;font-weight:bold;color:#7C3AED;}
td.lateral{background:#F1F5F9;font-weight:bold;} td.penal{background:#EEF2FF;color:#3730A3;font-weight:bold;}
td.penal-max{background:#4F46E5;color:#fff;font-weight:bold;} td.potencial{background:#DBEAFE;color:#1D4ED8;font-weight:bold;}
.explicacion{white-space:pre-wrap;font-size:13.5px;line-height:1.45;background:#F8FAFC;border:1px solid #E2E8F0;
             border-radius:10px;padding:12px 16px;margin:6px 0 18px 0;}
.titulo{font-size:17px;font-weight:bold;color:#3730A3;} .subtitulo{font-weight:bold;color:#0F172A;}
.negrita{font-weight:bold;} .suave{color:#475569;} .formula{font-family:Consolas,'Courier New',monospace;font-size:12.5px;}
.exito{color:#15803D;font-weight:bold;} .error{color:#B91C1C;font-weight:bold;} .advertencia{color:#B45309;font-weight:bold;}
.info{color:#1D4ED8;font-weight:bold;} .entra{color:#1D4ED8;font-weight:bold;} .sale{color:#C2410C;font-weight:bold;}
.pivote{background:#F59E0B;color:#fff;font-weight:bold;padding:0 4px;border-radius:4px;} .resaltado{background:#FDE68A;}
.alternativo{color:#7E22CE;font-weight:bold;}
.aviso{border-left:6px solid;border-radius:8px;padding:10px 14px;margin:8px 0;}
.aviso.error{background:#FEE2E2;border-color:#B91C1C;} .aviso.advertencia{background:#FEF3C7;border-color:#B45309;}
.aviso.info{background:#DBEAFE;border-color:#1D4ED8;} .aviso.exito{background:#DCFCE7;border-color:#15803D;}
.aviso b{display:block;margin-bottom:3px;} .aviso span{color:#0F172A;font-weight:normal;}
@media print{body{background:#fff;padding:0;} .hoja{box-shadow:none;padding:0;} h2{page-break-after:avoid;}
table{page-break-inside:avoid;}}
"""


def avisos_html(casos) -> str:
    return "".join(f'<div class="aviso {c.nivel}"><b>{html.escape(c.titulo)}</b><span>{html.escape(c.mensaje)}'
                   f'</span></div>' for c in casos)


def documento_html(titulo: str, cuerpo: str) -> str:
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    return (f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>{html.escape(titulo)}</title>"
            f"<style>{ESTILO_CSS}</style></head><body><div class='hoja'><h1>{html.escape(titulo)}</h1>"
            f"<div class='meta'>Proyecto final · Investigación de Operaciones 1 · Grupo 9 · Generado el {fecha}"
            f"</div>{cuerpo}</div></body></html>")


def encabezado_texto(titulo: str) -> str:
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    linea = "=" * 78
    return f"{linea}\n{titulo}\nProyecto final · Investigación de Operaciones 1 · Grupo 9 · {fecha}\n{linea}\n\n"


def seccion_texto(titulo: str) -> str:
    return f"\n{'-' * 78}\n{titulo.upper()}\n{'-' * 78}\n"
