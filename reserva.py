"""
reserva.py - Clase Reserva que integra Cliente, Servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo robusto de excepciones.
"""

import uuid
from enum import Enum
from datetime import datetime

from cliente import Cliente
from servicio import Servicio
from excepciones import (
    ReservaEstadoInvalidoError,
    DuracionInvalidaError,
    ServicioNoDisponibleError,
    CalculoCostoError,
    ReservaError,
)
import logger


class EstadoReserva(Enum):
    PENDIENTE   = "Pendiente"
    CONFIRMADA  = "Confirmada"
    CANCELADA   = "Cancelada"
    PROCESADA   = "Procesada"


class Reserva:
    """
    Representa una reserva de servicio para un cliente.
    Gestiona el ciclo de vida: Pendiente → Confirmada → Procesada / Cancelada.
    """

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        id_reserva: str = None,
        **kwargs_servicio
    ):
        # Validar cliente
        if not isinstance(cliente, Cliente):
            raise ReservaError("El parámetro 'cliente' debe ser instancia de Cliente.")
        if not cliente.activo:
            raise ReservaError(
                f"El cliente '{cliente.identificador}' está inactivo y no puede hacer reservas."
            )

        # Validar servicio
        if not isinstance(servicio, Servicio):
            raise ReservaError("El parámetro 'servicio' debe ser instancia de Servicio.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(servicio.identificador)

        # Validar duración
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DuracionInvalidaError(duracion)

        # Validar parámetros específicos del servicio (puede lanzar excepciones)
        try:
            servicio.validar_parametros(duracion, **kwargs_servicio)
        except Exception as e:
            raise ReservaError(
                f"Parámetros inválidos para el servicio '{servicio.identificador}': {e}"
            ) from e

        self._id_reserva      = id_reserva or str(uuid.uuid4())[:8].upper()
        self._cliente         = cliente
        self._servicio        = servicio
        self._duracion        = duracion
        self._kwargs_servicio = kwargs_servicio
        self._estado          = EstadoReserva.PENDIENTE
        self._fecha_creacion  = datetime.now()
        self._costo_total     = None
        self._notas           = []

        logger.info(
            f"Reserva {self._id_reserva} creada | "
            f"Cliente: {cliente.identificador} | Servicio: {servicio.identificador} | "
            f"Duración: {duracion}"
        )

    # ── Propiedades ────────────────────────────
    @property
    def id_reserva(self) -> str:
        return self._id_reserva

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def costo_total(self):
        return self._costo_total

    # ── Operaciones del ciclo de vida ──────────
    def confirmar(self, aplicar_iva: bool = True, descuento: float = 0.0) -> float:
        """
        Confirma la reserva y calcula el costo total.
        Usa try/except/else para manejar el cálculo de costo.
        """
        if self._estado != EstadoReserva.PENDIENTE:
            raise ReservaEstadoInvalidoError(self._estado.value, "confirmar")

        try:
            costo = self._servicio.calcular_costo_con_opciones(
                self._duracion,
                aplicar_iva=aplicar_iva,
                descuento=descuento,
                **self._kwargs_servicio,
            )
        except (CalculoCostoError, Exception) as e:
            logger.error(
                f"Error al calcular costo para reserva {self._id_reserva}: {e}", e
            )
            raise ReservaError(
                f"No se pudo confirmar la reserva {self._id_reserva}: {e}"
            ) from e
        else:
            self._costo_total = costo
            self._estado      = EstadoReserva.CONFIRMADA
            logger.info(
                f"Reserva {self._id_reserva} CONFIRMADA | "
                f"Costo: ${costo:,.2f} (IVA={aplicar_iva}, Desc={descuento*100:.0f}%)"
            )
            return costo
        finally:
            logger.info(f"Intento de confirmación para reserva {self._id_reserva} finalizado.")

    def cancelar(self, motivo: str = "Sin motivo especificado") -> None:
        """
        Cancela la reserva si está en estado Pendiente o Confirmada.
        Usa try/except/finally.
        """
        if self._estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
            raise ReservaEstadoInvalidoError(self._estado.value, "cancelar")
        try:
            self._estado = EstadoReserva.CANCELADA
            self._notas.append(f"Cancelada: {motivo}")
        except Exception as e:
            logger.error(f"Error inesperado al cancelar reserva {self._id_reserva}: {e}", e)
            raise
        finally:
            logger.advertencia(
                f"Reserva {self._id_reserva} CANCELADA | Motivo: {motivo}"
            )

    def procesar(self) -> None:
        """
        Marca la reserva como procesada (servicio entregado).
        Solo es posible desde estado Confirmada.
        Usa try/except/else/finally.
        """
        if self._estado != EstadoReserva.CONFIRMADA:
            raise ReservaEstadoInvalidoError(self._estado.value, "procesar")
        try:
            # Simulamos lógica de procesamiento
            if self._costo_total is None:
                raise ReservaError(
                    f"La reserva {self._id_reserva} no tiene costo calculado."
                )
        except ReservaError as e:
            logger.error(str(e), e)
            raise
        else:
            self._estado = EstadoReserva.PROCESADA
            logger.info(
                f"Reserva {self._id_reserva} PROCESADA exitosamente | "
                f"Costo final: ${self._costo_total:,.2f}"
            )
        finally:
            logger.info(f"Ciclo de procesamiento de reserva {self._id_reserva} finalizado.")

    # ── Representación ─────────────────────────
    def describir(self) -> str:
        costo_str = f"${self._costo_total:,.2f}" if self._costo_total else "No calculado"
        return (
            f"Reserva {self._id_reserva} [{self._estado.value}] | "
            f"Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.identificador} | "
            f"Duración: {self._duracion} | Costo: {costo_str}"
        )

    def __str__(self) -> str:
        return self.describir()
