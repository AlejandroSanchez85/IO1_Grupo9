"""
main.py — Punto de entrada del programa.

Proyecto final · Investigación de Operaciones 1 · Grupo 9
Método: Simplex (maximizar / minimizar).

Ejecutar:  python main.py      (en PyCharm: clic derecho sobre main.py → Run 'main')
"""
import importlib.util
import sys


def configurar_pantalla_windows() -> None:
    """En Windows evita que la ventana se vea borrosa en pantallas con escala (125 %, 150 %...)."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


def main() -> None:
    if sys.version_info < (3, 9):
        print("Este programa necesita Python 3.9 o superior. Versión actual:", sys.version)
        return
    if importlib.util.find_spec("tkinter") is None:          # Tkinter viene incluido con Python
        print("No se encontró Tkinter. Instale Python desde python.org marcando la opción 'tcl/tk and IDLE'.")
        return
    configurar_pantalla_windows()
    from controlador import ControladorPrincipal
    ControladorPrincipal().iniciar()


if __name__ == "__main__":
    main()
