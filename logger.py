"""
logger.py - Sistema de logging del proyecto Software FJ
Registra eventos y errores en logs.txt
"""

import os
import traceback
from datetime import datetime
from excepciones import LogError

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs.txt")


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _escribir(nivel: str, mensaje: str, exc: Exception = None) -> None:
    """Escribe una línea en el archivo de logs."""
    try:
        linea = f"[{_timestamp()}] [{nivel}] {mensaje}"
        if exc is not None:
            tb = traceback.format_exc()
            if tb and tb.strip() != "NoneType: None":
                linea += f"\n  Traceback:\n{tb}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
    except OSError as e:
        # Si no se puede escribir en el log, lanzamos excepción propia
        raise LogError(str(e)) from e


def info(mensaje: str) -> None:
    """Registra un evento informativo."""
    _escribir("INFO ", mensaje)
    print(f"  [LOG-INFO]  {mensaje}")


def advertencia(mensaje: str) -> None:
    """Registra una advertencia."""
    _escribir("WARN ", mensaje)
    print(f"  [LOG-WARN]  {mensaje}")


def error(mensaje: str, exc: Exception = None) -> None:
    """Registra un error, opcionalmente con traceback."""
    _escribir("ERROR", mensaje, exc)
    print(f"  [LOG-ERROR] {mensaje}")


def separador(titulo: str = "") -> None:
    """Escribe un separador visual en el log."""
    linea = "=" * 60
    if titulo:
        linea = f"{'='*20} {titulo} {'='*20}"
    _escribir("-----", linea)
