# Proyecto Final · Investigación de Operaciones I · Grupo 9

Software de escritorio en **Python** que resuelve, paso a paso, problemas de **Programación Lineal con el Método Simplex (maximizar y minimizar)**.

| Dato                   | Detalle                                                                     |
|------------------------|-----------------------------------------------------------------------------|
| **Universidad**        | Universidad Distrital Francisco José de Caldas                              |
| **Asignatura**         | Investigación de Operaciones I · Grupo 020-82 (IO1-82)                      |
| **Docente**            | Lilian Bejarano                                                             |
| **Periodo**            | 2026-3                                                                      |
| **Grupo del proyecto** | Grupo 9 · Método: **Simplex** · Lenguaje: **Python** |
| **Caso real**          | Cementos Argos S.A. – Línea de Concreto Premezclado (Regional Bogotá)       |
| **Ciudad**             | Bogotá D.C., Colombia                                                       |
| **Segunda Entrega**    | 27 de Octubre de 2026                                                       |

### Integrantes

| Nombre | Código |
|---|---|
| Diego Alejandro Parra Díaz | 20212020091 |
| Alejandro Sánchez Escobar | 20222020252 |
| Juan Andrés Villada Saray | 20242020261 |
| Jimmy Alejandro Granados Becerra | 20251020034 |

---

## Contenido

1. [¿Qué hace el software?](#1-qué-hace-el-software)
2. [Requisitos](#2-requisitos)
3. [Instalar Python](#3-instalar-python)
4. [Descargar el proyecto](#4-descargar-el-proyecto)
5. [Ejecutar el programa](#5-ejecutar-el-programa)
6. [Ejecutar las pruebas automáticas](#6-ejecutar-las-pruebas-automáticas)
7. [Manual de uso del programa](#7-manual-de-uso-del-programa)
8. [Ejemplos precargados](#8-ejemplos-precargados)
9. [Estructura del proyecto](#9-estructura-del-proyecto)
10. [Declaración de uso de IA](#10-declaración-de-uso-de-ia)


---

## 1. ¿Qué hace el software?

El programa implementa el **Método Simplex** asignado al Grupo 9 (tabla de la Sección 3 de la guía), **programado desde cero**.

| Método | Problema que resuelve | Tamaño máximo | Qué muestra | Casos especiales que avisa |
|---|---|---|---|---|
| **Simplex (max / min)** | Programación lineal con restricciones **≤** y b ≥ 0 | **8 variables × 8 restricciones** | Forma estándar; **cada tabla** con variable que **entra**, variable que **sale** y elemento **pivote**; cálculo de Zj y Cj − Zj; operaciones de fila; solución final y z; **análisis de sensibilidad** | No acotado · Óptimos alternativos · Degeneración · Ciclaje |

> **Importante:** ningún método usa librerías o programas que resuelvan el problema (**no se usa SciPy, PuLP, OR-Tools, NumPy ni el Solver de Excel**). Toda la matemática está escrita por el grupo en la carpeta `modelo/`. Esas herramientas solo se usan **aparte**, para comprobar los resultados en el informe.

**Características principales**

* Funciona con **cualquier problema** que escriba el usuario: los datos **nunca están dentro del código**.
* Cálculos con **fracciones exactas**: no hay errores de redondeo en empates, degeneración ni óptimos alternativos.
* Resultados con los **nombres y unidades** del problema (no solo x1, x2).
* **Validación**: casillas vacías, texto o datos imposibles se marcan en rojo con un mensaje claro y el programa **no se cierra**.
* **Ejemplos precargados** (caso real + problemas de prueba), y la opción de **guardar y abrir** problemas en archivos `.json`.

---

## 2. Requisitos

| Requisito | Detalle |
|---|---|
| **Sistema operativo** | Windows 10/11, macOS o Linux |
| **Python** | **3.10 o superior** (probado en 3.10, 3.11, 3.12, 3.13 y 3.14) |
| **Tkinter** | Viene **incluido** con Python de [python.org](https://www.python.org/downloads/) en Windows y macOS |
| **Librerías externas** | **Ninguna.** No hay que instalar nada con `pip` (ver `requirements.txt`) |
| **Espacio** | Menos de 1 MB |

---

## 3. Instalar Python

Para saber si ya tiene Python, abra una terminal (en Windows: tecla **Windows**, escriba `cmd` y presione **Enter**) y escriba:

```bash
python --version
```

Si aparece `Python 3.10` o superior, puede pasar a la [sección 5](#5-descargar-el-proyecto). Si sale un error o una versión menor, instálelo así:

### Windows

1. Entre a **https://www.python.org/downloads/** y pulse el botón amarillo **Download Python 3.x**.
2. Abra el archivo descargado (`python-3.x.x-amd64.exe`).
3. **MUY IMPORTANTE:** en la primera pantalla marque la casilla **☑ Add python.exe to PATH**.
4. Pulse **Install Now**. La opción *tcl/tk and IDLE* viene marcada por defecto: **no la desmarque** (es la que dibuja la ventana del programa).
5. Al terminar, si aparece **Disable path length limit**, púlselo. Luego **Close**.
6. Cierre y vuelva a abrir la terminal y compruebe con `python --version`.

### macOS

1. Descargue el instalador **macOS 64-bit universal2** desde **https://www.python.org/downloads/**.
2. Ábralo y siga los pasos (Continuar → Aceptar → Instalar).
3. En la terminal compruebe con `python3 --version`.

> Si instaló Python con **Homebrew**, Tkinter puede no venir incluido. Instálelo con: `brew install python-tk`

### Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install python3 python3-tk
```

En Fedora: `sudo dnf install python3 python3-tkinter`

---

## 4. Descargar el proyecto

### Archivo ZIP (la más común)

1. Descargue el archivo `IO1_Grupo9.zip` (de la plataforma del curso o del repositorio).
2. **Clic derecho** sobre el ZIP → **Extraer todo…** (Windows) o doble clic (macOS).
3. Elija una carpeta fácil de encontrar, por ejemplo el **Escritorio**, y pulse **Extraer**.
4. Abra la carpeta extraída y **verifique que adentro esté el archivo `main.py`** junto a las carpetas `modelo`, `vista`, `controlador`, `ejemplos` y `tests`.

> **Atención:** al descomprimir, a veces queda una carpeta dentro de otra con el mismo nombre (`IO1_Grupo9/IO1_Grupo9/`). La carpeta correcta es **la que contiene `main.py`**. Use siempre esa.


### Estructura que debe ver al abrir la carpeta

```
IO1_Grupo9/
├── main.py          ← archivo que se ejecuta
├── README.md
├── requirements.txt
├── controlador/
├── ejemplos/
├── modelo/
├── tests/
└── vista/
```

---

## 5. Ejecutar el programa

En todos los casos se ejecuta el archivo **`main.py`**. Al abrirse verá una ventana con una barra lateral oscura que dice **"IO1 · Grupo 9"** y el menú **Inicio · Simplex (max / min) · Ayuda**.

### 5.1 PyCharm (recomendado)

1. Abra **PyCharm**.
2. En la pantalla de bienvenida pulse **Open** (si ya hay un proyecto abierto: menú **☰ → File → Open…**).
3. Busque y seleccione **la carpeta que contiene `main.py`** → **OK**. Si pregunta *Trust project?*, pulse **Trust Project**.
4. **Configurar el intérprete de Python** (solo la primera vez):
   1. Menú **☰ → File → Settings** (en macOS: **PyCharm → Settings**).
   2. A la izquierda: **Project: IO1_Grupo9 → Python Interpreter**.
   3. Si dice **`<No interpreter>`**, pulse **Add Interpreter → Add Local Interpreter…**
   4. Elija **Generate new**, tipo **Virtualenv**, y en **Base Python** seleccione su Python (3.10 o superior). Deje la ubicación `.venv` que propone.
   5. Pulse **OK** y luego **OK** otra vez.
5. En el panel **Project** de la izquierda (si no lo ve: **Alt + 1**), **clic derecho sobre `main.py` → Run 'main'**.
6. Se abre la ventana del programa. Las siguientes veces puede usar el triángulo verde **▶** de arriba a la derecha.

### 5.2 Visual Studio Code

1. Instale **VS Code** (https://code.visualstudio.com) y, dentro de VS Code, la extensión **Python** de Microsoft (ícono de cuadritos a la izquierda → busque *Python* → **Install**).
2. **File → Open Folder…** y seleccione la carpeta que contiene `main.py`.
3. Pulse **Ctrl + Shift + P**, escriba **Python: Select Interpreter** y elija su Python 3.10 o superior.
4. Abra `main.py` (clic en el panel izquierdo).
5. Pulse el botón **▶ Run Python File** (arriba a la derecha) o presione **Ctrl + F5**.

### 5.3 Windows – Símbolo del sistema (CMD) o PowerShell

1. Abra la carpeta que contiene `main.py` en el Explorador de archivos.
2. Haga clic en la **barra de dirección** de arriba, escriba `cmd` y presione **Enter**. Se abre una consola ya ubicada en esa carpeta.
3. Escriba:

```bash
python main.py
```

Si `python` no funciona, use el lanzador de Windows:

```bash
py main.py
```

> También puede abrir la consola en cualquier lugar y moverse a la carpeta con `cd`, por ejemplo:
> `cd "C:\Users\SuUsuario\Desktop\IO1_Grupo9"`

### 5.4 macOS / Linux – Terminal

```bash
cd ruta/a/IO1_Grupo9
python3 main.py
```

### 5.5 Doble clic (Windows)

Si Python se instaló desde python.org, puede hacer **doble clic** sobre `main.py` (o clic derecho → **Abrir con → Python**). Si se abre y se cierra de inmediato, use la opción 6.3 para ver el mensaje de error.

### 5.6 IDLE (viene con Python)

1. Abra **IDLE** (búsquelo en el menú Inicio).
2. **File → Open…** → seleccione `main.py`.
3. Pulse **F5** (o **Run → Run Module**).


### 5.7 (Opcional) Entorno virtual desde la consola

No es obligatorio porque no hay dependencias, pero si prefiere aislar el proyecto:

| Paso | Windows | macOS / Linux |
|---|---|---|
| Crear entorno | `python -m venv .venv` | `python3 -m venv .venv` |
| Activarlo | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| Ejecutar | `python main.py` | `python main.py` |
| Salir | `deactivate` | `deactivate` |

### Resumen rápido

| Entorno | Cómo ejecutar |
|---|---|
| PyCharm | Clic derecho en `main.py` → **Run 'main'** |
| VS Code | Abrir `main.py` → **▶ Run Python File** / **Ctrl + F5** |
| CMD / PowerShell | `python main.py` o `py main.py` |
| Terminal macOS / Linux | `python3 main.py` |
| IDLE | Abrir `main.py` → **F5** |

---

## 6. Ejecutar las pruebas automáticas

El proyecto Usa `unittest`, que viene con Python (no hay que instalar nada). **Las pruebas no abren la ventana del programa**: solo muestran texto con el resultado.

### Cómo ejecutarlas

| Entorno | Cómo |
|---|---|
| **PyCharm** | Clic derecho sobre la carpeta **`tests`** → **Run 'Python tests in tests'**. Abajo debe decir **Tests passed** |
| **VS Code** | Ícono del matraz (**Testing**) → **Configure Python Tests** → **unittest** → carpeta **tests** → patrón `test_*.py` → ▶ **Run Tests** |
| **Consola** (en la carpeta del proyecto) | `python -m unittest discover -s tests -v` |

### Qué revisa cada archivo de pruebas

| Archivo | N.º | Qué comprueba |
|---|---|---|
| `test_numeros.py` | 4 | Lectura de números (`12`, `2,5`, `3/4`, `1e3`), rechazo de textos inválidos (`abc`, `1.250.000`, `3/0`) y el manejo del costo **M** |
| `test_simplex.py` | 9 | Maximización clásica (z = 36), minimización (z = −11), no acotado, óptimos alternativos, degeneración, que la solución cumpla las restricciones, tamaño máximo **8 × 8** y que **todos los ejemplos precargados** den el resultado esperado (incluido el caso real: **Z = 86.000**) |
| `test_sensibilidad.py` | 6 | Precios sombra, dualidad (Σ bᵢ·yᵢ = z), rangos de cⱼ y de bᵢ, sensibilidad en minimización y que exija una solución óptima |
| `test_validacion.py` | 6 | Campos vacíos, texto en vez de números, b negativo, más de 8 variables, nombres repetidos y signo ≥ no permitido |

---

## 7. Manual de uso del programa

### 7.1 Pantalla principal

| Zona | Función |
|---|---|
| **Barra lateral** | Navegar entre **Inicio**, **Simplex** y **Ayuda** |
| **Mostrar números como** | Ver los resultados en **fracciones** (5/3) o **decimales** (1.6667). Se actualiza todo al instante |
| **Franja de color** | Resumen del resultado (verde = óptimo, amarillo = caso especial, rojo = no acotado/infactible) |
| **Pestañas 1 a 6** | Datos, modelo, paso a paso, tablas, solución y sensibilidad |

### 7.2 Método Simplex – cómo ingresar un problema

1. En la barra lateral pulse **Simplex (max / min)** y quédese en la pestaña **1 · Datos**.
2. Para empezar de cero pulse **Limpiar**; para usar un ejemplo, elíjalo en **Ejemplos precargados** y pulse **Cargar ejemplo**.
3. Complete **1. Datos generales**:

| Campo | Qué escribir |
|---|---|
| Nombre del problema | Título del problema |
| Objetivo | **Maximizar** o **Minimizar** |
| ¿Qué mide z? | Qué representa la función objetivo |
| Unidad de z | Unidad de la función objetivo |
| Número de variables | De **1 a 8** |
| Número de restricciones | De **1 a 8** |

4. Complete **2. Modelo**:

| Fila / columna | Significado | Unidad |
|---|---|---|
| **Nombre de la variable** | Qué decide cada xⱼ | — |
| **Unidad** | Cómo se mide la variable | ej. lotes de 10 m³/semana |
| **cⱼ** | Aporte a z por **una** unidad de la variable | unidad de z por unidad de variable |
| **Nombre de la restricción** | Recurso que limita | — |
| **aᵢⱼ** | Cuánto del recurso i usa **una** unidad de la variable j (escriba **0** si no lo usa) | unidad del recurso por unidad de variable |
| **bᵢ (disponible)** | Cantidad disponible del recurso (debe ser **≥ 0**) | unidad del recurso |

5. Revise la **3. Vista previa del modelo matemático** (se actualiza mientras escribe).
6. Pulse **Resolver con Simplex ►** (o **Ctrl + Enter** / **F5**).

### 7.3 Método Simplex – pestañas de resultados

| Pestaña | Contenido |
|---|---|
| **2 · Modelo** | Modelo matemático, forma estándar con holguras y reglas del método |
| **3 · Paso a paso** | Cada tabla con **columna pivote** (azul), **fila pivote** (amarillo) y **elemento pivote** (naranja); explicación de Zj, Cj − Zj, variable que entra, razones, variable que sale y operaciones de fila. Botones **◄ Anterior / Siguiente ►** |
| **4 · Tablas** | Todas las tablas una debajo de otra |
| **5 · Solución** | Plan óptimo con nombres y unidades, uso de recursos, holguras, avisos de casos especiales y comprobación |
| **6 · Sensibilidad** | Precios sombra, costos reducidos, rangos de cada **cⱼ** y de cada **bᵢ**, matriz B⁻¹ y una frase de interpretación para cada uno |

### 7.4 Cómo escribir los números

| Se acepta | Ejemplo | No se acepta | Por qué |
|---|---|---|---|
| Enteros | `12`, `-3` | `1.250.000` | No use separador de miles: escriba `1250000` |
| Decimal con punto | `2.5` | `1,5.2` | Mezcla coma y punto |
| Decimal con coma | `2,5` | `abc` | No es un número |
| Fracción | `3/4` | `3/0` | División por cero |
| Notación científica | `1e3` | (vacío) | Toda casilla numérica debe tener un valor |

### 7.5 Botones y atajos

| Botón / atajo | Acción |
|---|---|
| **Cargar ejemplo** | Llena el formulario con el ejemplo elegido |
| **Abrir…** | Abre un problema guardado (`.json`) |
| **Guardar…** | Guarda el problema actual en `.json` |
| **Limpiar** | Borra el formulario |
| **Rellenar vacíos con 0** | Pone 0 en todas las casillas numéricas vacías |
| **Ctrl + Enter** o **F5** | Resolver |
| **Enter** | Pasar a la siguiente casilla |
| **F1** | Abrir la ayuda |
| **Shift + rueda del ratón** | Desplazar horizontalmente una tabla ancha |

---

## 8. Ejemplos precargados

Están en la carpeta `ejemplos/` como archivos `.json` (los datos nunca están dentro del código). Se cargan desde **Ejemplos precargados → Cargar ejemplo**.

### Simplex (`ejemplos/simplex/`)

| N.º | Ejemplo | Tipo |
|---|---|---|
| **01** | **Caso real: Cementos Argos – producción semanal de concreto** | Maximizar · 3 × 4 |
| 02 | Minimización del costo neto de tres mezclas | Minimizar · 3 × 3 |
| 03 | Caso especial: problema **NO ACOTADO** | Maximizar · 2 × 2 |
| 04 | Caso especial: **óptimos ALTERNATIVOS** | Maximizar · 2 × 2 |
| 05 | Caso especial: **DEGENERACIÓN** (empate en la razón mínima) | Maximizar · 2 × 2 |
| 06 | Prueba de **tamaño máximo 8 × 8** | Maximizar · 8 × 8 |

### Guardar un problema nuevo

Escriba los datos en la pestaña **1 · Datos**, pulse **Guardar…** y guárdelo en `ejemplos/simplex/`. Al guardarlo en esa carpeta aparecerá en la lista de ejemplos. **No hay que modificar el código.**

---

## 9. Estructura del proyecto

```
IO1_Grupo9/
├── main.py                         
├── README.md                          Guia
├── requirements.txt                   ── Archivo principal que se ejecuta para abrir el programa
│
├── modelo/                            ── MATEMÁTICA DE LOS MÉTODOS ──
│   ├── numeros.py                     Números exactos (fracciones) y costos con M
│   ├── excepciones.py                 Errores de validación y de archivos
│   ├── caso_especial.py               Avisos de casos especiales
│   ├── repositorio.py                 Leer y guardar problemas en JSON
│   ├── simplex/
│   │   ├── problema_pl.py             Clases del problema de PL
│   │   ├── validador_pl.py            Validación de datos del PL
│   │   ├── tabla_simplex.py           Tabla Simplex: Zj, Cj − Zj y pivoteo de Gauss-Jordan
│   │   ├── solver_simplex.py          MÉTODO SIMPLEX paso a paso
│   │   └── sensibilidad.py            Precios sombra, costos reducidos, rangos de cj y bi
│
├── vista/                             ── INTERFAZ GRÁFICA ──
│   ├── tema.py                        Colores, fuentes y estilos
│   ├── formato.py                     Formato fracción/decimal
│   ├── ventana_principal.py           Ventana, barra lateral y navegación
│   ├── vista_inicio.py                Pantalla de inicio
│   ├── vista_ayuda.py                 Ayuda dentro del programa
│   ├── componentes/                   Tablas, tarjetas, avisos
│   ├── explicaciones/                 Textos del paso a paso (Simplex y sensibilidad)
│   └── simplex/                       Pestañas del Método Simplex
│
├── controlador/                       ── CONEXIÓN VISTA ↔ MODELO ──
│   ├── controlador_principal.py       Crea la ventana y los atajos de teclado
│   └── controlador_simplex.py         Acciones del Simplex
│
├── ejemplos/                          ── DATOS ──
│   └── simplex/                       caso real Argos mas problemas de prueba
│
└── tests/                             ── PRUEBAS AUTOMÁTICAS ──
    ├── test_numeros.py
    ├── test_simplex.py
    ├── test_sensibilidad.py
    └── test_validacion.py
```
---

## 10. Declaración de uso de IA

El grupo declara que utilizó herramientas de inteligencia artificial únicamente como **apoyo**, no para resolver los métodos. 

El modelo matemático, la formulación del caso real, la lógica de los algoritmos, la interpretación de los resultados y las conclusiones son trabajo propio del grupo.

| Herramienta                                                            | Para qué se usó                                                                                                 | Cómo se verificó                                                                                                                                                  |
|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Asistente de IA (Claude)                                               | Sugerencias para estructurar el código en el patrón MVC y ayuda para redactar los comentarios y este manual (README). | El grupo revisó que la separación en Modelo, Vista y Controlador fuera correcta, reviso cada comentario, y comprobó que el README describe fielmente el proyecto. |
| Asistente de IA (Claude)                                               | Ayuda para identificar errores de ejecución (depuración) y para explicar mensajes de error de Python y PyCharm. | Se usó para identificar los errores que se presentaban al momento de escribir el código del software.                                                             |
| Validacion con Libro de Taha, *Investigación de Operaciones* (Pearson) | Referencia académica para comprobar que el software resuelve correctamente, usando ejercicios ya resueltos del libro. | El software coincidió con el libro: modelo Reddy Mikks (Simplex).                                                           |


---