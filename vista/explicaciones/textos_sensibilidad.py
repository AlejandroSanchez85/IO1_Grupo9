"""
vista/explicaciones/textos_sensibilidad.py
==========================================
Frases de interpretación del análisis de sensibilidad (para quien toma la
decisión) y detalle de los cálculos hechos desde la tabla óptima.
"""
from __future__ import annotations

from modelo.simplex import ResultadoSensibilidad
from modelo.simplex.sensibilidad import INFERIOR, NINGUNO, SUPERIOR


def _b(texto, *etiquetas):
    return (texto, etiquetas)


def frase_recurso(s: ResultadoSensibilidad, rr, fmt) -> str:
    """Interpretación del precio sombra y del rango de b_i de una restricción."""
    p = s.problema
    rango = f"entre {fmt.limite_inferior(rr.minimo)} y {fmt.limite_superior(rr.maximo)} {rr.unidad}"
    y = rr.precio_sombra
    if not rr.activa:
        return (f"«{rr.nombre}» NO es limitante: se usan {fmt.num(rr.usado)} de {fmt.num(rr.valor_actual)} "
                f"{rr.unidad} y sobran {fmt.num(rr.holgura)}. Su precio sombra es 0: conseguir más de este "
                f"recurso no mejora z. Puede bajar hasta {fmt.limite_inferior(rr.minimo)} {rr.unidad} sin "
                f"cambiar el plan óptimo.")
    if y == 0:
        return (f"«{rr.nombre}» está activa (sin holgura) pero su precio sombra es 0 (caso degenerado): una "
                f"unidad adicional no cambia z. Rango válido: {rango}.")
    sube = "aumenta" if y > 0 else "disminuye"
    beneficio = ""
    if p.es_max and y > 0:
        beneficio = (f" Lo máximo que convendría pagar por cada {rr.unidad} adicional es "
                     f"{fmt.num(y)} {p.unidad_z}.")
    elif not p.es_max and y < 0:
        beneficio = f" Cada unidad adicional permite ahorrar {fmt.num(abs(y))} {p.unidad_z}."
    return (f"«{rr.nombre}» es un CUELLO DE BOTELLA (se usa completo). Si se dispone de 1 {rr.unidad} más, "
            f"z {sube} {fmt.num(abs(y))} {p.unidad_z} (y si hay 1 menos, cambia lo mismo al revés). "
            f"Este precio sombra es válido mientras el recurso esté {rango}.{beneficio}")


def frase_variable(s: ResultadoSensibilidad, rc, fmt) -> str:
    """Interpretación del costo reducido y del rango de c_j de una variable."""
    p = s.problema
    rango = f"entre {fmt.limite_inferior(rc.minimo)} y {fmt.limite_superior(rc.maximo)}"
    if rc.es_basica:
        return (f"«{rc.nombre}» está en el plan óptimo ({fmt.num(rc.valor_variable)} {rc.unidad}). Su "
                f"coeficiente actual es {fmt.num(rc.valor_actual)}; mientras se mantenga {rango} "
                f"(puede bajar {fmt.cambio(rc.disminucion)} o subir {fmt.cambio(rc.aumento)}), el plan "
                f"óptimo NO cambia (solo cambia el valor de z). Fuera de ese rango conviene cambiar el plan.")
    d = abs(rc.costo_reducido)
    if p.es_max:
        return (f"«{rc.nombre}» NO entra en el plan (vale 0). Costo reducido = {fmt.num(rc.costo_reducido)}: "
                f"obligar a producir 1 {rc.unidad} bajaría z en {fmt.num(d)} {p.unidad_z}. Solo convendría "
                f"incluirla si su coeficiente sube por encima de {fmt.limite_superior(rc.maximo)} "
                f"(aumento de {fmt.cambio(rc.aumento)}).")
    return (f"«{rc.nombre}» NO entra en el plan (vale 0). Costo reducido = {fmt.num(rc.costo_reducido)}: "
            f"obligar a usar 1 {rc.unidad} subiría z en {fmt.num(d)} {p.unidad_z}. Solo convendría incluirla "
            f"si su coeficiente baja de {fmt.limite_inferior(rc.minimo)} (disminución de "
            f"{fmt.cambio(rc.disminucion)}).")


def bloques_interpretacion(s: ResultadoSensibilidad, fmt) -> list:
    bloques = [_b("Interpretación para la toma de decisiones\n", "titulo"),
               _b("Recursos (restricciones)\n", "subtitulo")]
    for rr in s.rangos_recursos:
        bloques.append(_b(f"• {frase_recurso(s, rr, fmt)}\n", "vineta"))
    bloques.append(_b("\nVariables de decisión\n", "subtitulo"))
    for rc in s.rangos_costos:
        bloques.append(_b(f"• {frase_variable(s, rc, fmt)}\n", "vineta"))
    return bloques


def bloques_calculos(s: ResultadoSensibilidad, fmt) -> list:
    """Detalle matemático de todos los cálculos de sensibilidad."""
    p, t = s.problema, s.tabla
    es_max = p.es_max
    bloques = [_b("Cálculos desde la tabla óptima\n", "titulo")]
    bloques.append(_b("1) Matriz B^-1 y precios sombra\n", "subtitulo"))
    bloques.append(_b("  Como la base inicial eran las holguras, B^-1 son las columnas s1..sm de la tabla óptima.\n",
                      "vineta"))
    bloques.append(_b(f"  Cb (coeficientes de las básicas {', '.join(s.simbolos_base)}) = {fmt.vector(s.cb, False)}\n",
                      "formula"))
    for i in range(p.m):
        terminos = " + ".join(f"({fmt.num(s.cb[k])})({fmt.num(s.binv[k][i])})" for k in range(p.m))
        bloques.append(_b(f"  y{i + 1} = Cb · (columna s{i + 1}) = {terminos} = {fmt.num(s.precios_sombra[i])}\n",
                          "formula"))
    terminos = " + ".join(f"({fmt.num(p.b[i])})({fmt.num(s.precios_sombra[i])})" for i in range(p.m))
    bloques.append(_b(f"  Comprobación (dualidad): Σ b_i·y_i = {terminos} = {fmt.num(s.z_dual)}", "formula"))
    bloques.append(_b("  = z* " if s.z_dual == s.z else "  ≠ z* ", "exito" if s.z_dual == s.z else "error"))
    bloques.append(_b(f"({fmt.num(s.z)})\n", "formula"))

    bloques.append(_b("\n2) Rango de cada c_j (optimalidad)\n", "subtitulo"))
    regla = "≤ 0" if es_max else "≥ 0"
    bloques.append(_b(f"  Condición: con c_j + Δ, todos los Cj − Zj de las no básicas deben seguir {regla}.\n",
                      "vineta"))
    for rc in s.rangos_costos:
        bloques.append(_b(f"  {rc.simbolo} ({rc.nombre}) — {'básica' if rc.es_basica else 'no básica'}:\n",
                          "negrita"))
        if not rc.es_basica:
            if es_max:
                bloques.append(_b(f"     Solo cambia su propio Cj − Zj = {fmt.num(rc.costo_reducido)}: "
                                  f"c_j puede subir hasta Zj = {fmt.num(rc.maximo)} (Δ ≤ {fmt.cambio(rc.aumento)}); "
                                  f"bajar no la hace entrar (Δ ≥ −∞).\n", "formula"))
            else:
                bloques.append(_b(f"     Solo cambia su propio Cj − Zj = {fmt.num(rc.costo_reducido)}: "
                                  f"c_j puede bajar hasta Zj = {fmt.num(rc.minimo)} (Δ ≥ −{fmt.cambio(rc.disminucion)}); "
                                  f"subir no la hace entrar (Δ ≤ +∞).\n", "formula"))
        else:
            fila = t.fila_de(rc.indice)
            bloques.append(_b(f"     Es básica en la fila {t.simbolos[t.base[fila]]}. Para cada no básica l: "
                              f"(Cl − Zl) − Δ·a_rl {regla}\n", "formula"))
            for calc in rc.calculos:
                if calc.tipo == NINGUNO:
                    bloques.append(_b(f"       {calc.referencia}: a = 0 → no limita\n", "formula"))
                else:
                    limite = "Δ ≤" if calc.tipo == SUPERIOR else "Δ ≥"
                    bloques.append(_b(f"       {calc.referencia}: ({fmt.num(calc.numerador)}) − Δ·({fmt.num(calc.denominador)}) "
                                      f"{regla} → {limite} {fmt.num(calc.cociente)}\n", "formula"))
        bloques.append(_b(f"     Rango: {fmt.limite_inferior(rc.minimo)} ≤ c ≤ {fmt.limite_superior(rc.maximo)}\n",
                          "formula", "negrita"))

    bloques.append(_b("\n3) Rango de cada b_i (factibilidad)\n", "subtitulo"))
    bloques.append(_b("  Condición: x_B + Δ·(columna i de B^-1) ≥ 0 para todas las básicas.\n", "vineta"))
    for rr in s.rangos_recursos:
        bloques.append(_b(f"  b{rr.indice + 1} ({rr.nombre}) = {fmt.num(rr.valor_actual)}:\n", "negrita"))
        for calc in rr.calculos:
            if calc.tipo == NINGUNO:
                bloques.append(_b(f"       {calc.referencia}: {fmt.num(calc.numerador)} + Δ·(0) ≥ 0 → no limita\n",
                                  "formula"))
            else:
                limite = "Δ ≥" if calc.tipo == INFERIOR else "Δ ≤"
                bloques.append(_b(f"       {calc.referencia}: {fmt.num(calc.numerador)} + Δ·({fmt.num(calc.denominador)}) "
                                  f"≥ 0 → {limite} {fmt.num(calc.cociente)}\n", "formula"))
        bloques.append(_b(f"     Rango: {fmt.limite_inferior(rr.minimo)} ≤ b ≤ {fmt.limite_superior(rr.maximo)} "
                          f"{rr.unidad}\n", "formula", "negrita"))
    return bloques
