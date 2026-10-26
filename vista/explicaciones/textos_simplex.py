"""
vista/explicaciones/textos_simplex.py
=====================================
Convierte los resultados del modelo Simplex en EXPLICACIONES paso a paso
(con los nombres y unidades del problema) y en los datos de
las tablas que se dibujan. Lo usan los paneles.

Cada explicación es una lista de bloques (texto, etiquetas) donde las
etiquetas dan el estilo: "titulo", "subtitulo", "negrita", "formula", ...
"""
from __future__ import annotations

from fractions import Fraction

from modelo.simplex import (ALTERNATIVA, CONTINUA, LIMITE, NO_ACOTADA, OPTIMA, ProblemaPL,
                            ResultadoSimplex)
from ..tema import COLORES


# ---------------------------------------------------------------- utilidades
def etiqueta_columna(problema: ProblemaPL, j: int) -> str:
    if j < problema.n:
        return problema.variables[j].etiqueta
    restriccion = problema.restricciones[j - problema.n]
    return f"s{j - problema.n + 1} (holgura de {restriccion.nombre})"


def expresion_lineal(coeficientes, simbolos, fmt, separador: str = "·") -> str:
    """70000·x1 + 50000·x2 − 3·x3 (omite los ceros)."""
    partes = []
    for coef, simbolo in zip(coeficientes, simbolos):
        coef = Fraction(coef)
        if coef == 0:
            continue
        signo = "-" if coef < 0 else "+"
        absoluto = abs(coef)
        termino = simbolo if absoluto == 1 else f"{fmt.num(absoluto)}{separador}{simbolo}"
        partes.append((signo, termino))
    if not partes:
        return "0"
    texto = ("-" if partes[0][0] == "-" else "") + partes[0][1]
    for signo, termino in partes[1:]:
        texto += f" {signo} {termino}"
    return texto


def _b(texto, *etiquetas):
    return (texto, etiquetas)


def _verbo_mejora(problema: ProblemaPL) -> str:
    return "aumenta" if problema.es_max else "disminuye"


# ------------------------------------------------------------------- modelo
def bloques_modelo(problema: ProblemaPL, fmt) -> list:
    p = problema
    simbolos = [v.simbolo for v in p.variables]
    sentido = "Maximizar" if p.es_max else "Minimizar"
    bloques = [_b(f"{p.nombre}\n", "titulo")]
    if p.descripcion:
        bloques.append(_b(p.descripcion + "\n\n", "suave"))
    bloques.append(_b("1. Variables de decisión\n", "subtitulo"))
    for v in p.variables:
        bloques.append(_b(f"  {v.simbolo} = {v.nombre}  [{v.unidad}]\n", "vineta"))
    bloques.append(_b(f"\n2. Función objetivo ({p.descripcion_z}, en {p.unidad_z})\n", "subtitulo"))
    bloques.append(_b(f"  {sentido}  z = {expresion_lineal(p.c, simbolos, fmt)}\n", "formula"))
    bloques.append(_b("\n3. Restricciones (todas de tipo ≤)\n", "subtitulo"))
    for r in p.restricciones:
        bloques.append(_b(f"  {r.simbolo}: {expresion_lineal(r.coeficientes, simbolos, fmt)} ≤ "
                          f"{fmt.num(r.lado_derecho)}", "formula"))
        bloques.append(_b(f"     ← {r.nombre} [{r.unidad}]\n", "suave"))
    bloques.append(_b(f"  {', '.join(simbolos)} ≥ 0   (no negatividad)\n", "formula"))

    bloques.append(_b("\n4. Forma estándar (PASO 1 del Simplex)\n", "subtitulo"))
    bloques.append(_b("Se suma una variable de HOLGURA s_i ≥ 0 a cada restricción ≤ para volverla igualdad. "
                      "s_i = cantidad que SOBRA del recurso i. Las holguras no aportan a z (Cj = 0).\n", ""))
    todos = simbolos + [f"s{i + 1}" for i in range(p.m)]
    bloques.append(_b(f"  {sentido}  z = {expresion_lineal(p.c, simbolos, fmt)}"
                      + "".join(f" + 0·s{i + 1}" for i in range(p.m)) + "\n", "formula"))
    for i, r in enumerate(p.restricciones):
        coefs = list(r.coeficientes) + [1 if k == i else 0 for k in range(p.m)]
        bloques.append(_b(f"  {expresion_lineal(coefs, todos, fmt)} = {fmt.num(r.lado_derecho)}\n", "formula"))
    bloques.append(_b(f"  {', '.join(todos)} ≥ 0\n", "formula"))
    bloques.append(_b("\nSolución inicial: las variables de decisión valen 0 y cada holgura vale su b_i "
                      "(base inicial = holguras).\n", "suave"))

    bloques.append(_b("\n5. Reglas del método usadas en este problema\n", "subtitulo"))
    if p.es_max:
        reglas = ["Prueba de optimalidad: la tabla es ÓPTIMA cuando todos los Cj − Zj ≤ 0.",
                  "Variable que ENTRA: la de mayor Cj − Zj positivo (si hay empate, la de menor índice).",
                  "Variable que SALE: la de menor razón b_i / a_ik con a_ik > 0 (empate: menor índice).",
                  "Si ningún a_ik es positivo, el problema es NO ACOTADO."]
    else:
        reglas = ["Prueba de optimalidad: la tabla es ÓPTIMA cuando todos los Cj − Zj ≥ 0.",
                  "Variable que ENTRA: la de Cj − Zj más negativo (si hay empate, la de menor índice).",
                  "Variable que SALE: la de menor razón b_i / a_ik con a_ik > 0 (empate: menor índice).",
                  "Si ningún a_ik es positivo, el problema es NO ACOTADO."]
    for regla in reglas:
        bloques.append(_b(f"  • {regla}\n", "vineta"))
    bloques.append(_b("  • Zj = Σ (Cb_i × a_ij)   y   z = Σ (Cb_i × b_i)\n", "vineta"))
    return bloques


# ------------------------------------------------------- tabla de iteración
def datos_tabla(resultado: ResultadoSimplex, indice: int, fmt, iteracion=None) -> dict:
    """Filas y estilos de la tabla Simplex de una iteración (para TablaCanvas)."""
    p = resultado.problema
    it = iteracion or resultado.iteraciones[indice]
    t = it.tabla
    columnas = t.columnas
    nombres = p.nombres_columnas()
    mostrar_razones = it.estado in (CONTINUA, NO_ACOTADA) or (it.estado == OPTIMA and it.columna_entra is not None)
    encabezado_cj = ["", "Cj →"] + [fmt.num(v) for v in t.cj] + ["", ""] if mostrar_razones else \
        ["", "Cj →"] + [fmt.num(v) for v in t.cj] + [""]
    encabezado = ["Base", "Cb"] + [f"{t.simbolos[j]}\n{_corto(nombres[j])}" for j in range(columnas)] + \
                 ["b\n(Solución)"]
    if mostrar_razones:
        encabezado.append("Razón\nb / a")
    filas = [encabezado_cj, encabezado]
    for i in range(t.m):
        fila = [t.simbolos[t.base[i]], fmt.num(t.cb[i])] + [fmt.num(v) for v in t.matriz[i]] + [fmt.num(t.b[i])]
        if mostrar_razones:
            razon = it.razones[i] if i < len(it.razones) else None
            fila.append(fmt.num(razon) if razon is not None else "—")
        filas.append(fila)
    fila_zj = ["Zj", ""] + [fmt.num(v) for v in t.zj] + [fmt.num(t.z)]
    fila_cz = ["Cj − Zj", ""] + [fmt.num(v) for v in t.cj_menos_zj] + [""]
    if mostrar_razones:
        fila_zj.append("")
        fila_cz.append("")
    filas += [fila_zj, fila_cz]

    estilos = {}
    c = COLORES
    fila_zj_idx, fila_cz_idx = 2 + t.m, 3 + t.m
    estilos_fila = {fila_zj_idx: {"bg": c["zj"], "negrita": True},
                    fila_cz_idx: {"bg": c["cjzj"], "negrita": True}}
    col_b = 2 + columnas
    # Columna y fila pivote, elemento pivote
    if it.columna_entra is not None:
        k = 2 + it.columna_entra
        color_columna = c["no_acotado"] if it.estado == NO_ACOTADA else (
            c["alternativo"] if it.estado == OPTIMA else c["col_pivote"])
        for r in range(2, 4 + t.m):
            estilos[(r, k)] = {"bg": color_columna}
        estilos[(1, k)] = {"bg": COLORES["info"] if it.estado == CONTINUA else (
            c["error"] if it.estado == NO_ACOTADA else c["alternativo_texto"]), "fg": "#FFFFFF", "negrita": True}
        estilos[(fila_cz_idx, k)] = {"bg": color_columna, "negrita": True,
                                     "fg": COLORES["info"] if it.estado == CONTINUA else c["texto"]}
    if it.fila_sale is not None:
        r = 2 + it.fila_sale
        for col in range(0, len(filas[1])):
            estilos.setdefault((r, col), {})
            estilos[(r, col)] = {**estilos[(r, col)], "bg": c["fila_pivote"]}
        estilos[(r, 0)] = {"bg": "#C2410C", "fg": "#FFFFFF", "negrita": True}
        if it.columna_entra is not None:
            estilos[(r, 2 + it.columna_entra)] = {"bg": c["celda_pivote"], "fg": "#FFFFFF", "negrita": True}
        if mostrar_razones:
            estilos[(r, len(filas[1]) - 1)] = {"bg": c["razon_minima"], "negrita": True}
    # Óptima: resaltar z y los Cj − Zj = 0 de no básicas (óptimos alternativos)
    if it.estado in (OPTIMA, ALTERNATIVA):
        estilos[(fila_zj_idx, col_b)] = {"bg": c["optimo"], "fg": c["optimo_texto"], "negrita": True}
        for j in range(columnas):
            if not t.es_basica(j) and t.cj_menos_zj[j] == 0:
                estilos[(fila_cz_idx, 2 + j)] = {"bg": c["alternativo"], "fg": c["alternativo_texto"],
                                                 "negrita": True}
        for i in range(t.m):
            if t.base[i] < p.n:
                estilos.setdefault((2 + i, col_b), {})
                estilos[(2 + i, col_b)] = {**estilos[(2 + i, col_b)], "bg": c["optimo"], "negrita": True}
    # Valores básicos degenerados (= 0)
    for i in range(t.m):
        if t.b[i] == 0:
            estilos[(2 + i, col_b)] = {**estilos.get((2 + i, col_b), {}), "fg": c["advertencia"], "negrita": True}
    # Fila Cj de encabezado con estilo secundario
    for col in range(len(filas[0])):
        estilos[(0, col)] = {"bg": c["tabla_sub"], "fg": c["texto"], "negrita": col == 1}
    return {"filas": filas, "estilos": estilos, "estilos_fila": estilos_fila,
            "filas_encabezado": 2, "columnas_encabezado": 2}


def _corto(texto: str, maximo: int = 14) -> str:
    return texto if len(texto) <= maximo else texto[:maximo - 1] + "…"


def titulo_iteracion(resultado: ResultadoSimplex, indice: int, iteracion=None) -> str:
    it = iteracion or resultado.iteraciones[indice]
    if it.estado == ALTERNATIVA:
        return f"Tabla {it.numero} — solución óptima ALTERNATIVA"
    nombre = "Tabla inicial (iteración 0)" if it.numero == 0 else f"Tabla de la iteración {it.numero}"
    estado = {CONTINUA: "no óptima", OPTIMA: "ÓPTIMA", NO_ACOTADA: "NO ACOTADO",
              LIMITE: "límite de iteraciones"}.get(it.estado, "")
    return f"{nombre} — {estado}"


# ----------------------------------------------------- explicación de pasos
def bloques_iteracion(resultado: ResultadoSimplex, indice: int, fmt, iteracion=None, siguiente=None) -> list:
    p = resultado.problema
    it = iteracion or resultado.iteraciones[indice]
    t = it.tabla
    if siguiente is None:
        if it.estado == OPTIMA and it.columna_entra is not None:
            siguiente = resultado.iteracion_alternativa
        elif indice + 1 < len(resultado.iteraciones):
            siguiente = resultado.iteraciones[indice + 1]
    bloques = [_b(titulo_iteracion(resultado, indice, it) + "\n", "titulo")]
    if it.estado == ALTERNATIVA:
        bloques.append(_b("Esta tabla se obtuvo haciendo entrar una variable no básica con Cj − Zj = 0 en la "
                          "tabla óptima: el valor de z no cambia, pero la solución es otra.\n", ""))

    # 1) Solución básica actual
    bloques.append(_b("1) Solución básica actual\n", "subtitulo"))
    basicas = [f"{t.simbolos[t.base[i]]} = {fmt.num(t.b[i])}" for i in range(t.m)]
    no_basicas = [t.simbolos[j] for j in range(t.columnas) if not t.es_basica(j)]
    bloques.append(_b("  Variables básicas: " + ", ".join(basicas) + "\n", "vineta"))
    bloques.append(_b("  No básicas (valen 0): " + (", ".join(no_basicas) or "ninguna") + "\n", "vineta"))
    valores = ", ".join(f"{v.nombre} = {fmt.num(t.valor(j))} {v.unidad}" for j, v in enumerate(p.variables))
    bloques.append(_b(f"  Plan actual: {valores}\n", "vineta"))
    bloques.append(_b(f"  z = {fmt.num(t.z)} {p.unidad_z}\n", "vineta", "negrita"))
    if t.es_degenerada():
        bloques.append(_b("  Atención: Solución DEGENERADA: una variable básica vale 0.\n", "advertencia"))

    # 2) Cálculo de Zj y Cj − Zj
    bloques.append(_b("2) Cálculo del renglón Zj y Cj − Zj   (Zj = Σ Cb_i × a_ij)\n", "subtitulo"))
    for j in range(t.columnas):
        terminos = " + ".join(f"({fmt.num(t.cb[i])})({fmt.num(t.matriz[i][j])})" for i in range(t.m))
        bloques.append(_b(f"  Z({t.simbolos[j]}) = {terminos} = {fmt.num(t.zj[j])}   →   "
                          f"C − Z = {fmt.num(t.cj[j])} − {fmt.par(t.zj[j])} = {fmt.num(t.cj_menos_zj[j])}\n",
                          "formula"))
    terminos = " + ".join(f"({fmt.num(t.cb[i])})({fmt.num(t.b[i])})" for i in range(t.m))
    bloques.append(_b(f"  z = Σ Cb_i × b_i = {terminos} = {fmt.num(t.z)}\n", "formula"))

    # 3) Prueba de optimalidad
    criterio = "todos los Cj − Zj ≤ 0" if p.es_max else "todos los Cj − Zj ≥ 0"
    signo = "> 0" if p.es_max else "< 0"
    bloques.append(_b(f"3) Prueba de optimalidad ({'Maximizar' if p.es_max else 'Minimizar'}: "
                      f"es óptima si {criterio})\n", "subtitulo"))
    if it.estado in (CONTINUA, NO_ACOTADA, LIMITE):
        lista = ", ".join(f"{t.simbolos[j]} ({fmt.num(t.cj_menos_zj[j])})" for j in it.candidatos_entrada)
        bloques.append(_b(f"  Hay Cj − Zj {signo} en: {lista}. La tabla NO es óptima: z todavía "
                          f"{'puede crecer' if p.es_max else 'puede bajar'}.\n", "vineta"))
    else:
        bloques.append(_b(f"  Se cumple: {criterio}. ", "vineta"))
        bloques.append(_b("La tabla es ÓPTIMA.\n", "exito"))

    if it.estado in (CONTINUA, NO_ACOTADA):
        k = it.columna_entra
        regla = "mayor Cj − Zj positivo" if p.es_max else "Cj − Zj más negativo"
        if it.regla == "bland":
            regla = "regla de Bland: la de menor índice que mejora z"
        bloques.append(_b("4) Variable que ENTRA\n", "subtitulo"))
        bloques.append(_b(f"  Entra {etiqueta_columna(p, k)}", "entra"))
        bloques.append(_b(f" porque tiene el {regla} ({fmt.num(t.cj_menos_zj[k])}). Por cada unidad que "
                          f"entre, z {_verbo_mejora(p)} {fmt.num(abs(t.cj_menos_zj[k]))} {p.unidad_z}.\n", ""))
        if it.empate_entrada:
            nombres = ", ".join(t.simbolos[j] for j in it.empate_entrada)
            bloques.append(_b(f"  Empate entre {nombres}: se elige la de menor índice ({t.simbolos[k]}).\n",
                              "advertencia"))
        bloques.extend(_bloques_razon(p, it, fmt, numero="5"))
        if it.estado == NO_ACOTADA:
            bloques.append(_b(f"  Ningún coeficiente de la columna {t.simbolos[k]} es positivo: no hay razón "
                              f"mínima, nada detiene el crecimiento de {t.simbolos[k]}.\n", "vineta"))
            bloques.append(_b(f"  PROBLEMA NO ACOTADO: z → {'+∞' if p.es_max else '−∞'}.\n", "error"))
            return bloques
        bloques.extend(_bloques_operaciones(p, it, siguiente, fmt, numero="6"))
        if siguiente is not None:
            cambio = siguiente.tabla.z - t.z
            if cambio == 0:
                bloques.append(_b(f"  z se mantiene en {fmt.num(t.z)} (pivoteo degenerado: la razón mínima "
                                  f"fue 0).\n", "advertencia"))
            else:
                bloques.append(_b(f"  z pasa de {fmt.num(t.z)} a {fmt.num(siguiente.tabla.z)} "
                                  f"({'+' if cambio > 0 else ''}{fmt.num(cambio)} {p.unidad_z}).\n", "negrita"))
    elif it.estado == OPTIMA:
        bloques.extend(bloques_resumen_optimo(resultado, fmt, t))
        if it.columnas_cero:
            nombres = ", ".join(etiqueta_columna(p, j) for j in it.columnas_cero)
            bloques.append(_b("\nÓptimos alternativos\n", "subtitulo"))
            bloques.append(_b(f"  Cj − Zj = 0 en variable(s) NO básica(s): {nombres}. Si una de ellas entra a "
                              f"la base, z no cambia.\n", "alternativo"))
            if it.columna_entra is not None and siguiente is not None:
                bloques.append(_b(f"  Se hace entrar {etiqueta_columna(p, it.columna_entra)} para obtener "
                                  f"otra solución óptima:\n", "vineta"))
                bloques.extend(_bloques_razon(p, it, fmt, numero="a"))
                bloques.extend(_bloques_operaciones(p, it, siguiente, fmt, numero="b"))
    elif it.estado == ALTERNATIVA:
        bloques.extend(bloques_resumen_optimo(resultado, fmt, t, alternativa=True))
    return bloques


def _bloques_razon(p, it, fmt, numero: str) -> list:
    t = it.tabla
    k = it.columna_entra
    bloques = [_b(f"{numero}) Prueba de la razón mínima (b_i ÷ a_i,{t.simbolos[k]}, solo con a > 0)\n",
                  "subtitulo")]
    validas = [r for r in it.razones if r is not None]
    minima = min(validas) if validas else None
    for i in range(t.m):
        a = t.matriz[i][k]
        nombre = t.simbolos[t.base[i]]
        if it.razones and it.razones[i] is not None:
            marca = "   ← mínima" if it.razones[i] == minima else ""
            bloques.append(_b(f"  Fila {nombre}: {fmt.num(t.b[i])} ÷ {fmt.num(a)} = {fmt.num(it.razones[i])}{marca}\n",
                              "formula", *(("resaltado",) if marca else ())))
        else:
            bloques.append(_b(f"  Fila {nombre}: a = {fmt.num(a)} ≤ 0 → no se considera\n", "formula"))
    if it.fila_sale is not None:
        sale = t.simbolos[t.base[it.fila_sale]]
        bloques.append(_b(f"  Sale {sale}", "sale"))
        bloques.append(_b(f" (la menor razón = {fmt.num(it.razones[it.fila_sale])}; es lo máximo que puede crecer "
                          f"{t.simbolos[k]} sin que ninguna variable se vuelva negativa).\n", ""))
        bloques.append(_b("  Elemento pivote: ", ""))
        bloques.append(_b(f" {fmt.num(it.pivote)} ", "pivote"))
        bloques.append(_b(f"  (fila {sale}, columna {t.simbolos[k]}).\n", ""))
        if it.empate_salida:
            nombres = ", ".join(t.simbolos[t.base[i]] for i in it.empate_salida)
            bloques.append(_b(f"  Atención: Empate en la razón mínima entre {nombres}: se elige la básica de menor índice. "
                              f"La siguiente solución será DEGENERADA (una básica quedará en 0).\n", "advertencia"))
    return bloques


def _bloques_operaciones(p, it, siguiente, fmt, numero: str) -> list:
    if siguiente is None:
        return []
    t, nueva = it.tabla, siguiente.tabla
    r, k = it.fila_sale, it.columna_entra
    entra = t.simbolos[k]
    sale = t.simbolos[t.base[r]]
    bloques = [_b(f"{numero}) Operaciones de fila (Gauss-Jordan) para obtener la tabla siguiente\n", "subtitulo")]
    fila_pivote_nueva = list(nueva.matriz[r]) + [nueva.b[r]]
    bloques.append(_b(f"  Nueva fila {entra} = fila {sale} ÷ {fmt.par(it.pivote)} = "
                      f"{fmt.vector(fila_pivote_nueva)}\n", "formula"))
    for i in range(t.m):
        if i == r:
            continue
        nombre = t.simbolos[t.base[i]]
        factor = it.factores[i] if i < len(it.factores) else t.matriz[i][k]
        if factor == 0:
            bloques.append(_b(f"  Fila {nombre}: su coeficiente en {entra} es 0 → no cambia\n", "formula"))
            continue
        vieja = list(t.matriz[i]) + [t.b[i]]
        resultado_fila = list(nueva.matriz[i]) + [nueva.b[i]]
        bloques.append(_b(f"  Nueva fila {nombre} = fila {nombre} − ({fmt.num(factor)}) × nueva fila {entra}\n"
                          f"      = {fmt.vector(vieja)} − ({fmt.num(factor)}) × {fmt.vector(fila_pivote_nueva)}\n"
                          f"      = {fmt.vector(resultado_fila)}\n", "formula"))
    return bloques


def bloques_resumen_optimo(resultado: ResultadoSimplex, fmt, tabla=None, alternativa: bool = False) -> list:
    p = resultado.problema
    t = tabla or resultado.tabla_final
    titulo = "Solución óptima alternativa" if alternativa else "Solución óptima"
    bloques = [_b(f"\n{titulo}\n", "subtitulo")]
    for j, v in enumerate(p.variables):
        bloques.append(_b(f"  {v.simbolo} = {v.nombre}: {fmt.num_doble(t.valor(j))} {v.unidad}\n", "vineta"))
    for i, r in enumerate(p.restricciones):
        holgura = t.valor(p.n + i)
        estado = "sin holgura (recurso agotado)" if holgura == 0 else f"sobran {fmt.num(holgura)} {r.unidad}"
        bloques.append(_b(f"  s{i + 1} = {fmt.num(holgura)} → {r.nombre}: {estado}\n", "vineta"))
    bloques.append(_b(f"  z* = {fmt.num_doble(t.z)} {p.unidad_z}  ({p.descripcion_z} "
                      f"{'máxima' if p.es_max else 'mínima'})\n", "exito"))
    return bloques


# ------------------------------------------------------------------ solución
def bloques_comprobacion(resultado: ResultadoSimplex, fmt) -> list:
    """Sustituye la solución en el modelo original para comprobarla."""
    p = resultado.problema
    x = resultado.valores_variables()
    bloques = [_b("Comprobación: se reemplaza la solución en el modelo original\n", "subtitulo")]
    terminos = " + ".join(f"({fmt.num(p.c[j])})({fmt.num(x[j])})" for j in range(p.n))
    z = sum((p.c[j] * x[j] for j in range(p.n)), Fraction(0))
    bloques.append(_b(f"  z = {terminos} = {fmt.num(z)} {p.unidad_z}\n", "formula"))
    for r in p.restricciones:
        izquierda = sum((r.coeficientes[j] * x[j] for j in range(p.n)), Fraction(0))
        terminos = " + ".join(f"({fmt.num(r.coeficientes[j])})({fmt.num(x[j])})" for j in range(p.n))
        cumple = "(cumple)" if izquierda <= r.lado_derecho else "(NO cumple)"
        bloques.append(_b(f"  {r.nombre}: {terminos} = {fmt.num(izquierda)} ≤ {fmt.num(r.lado_derecho)}  "
                          f"{cumple}\n", "formula"))
    return bloques


def texto_plan(resultado: ResultadoSimplex, fmt, tabla=None) -> str:
    """Frase final con nombres y unidades."""
    p = resultado.problema
    t = tabla or resultado.tabla_final
    partes = [f"{fmt.num(t.valor(j))} {v.unidad} de {v.nombre}" for j, v in enumerate(p.variables)]
    verbo = "máxima" if p.es_max else "mínima"
    return (f"La decisión óptima es: {', '.join(partes)}. Con este plan se obtiene {p.descripcion_z.lower()} "
            f"{verbo} de z = {fmt.num(t.z)} {p.unidad_z}.")
