"""
main.py - Sistema Integral de Gestión de Clientes, Servicios y Reservas
         Software FJ — Simulación de 10+ operaciones con manejo de excepciones.
"""

import sys
import os

# Aseguramos que los imports funcionen desde el directorio del proyecto
sys.path.insert(0, os.path.dirname(__file__))

import logger
from cliente import Cliente
from servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reserva import Reserva
from excepciones import (
    SoftwareFJError,
    DatosClienteInvalidosError,
    ParametroServicioInvalidoError,
    ReservaError,
    ReservaEstadoInvalidoError,
)


def titulo(texto: str):
    print(f"\n{'═'*60}")
    print(f"  {texto}")
    print(f"{'═'*60}")


def subtitulo(texto: str):
    print(f"\n  ── {texto}")


def resultado(ok: bool, detalle: str):
    icono = "✓" if ok else "✗"
    print(f"    [{icono}] {detalle}")


# ──────────────────────────────────────────────────────────────
# GESTOR DEL SISTEMA (almacena clientes, servicios y reservas)
# ──────────────────────────────────────────────────────────────
class GestorSistema:
    def __init__(self):
        self._clientes:  dict[str, Cliente]  = {}
        self._servicios: dict[str, object]   = {}
        self._reservas:  dict[str, Reserva]  = {}

    # ── Clientes ────────────────────────────────
    def registrar_cliente(self, nombre: str, email: str, telefono: str) -> Cliente | None:
        try:
            if email.lower().strip() in self._clientes:
                raise DatosClienteInvalidosError("email", f"'{email}' ya está registrado.")
            c = Cliente(nombre, email, telefono)
            self._clientes[c.identificador] = c
            resultado(True, f"Cliente registrado: {c.nombre} <{c.email}>")
            return c
        except SoftwareFJError as e:
            resultado(False, f"No se pudo registrar cliente: {e}")
            logger.error(f"Registro fallido de cliente ({email}): {e}", e)
            return None

    def obtener_cliente(self, email: str) -> Cliente | None:
        return self._clientes.get(email.lower().strip())

    # ── Servicios ───────────────────────────────
    def agregar_servicio(self, servicio) -> bool:
        try:
            servicio.validar()
            self._servicios[servicio.identificador] = servicio
            resultado(True, f"Servicio agregado: {servicio.describir()}")
            return True
        except SoftwareFJError as e:
            resultado(False, f"Servicio inválido: {e}")
            logger.error(f"Agregar servicio fallido: {e}", e)
            return False

    def obtener_servicio(self, id_servicio: str):
        return self._servicios.get(id_servicio)

    # ── Reservas ────────────────────────────────
    def crear_reserva(
        self, cliente: Cliente, servicio, duracion: float, **kwargs
    ) -> Reserva | None:
        try:
            r = Reserva(cliente, servicio, duracion, **kwargs)
            self._reservas[r.id_reserva] = r
            resultado(True, f"Reserva creada: {r.id_reserva}")
            return r
        except SoftwareFJError as e:
            resultado(False, f"No se pudo crear reserva: {e}")
            logger.error(f"Creación de reserva fallida: {e}", e)
            return None

    def obtener_reserva(self, id_reserva: str) -> Reserva | None:
        return self._reservas.get(id_reserva)

    def listar_reservas(self):
        if not self._reservas:
            print("    (No hay reservas en el sistema)")
            return
        for r in self._reservas.values():
            print(f"    • {r.describir()}")


# ──────────────────────────────────────────────────────────────
# SIMULACIÓN DE OPERACIONES
# ──────────────────────────────────────────────────────────────
def main():
    logger.separador("INICIO SIMULACIÓN SOFTWARE FJ")
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + "  SOFTWARE FJ — Sistema de Gestión Integral".center(58) + "║")
    print("║" + "  Simulación de operaciones con POO + Excepciones".center(58) + "║")
    print("╚" + "═"*58 + "╝")

    gestor = GestorSistema()

    # ══════════════════════════════════════════════════════════
    # BLOQUE 1: Registro de clientes (válidos e inválidos)
    # ══════════════════════════════════════════════════════════
    titulo("BLOQUE 1 — Registro de Clientes")

    subtitulo("Op 1: Registro de cliente válido")
    c1 = gestor.registrar_cliente("Ana García", "ana.garcia@softwarefj.co", "+57 310 1234567")

    subtitulo("Op 2: Registro de segundo cliente válido")
    c2 = gestor.registrar_cliente("Carlos Rodríguez", "carlos.r@empresa.com", "3001234567")

    subtitulo("Op 3: Email con formato inválido")
    gestor.registrar_cliente("Pedro Inválido", "no-es-un-email", "3009999999")

    subtitulo("Op 4: Nombre demasiado corto")
    gestor.registrar_cliente("X", "usuario@dominio.com", "3001111111")

    subtitulo("Op 5: Teléfono con caracteres inválidos")
    gestor.registrar_cliente("María López", "maria@correo.com", "abc-not-phone")

    subtitulo("Op 6: Email duplicado")
    gestor.registrar_cliente("Ana Duplicada", "ana.garcia@softwarefj.co", "+57 320 9876543")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 2: Creación de servicios
    # ══════════════════════════════════════════════════════════
    titulo("BLOQUE 2 — Creación de Servicios")

    subtitulo("Op 7: Sala de reuniones válida (10 personas)")
    sala1 = None
    try:
        sala1 = ReservaSala("SALA-01", "Sala Innovación", 80_000, capacidad=10)
        gestor.agregar_servicio(sala1)
    except SoftwareFJError as e:
        resultado(False, str(e))

    subtitulo("Op 8: Equipo de cómputo válido (stock=5)")
    equipo1 = None
    try:
        equipo1 = AlquilerEquipo("EQP-01", "Laptop HP Pro", 45_000, "Laptop", stock=5)
        gestor.agregar_servicio(equipo1)
    except SoftwareFJError as e:
        resultado(False, str(e))

    subtitulo("Op 9: Asesoría Senior en TI válida")
    asesoria1 = None
    try:
        asesoria1 = AsesoriaEspecializada(
            "ASES-01", "Consultoría TI", 120_000, area="Tecnología", nivel_asesor="senior"
        )
        gestor.agregar_servicio(asesoria1)
    except SoftwareFJError as e:
        resultado(False, str(e))

    subtitulo("Op 10: Servicio con precio negativo (error)")
    try:
        malo = ReservaSala("SALA-X", "Sala Inexistente", -500, capacidad=5)
    except ParametroServicioInvalidoError as e:
        resultado(False, f"Error esperado capturado: {e}")
        logger.error(f"Servicio con precio negativo rechazado: {e}")

    subtitulo("Op 11: Servicio con capacidad inválida (error)")
    try:
        malo2 = ReservaSala("SALA-Y", "Sala Gigante", 200_000, capacidad=999)
    except ParametroServicioInvalidoError as e:
        resultado(False, f"Error esperado capturado: {e}")
        logger.error(f"Sala con capacidad inválida rechazada: {e}")

    subtitulo("Op 12: Asesoría con nivel inexistente (error)")
    try:
        malo3 = AsesoriaEspecializada(
            "ASES-X", "Asesoría VIP", 300_000, area="Finanzas", nivel_asesor="dios"
        )
    except ParametroServicioInvalidoError as e:
        resultado(False, f"Error esperado capturado: {e}")
        logger.error(f"Asesoría con nivel inválido rechazada: {e}")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 3: Reservas (exitosas y fallidas)
    # ══════════════════════════════════════════════════════════
    titulo("BLOQUE 3 — Gestión de Reservas")

    if c1 and sala1:
        subtitulo("Op 13: Reserva de sala válida (Ana, 3 horas)")
        r1 = gestor.crear_reserva(c1, sala1, duracion=3)

        if r1:
            subtitulo("Op 14: Confirmar reserva con IVA y sin descuento")
            try:
                costo = r1.confirmar(aplicar_iva=True, descuento=0.0)
                resultado(True, f"Reserva confirmada. Costo con IVA: ${costo:,.2f}")
            except ReservaError as e:
                resultado(False, str(e))

            subtitulo("Op 15: Intentar confirmar la misma reserva dos veces (error)")
            try:
                r1.confirmar()
            except ReservaEstadoInvalidoError as e:
                resultado(False, f"Error esperado capturado: {e}")

            subtitulo("Op 16: Procesar reserva confirmada")
            try:
                r1.procesar()
                resultado(True, "Reserva procesada exitosamente un gustogir.")
            except ReservaError as e:
                resultado(False, str(e))

    if c2 and equipo1:
        subtitulo("Op 17: Reserva de equipo (Carlos, 7 días, 2 laptops)")
        r2 = gestor.crear_reserva(c2, equipo1, duracion=7, cantidad=2)

        if r2:
            subtitulo("Op 18: Confirmar con descuento del 10%")
            try:
                costo = r2.confirmar(aplicar_iva=True, descuento=0.10)
                resultado(True, f"Reserva confirmada. Costo con IVA y desc 10%: ${costo:,.2f}")
            except ReservaError as e:
                resultado(False, str(e))

            subtitulo("Op 19: Cancelar una reserva confirmada")
            try:
                r2.cancelar("Cliente cambió de equipo")
                resultado(True, f"Reserva {r2.id_reserva} cancelada.")
            except ReservaError as e:
                resultado(False, str(e))

            subtitulo("Op 20: Intentar procesar reserva cancelada (error)")
            try:
                r2.procesar()
            except ReservaEstadoInvalidoError as e:
                resultado(False, f"Error esperado capturado: {e}")

    if c1 and asesoria1:
        subtitulo("Op 21: Asesoría con duración inválida (0 horas)")
        r3 = gestor.crear_reserva(c1, asesoria1, duracion=0)

        subtitulo("Op 22: Asesoría válida (2.5 horas, Ana)")
        r4 = gestor.crear_reserva(c1, asesoria1, duracion=2.5)
        if r4:
            try:
                costo = r4.confirmar(aplicar_iva=False)
                resultado(True, f"Asesoría confirmada sin IVA. Costo: ${costo:,.2f}")
                r4.procesar()
                resultado(True, "Asesoría procesada.")
            except ReservaError as e:
                resultado(False, str(e))

    subtitulo("Op 23: Servicio no disponible")
    if sala1:
        sala1.disponible = False
        logger.advertencia(f"Servicio {sala1.identificador} marcado como no disponible.")
        if c2:
            r5 = gestor.crear_reserva(c2, sala1, duracion=2)
        sala1.disponible = True  # restaurar

    subtitulo("Op 24: Cliente inactivo intenta reservar")
    if c2 and equipo1:
        c2.desactivar()
        r6 = gestor.crear_reserva(c2, equipo1, duracion=3, cantidad=1)

    # ══════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ══════════════════════════════════════════════════════════
    titulo("RESUMEN — Estado del Sistema Revision")
    print(f"\n  Clientes registrados: {len(gestor._clientes)}")
    print(f"  Servicios en catálogo: {len(gestor._servicios)}")
    print(f"  Reservas en sistema:   {len(gestor._reservas)}")
    print("\n  Detalle de reservas:")
    gestor.listar_reservas()

    logger.separador("FIN SIMULACIÓN SOFTWARE FJ")
    print(f"\n  ✔ Simulación completada. Revisa 'logs.txt' para el registro completo.\n")


if __name__ == "__main__":
    main()
