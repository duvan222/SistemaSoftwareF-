"""
servicio.py - Clase abstracta Servicio y tres servicios especializados:
  - ReservaSala
  - AlquilerEquipo
  - AsesoriaespecIalizada
"""

from abc import abstractmethod
from cliente import EntidadSistema
from excepciones import (
    ParametroServicioInvalidoError,
    ServicioNoDisponibleError,
    CalculoCostoError,
)
import logger


# ──────────────────────────────────────────────
# Clase Abstracta Servicio
# ──────────────────────────────────────────────
class Servicio(EntidadSistema):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.
    Define la interfaz común: calcular_costo(), disponible y validar_parametros().
    """

    IVA = 0.19  # 19% IVA Colombia

    def __init__(self, id_servicio: str, nombre: str, precio_base: float):
        if not id_servicio or not isinstance(id_servicio, str):
            raise ParametroServicioInvalidoError("id_servicio", "No puede estar vacío.")
        if not nombre or not isinstance(nombre, str):
            raise ParametroServicioInvalidoError("nombre", "No puede estar vacío.")
        if not isinstance(precio_base, (int, float)) or precio_base <= 0:
            raise ParametroServicioInvalidoError(
                "precio_base", f"Debe ser un número positivo, se recibió: {precio_base}"
            )
        self._id_servicio  = id_servicio.strip()
        self._nombre       = nombre.strip()
        self._precio_base  = float(precio_base)
        self._disponible   = True

    # ── Propiedades ────────────────────────────
    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):
        self._disponible = bool(valor)

    @property
    def precio_base(self) -> float:
        return self._precio_base

    # ── EntidadSistema ─────────────────────────
    @property
    def identificador(self) -> str:
        return self._id_servicio

    def validar(self) -> bool:
        if self._precio_base <= 0:
            raise ParametroServicioInvalidoError("precio_base", "Debe ser > 0.")
        return True

    # ── Métodos abstractos específicos ─────────
    @abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """
        Calcula el costo total del servicio.
        Implementa polimorfismo: cada subclase define su lógica.
        """

    @abstractmethod
    def validar_parametros(self, duracion: float, **kwargs) -> None:
        """Valida parámetros antes de calcular costo o confirmar reserva."""

    @abstractmethod
    def tipo_servicio(self) -> str:
        """Retorna el tipo legible del servicio."""

    # ── Método con sobrecarga simulada (kwargs) ─
    def calcular_costo_con_opciones(
        self,
        duracion: float,
        aplicar_iva: bool = True,
        descuento: float = 0.0,
        **kwargs
    ) -> float:
        """
        Variante sobrecargada de calcular_costo que acepta IVA y descuento.
        Demuestra sobrecarga de métodos con parámetros opcionales.
        """
        try:
            costo_base = self.calcular_costo(duracion, **kwargs)
            if not (0 <= descuento < 1):
                raise CalculoCostoError(
                    f"Descuento debe estar entre 0 y 1, se recibió: {descuento}"
                )
            costo = costo_base * (1 - descuento)
            if aplicar_iva:
                costo *= (1 + self.IVA)
            return round(costo, 2)
        except CalculoCostoError:
            raise
        except Exception as e:
            raise CalculoCostoError(str(e)) from e

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"{self.tipo_servicio()} [{estado}] | ID: {self._id_servicio} | "
            f"Nombre: {self._nombre} | Precio base/h: ${self._precio_base:,.0f}"
        )

    def __str__(self) -> str:
        return self.describir()


# ──────────────────────────────────────────────
# Servicio 1: Reserva de Sala
# ──────────────────────────────────────────────
class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión o eventos.
    El costo se calcula por hora; la capacidad es un parámetro.
    """

    CAPACIDADES_VALIDAS = [5, 10, 20, 50]  # personas

    def __init__(self, id_servicio: str, nombre: str, precio_base: float, capacidad: int):
        super().__init__(id_servicio, nombre, precio_base)
        if capacidad not in self.CAPACIDADES_VALIDAS:
            raise ParametroServicioInvalidoError(
                "capacidad",
                f"Debe ser uno de {self.CAPACIDADES_VALIDAS}, se recibió: {capacidad}."
            )
        self._capacidad = capacidad

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def tipo_servicio(self) -> str:
        return "ReservaSala"

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if not isinstance(duracion, (int, float)) or duracion < 1:
            raise ParametroServicioInvalidoError(
                "duracion", f"Para sala debe ser >= 1 hora. Recibido: {duracion}"
            )
        if duracion > 24:
            raise ParametroServicioInvalidoError(
                "duracion", "No se puede reservar una sala por más de 24 horas seguidas."
            )

    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """Costo = precio_base × horas. Horas adicionales tienen 10% de recargo."""
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre)
        self.validar_parametros(duracion)
        if duracion <= 8:
            return round(self._precio_base * duracion, 2)
        else:
            costo_primeras = self._precio_base * 8
            costo_extra    = self._precio_base * 1.10 * (duracion - 8)
            return round(costo_primeras + costo_extra, 2)

    def describir(self) -> str:
        return super().describir() + f" | Capacidad: {self._capacidad} personas"


# ──────────────────────────────────────────────
# Servicio 2: Alquiler de Equipo
# ──────────────────────────────────────────────
class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (laptops, proyectores, etc.).
    El costo se calcula por día; incluye tarifa por unidad.
    """

    def __init__(
        self, id_servicio: str, nombre: str, precio_base: float,
        tipo_equipo: str, stock: int
    ):
        super().__init__(id_servicio, nombre, precio_base)
        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ParametroServicioInvalidoError("tipo_equipo", "No puede estar vacío.")
        if not isinstance(stock, int) or stock < 0:
            raise ParametroServicioInvalidoError("stock", "Debe ser un entero >= 0.")
        self._tipo_equipo = tipo_equipo.strip()
        self._stock       = stock

    @property
    def stock(self) -> int:
        return self._stock

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    def tipo_servicio(self) -> str:
        return "AlquilerEquipo"

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        cantidad = kwargs.get("cantidad", 1)
        if not isinstance(duracion, (int, float)) or duracion < 1:
            raise ParametroServicioInvalidoError(
                "duracion", f"Debe ser >= 1 día. Recibido: {duracion}"
            )
        if not isinstance(cantidad, int) or cantidad < 1:
            raise ParametroServicioInvalidoError(
                "cantidad", f"Debe ser entero >= 1. Recibido: {cantidad}"
            )
        if cantidad > self._stock:
            raise ParametroServicioInvalidoError(
                "cantidad",
                f"Stock insuficiente. Disponible: {self._stock}, solicitado: {cantidad}."
            )

    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """Costo = precio_base × días × cantidad. Descuento del 5% desde 7 días."""
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre)
        cantidad = kwargs.get("cantidad", 1)
        self.validar_parametros(duracion, cantidad=cantidad)
        costo = self._precio_base * duracion * cantidad
        if duracion >= 7:
            costo *= 0.95  # 5% descuento por semana completa
        return round(costo, 2)

    def reducir_stock(self, cantidad: int):
        if cantidad > self._stock:
            raise ParametroServicioInvalidoError(
                "stock", f"No hay suficiente stock ({self._stock}) para reducir {cantidad}."
            )
        self._stock -= cantidad

    def describir(self) -> str:
        return super().describir() + f" | Equipo: {self._tipo_equipo} | Stock: {self._stock}"


# ──────────────────────────────────────────────
# Servicio 3: Asesoría Especializada
# ──────────────────────────────────────────────
class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría técnica o empresarial.
    El costo varía según el nivel del asesor (Junior, Senior, Expert).
    """

    NIVELES = {
        "junior":  1.0,
        "senior":  1.5,
        "experto": 2.0,
    }

    def __init__(
        self, id_servicio: str, nombre: str, precio_base: float,
        area: str, nivel_asesor: str
    ):
        super().__init__(id_servicio, nombre, precio_base)
        if not area:
            raise ParametroServicioInvalidoError("area", "El área de asesoría no puede estar vacía.")
        nivel = nivel_asesor.lower().strip() if isinstance(nivel_asesor, str) else ""
        if nivel not in self.NIVELES:
            raise ParametroServicioInvalidoError(
                "nivel_asesor",
                f"Debe ser uno de {list(self.NIVELES.keys())}. Recibido: '{nivel_asesor}'."
            )
        self._area         = area.strip()
        self._nivel_asesor = nivel

    @property
    def nivel_asesor(self) -> str:
        return self._nivel_asesor

    @property
    def area(self) -> str:
        return self._area

    def tipo_servicio(self) -> str:
        return "AsesoriaEspecializada"

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if not isinstance(duracion, (int, float)) or duracion < 0.5:
            raise ParametroServicioInvalidoError(
                "duracion", f"Mínimo 0.5 horas (30 min). Recibido: {duracion}"
            )
        if duracion > 8:
            raise ParametroServicioInvalidoError(
                "duracion", "Máximo 8 horas por sesión de asesoría."
            )

    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """Costo = precio_base × multiplicador_nivel × horas."""
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre)
        self.validar_parametros(duracion)
        multiplicador = self.NIVELES[self._nivel_asesor]
        return round(self._precio_base * multiplicador * duracion, 2)

    def describir(self) -> str:
        return (
            super().describir()
            + f" | Área: {self._area} | Nivel: {self._nivel_asesor.capitalize()}"
        )
