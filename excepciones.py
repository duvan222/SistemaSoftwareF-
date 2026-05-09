"""
excepciones.py - Excepciones personalizadas del sistema Software FJ
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


class ClienteError(SoftwareFJError):
    """Errores relacionados con la gestión de clientes."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE")


class ClienteNoEncontradoError(ClienteError):
    """El cliente buscado no existe en el sistema."""
    def __init__(self, identificador):
        super().__init__(f"Cliente '{identificador}' no encontrado en el sistema.")


class ClienteDuplicadoError(ClienteError):
    """Intento de registrar un cliente que ya existe."""
    def __init__(self, email: str):
        super().__init__(f"Ya existe un cliente registrado con el email '{email}'.")


class DatosClienteInvalidosError(ClienteError):
    """Datos del cliente no pasan validación."""
    def __init__(self, campo: str, detalle: str):
        super().__init__(f"Dato inválido en '{campo}': {detalle}")


class ServicioError(SoftwareFJError):
    """Errores relacionados con servicios."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO")


class ServicioNoDisponibleError(ServicioError):
    """El servicio solicitado no está disponible."""
    def __init__(self, nombre_servicio: str):
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible actualmente.")


class ServicioNoEncontradoError(ServicioError):
    """El servicio no existe en el sistema."""
    def __init__(self, identificador):
        super().__init__(f"Servicio '{identificador}' no encontrado.")


class ParametroServicioInvalidoError(ServicioError):
    """Parámetro inválido al configurar un servicio."""
    def __init__(self, parametro: str, detalle: str):
        super().__init__(f"Parámetro inválido '{parametro}': {detalle}")


class CalculoCostoError(ServicioError):
    """Error al calcular el costo de un servicio."""
    def __init__(self, detalle: str):
        super().__init__(f"Error en cálculo de costo: {detalle}")


class ReservaError(SoftwareFJError):
    """Errores relacionados con reservas."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RESERVA")


class ReservaNoEncontradaError(ReservaError):
    """La reserva buscada no existe."""
    def __init__(self, id_reserva: str):
        super().__init__(f"Reserva '{id_reserva}' no encontrada.")


class ReservaDuplicadaError(ReservaError):
    """Intento de crear una reserva duplicada."""
    def __init__(self, id_reserva: str):
        super().__init__(f"Ya existe una reserva con ID '{id_reserva}'.")


class ReservaEstadoInvalidoError(ReservaError):
    """Operación inválida según el estado actual de la reserva."""
    def __init__(self, estado_actual: str, operacion: str):
        super().__init__(
            f"No se puede '{operacion}' una reserva en estado '{estado_actual}'."
        )


class DuracionInvalidaError(ReservaError):
    """Duración inválida para una reserva."""
    def __init__(self, duracion, minimo=1):
        super().__init__(
            f"Duración inválida: {duracion}. Debe ser un número positivo >= {minimo}."
        )


class LogError(SoftwareFJError):
    """Error en el sistema de logging."""
    def __init__(self, detalle: str):
        super().__init__(f"Error en sistema de log: {detalle}", "ERR_LOG")
