"""
cliente.py - Clase Cliente con encapsulación, validaciones robustas y clase abstracta base.
"""

import re
from abc import ABC, abstractmethod
from excepciones import DatosClienteInvalidosError, ClienteError
import logger


# ──────────────────────────────────────────────
# Clase Abstracta Base del sistema
# ──────────────────────────────────────────────
class EntidadSistema(ABC):
    """
    Clase abstracta que representa cualquier entidad registrable en Software FJ.
    Obliga a implementar: identificador, describir() y validar().
    """

    @property
    @abstractmethod
    def identificador(self) -> str:
        """Retorna el identificador único de la entidad."""

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción textual de la entidad."""

    @abstractmethod
    def validar(self) -> bool:
        """Valida la integridad de los datos de la entidad."""

    def __str__(self) -> str:
        return self.describir()


# ──────────────────────────────────────────────
# Clase Cliente
# ──────────────────────────────────────────────
class Cliente(EntidadSistema):
    """
    Representa un cliente de Software FJ.
    Encapsula nombre, email y teléfono con validaciones estrictas.
    """

    _PATRON_EMAIL = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.IGNORECASE)
    _PATRON_TEL   = re.compile(r"^\+?[\d\s\-]{7,15}$")

    def __init__(self, nombre: str, email: str, telefono: str):
        # Usamos setters para validar en construcción
        self.nombre    = nombre
        self.email     = email
        self.telefono  = telefono
        self._activo   = True
        logger.info(f"Cliente creado: {self._email} — {self._nombre}")

    # ── Propiedades ────────────────────────────
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        valor = valor.strip() if isinstance(valor, str) else ""
        if not valor or len(valor) < 2:
            raise DatosClienteInvalidosError("nombre", "Debe tener al menos 2 caracteres.")
        if len(valor) > 100:
            raise DatosClienteInvalidosError("nombre", "No puede superar 100 caracteres.")
        self._nombre = valor

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        valor = valor.strip().lower() if isinstance(valor, str) else ""
        if not self._PATRON_EMAIL.match(valor):
            raise DatosClienteInvalidosError("email", f"Formato inválido: '{valor}'.")
        self._email = valor

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        valor = valor.strip() if isinstance(valor, str) else ""
        if not self._PATRON_TEL.match(valor):
            raise DatosClienteInvalidosError(
                "telefono", f"Formato inválido: '{valor}'. Use solo dígitos, espacios o guiones."
            )
        self._telefono = valor

    @property
    def activo(self) -> bool:
        return self._activo

    # ── EntidadSistema ─────────────────────────
    @property
    def identificador(self) -> str:
        return self._email

    def describir(self) -> str:
        estado = "Activo" if self._activo else "Inactivo"
        return (
            f"Cliente [{estado}] | Nombre: {self._nombre} | "
            f"Email: {self._email} | Tel: {self._telefono}"
        )

    def validar(self) -> bool:
        try:
            assert len(self._nombre) >= 2, "Nombre muy corto"
            assert self._PATRON_EMAIL.match(self._email), "Email inválido"
            assert self._PATRON_TEL.match(self._telefono), "Teléfono inválido"
            return True
        except AssertionError as e:
            raise ClienteError(f"Validación fallida para {self._email}: {e}") from e

    # ── Operaciones ────────────────────────────
    def desactivar(self):
        """Desactiva el cliente (baja lógica)."""
        self._activo = False
        logger.advertencia(f"Cliente desactivado: {self._email}")

    def actualizar_telefono(self, nuevo_tel: str):
        self.telefono = nuevo_tel
        logger.info(f"Teléfono actualizado para {self._email}: {self._telefono}")
