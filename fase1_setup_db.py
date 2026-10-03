"""
==============================================================================
TESIS MAESTRÍA EN REDES Y TELECOMUNICACIONES - UMG
Fase 1: Configuración de Base de Datos y Persistencia para Autodiagnóstico
==============================================================================
Adaptado al protocolo oficial: Equipos Raisecom de Última Milla (CPE)
Motor de persistencia relacional: SQLite / PostgreSQL (entorno de pruebas)
"""

import os
import sys
import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    inspect
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_ENGINE_CHOICE = os.getenv("DATABASE_URL", "sqlite:///netauto_laboratorio.db")

print("=" * 80)
print("INICIANDO FASE 1: INICIALIZACIÓN DE MOTOR DE DATOS - NETAUTO MTTR (RAISECOM)")
print(f"Cadena de conexión activa: {DB_ENGINE_CHOICE}")
print("=" * 80)

Base = declarative_base()


class CpeDevice(Base):
    """
    TABLA 1: cpe_devices
    Representa la Población Técnica de la Investigación (Equipos Raisecom).
    """
    __tablename__ = "cpe_devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(80), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=False)
    vendor = Column(String(50), default="Raisecom")
    model = Column(String(60), default="ISCOM2600G-4C-EI")
    firmware_version = Column(String(40), default="ROS v5.4.1")
    wan_interface = Column(String(30), default="ge-1/1/1")
    site_location = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    diagnostics = relationship("DiagnosticRun", back_populates="device")

    def __repr__(self):
        return f"<CPE Raisecom {self.hostname} ({self.ip_address}) - Mod: {self.model}>"


class DiagnosticRun(Base):
    """
    TABLA 2: diagnostic_runs
    Operacionalización de la Variable Independiente (Herramienta de Autodiagnóstico).
    """
    __tablename__ = "diagnostic_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("cpe_devices.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Telemetría Capa 3
    icmp_loss_pct = Column(Float, nullable=False)
    latency_avg_ms = Column(Float, nullable=True)
    
    # Telemetría Capa 1 y 2
    sfp_rx_power_dbm = Column(Float, nullable=True)
    sfp_tx_power_dbm = Column(Float, nullable=True)
    interface_state = Column(String(20), nullable=False)
    crc_errors = Column(Integer, default=0)
    
    # Descubrimiento LLDP
    neighbor_lldp_identity = Column(String(100), nullable=True)
    neighbor_lldp_port = Column(String(50), nullable=True)
    
    # Causa Raíz (RCA) y Despacho
    root_cause_verdict = Column(String(150), nullable=False)
    dispatch_recommended = Column(Boolean, nullable=False)
    duration_seconds = Column(Float, nullable=False)

    device = relationship("CpeDevice", back_populates="diagnostics")


class MttrTicket(Base):
    """
    TABLA 3: mttr_tickets
    Operacionalización de la Variable Dependiente (MTTR - Preprueba vs Posprueba).
    """
    __tablename__ = "mttr_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_code = Column(String(30), unique=True, nullable=False)
    evaluation_phase = Column(String(25), nullable=False)
    incident_cause = Column(String(120), nullable=False)
    dispatch_status = Column(String(50), nullable=False)
    resolution_time_minutes = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def initialize_database():
    try:
        engine = create_engine(DB_ENGINE_CHOICE, echo=False)
        print("\n[*] Creando estructura de tablas relacionales para ecosistema Raisecom...")
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"[✓] Tablas verificadas exitosamente en la BD: {tables}")
        
        Session = sessionmaker(bind=engine)
        session = Session()

        existing_cpe = session.query(CpeDevice).filter_by(hostname="RAISECOM-ISCOM2600-01").first()
        if not existing_cpe:
            print("\n[*] Registrando dispositivo CPE Raisecom en inventario de laboratorio...")
            lab_cpe = CpeDevice(
                hostname="RAISECOM-ISCOM2600-01",
                ip_address="192.168.88.1",
                vendor="Raisecom",
                model="ISCOM2600G-4C-EI",
                firmware_version="ROS v5.4.1-Build2023",
                wan_interface="ge-1/1/1",
                site_location="Nodo Central / Laboratorio de Pruebas UMG",
                is_active=True
            )
            session.add(lab_cpe)
            session.commit()
            print(f"[✓] CPE Raisecom registrado: ID={lab_cpe.id} | Host: {lab_cpe.hostname} | Modelo: {lab_cpe.model}")

            print("\n[*] Insertando diagnóstico inicial automatizado...")
            test_run = DiagnosticRun(
                device_id=lab_cpe.id,
                icmp_loss_pct=0.0,
                latency_avg_ms=2.9,
                sfp_rx_power_dbm=-17.8,
                sfp_tx_power_dbm=-2.5,
                interface_state="UP",
                crc_errors=0,
                neighbor_lldp_identity="SW-AGR-PE-01",
                neighbor_lldp_port="TenGigabitEthernet1/1/14",
                root_cause_verdict="Enlace Óptico Operativo y Saludable",
                dispatch_recommended=False,
                duration_seconds=2.85
            )
            session.add(test_run)

            print("[*] Registrando ticket de muestra comparativa...")
            test_ticket = MttrTicket(
                ticket_code="TK-RAISECOM-01",
                evaluation_phase="posttest_automated",
                incident_cause="Corte de Energía Comercial en Sitio Cliente",
                dispatch_status="Prevenido (Falso Despacho Cancelado)",
                resolution_time_minutes=11.5
            )
            session.add(test_ticket)
            session.commit()

            print(f"[✓] Diagnóstico registrado: ID={test_run.id} | Veredicto: '{test_run.root_cause_verdict}'")
            print(f"[✓] Ticket MTTR registrado: Código={test_ticket.ticket_code} | MTTR={test_ticket.resolution_time_minutes} min")
        else:
            print(f"\n[i] El CPE Raisecom de laboratorio ya se encontraba registrado (ID: {existing_cpe.id}).")

        total_cpes = session.query(CpeDevice).count()
        total_diags = session.query(DiagnosticRun).count()
        total_tickets = session.query(MttrTicket).count()
        session.close()

        print("\n" + "=" * 80)
        print("RESUMEN FASE 1 COMPLETADA CON ÉXITO (ORIENTACIÓN OFICIAL RAISECOM):")
        print(f" - Dispositivos Raisecom en BD : {total_cpes}")
        print(f" - Pruebas diagnósticas        : {total_diags}")
        print(f" - Tickets MTTR almacenados    : {total_tickets}")
        print(f" - Estado de la arquitectura   : LISTO PARA ADAPTADOR DE TELEMETRÍA")
        print("=" * 80)

    except Exception as e:
        print(f"\n[!] Error durante la inicialización de la BD: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    initialize_database()