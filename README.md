# NetAuto-MTTR

Prototipo de herramienta de autodiagnóstico para redes de última milla, desarrollado como proyecto de investigación y graduación de la **Maestría en Redes y Telecomunicaciones (UMG)**.

El sistema automatiza el diagnóstico de fallas en equipos CPE (adaptado al estándar Raisecom ROS/ROAP, con soporte de laboratorio sobre MikroTik vía SSH), correlacionando telemetría de Capa 1 (óptica SFP/DDM), Capa 2 (LLDP/MNDP) y Capa 3 (ICMP) para inferir la causa raíz de un incidente y decidir si corresponde o no el despacho de una cuadrilla técnica a sitio. El objetivo del proyecto es demostrar, de forma cuantitativa, la reducción del MTTR (Mean Time To Repair) frente al proceso de diagnóstico manual tradicional.

## Arquitectura del proyecto

El proyecto está organizado en fases secuenciales, cada una implementada como un script independiente:

| Archivo | Fase | Descripción |
|---|---|---|
| `fase1_setup_db.py` | 1 | Define el modelo de datos (SQLAlchemy) y crea/inicializa la base de datos SQLite con un equipo CPE de laboratorio. |
| `fase2_adaptador_telemetria.py` | 2 | Motor adaptador de telemetría: ejecuta un ciclo de autodiagnóstico (ICMP, DDM óptico, LLDP) sobre escenarios simulados (`healthy`, `attenuation`, `power_outage`) y persiste el resultado. |
| `fase3_api_rest.py` | 3 | Expone la lógica de diagnóstico como API RESTful (FastAPI), con endpoints de inventario, ejecución de diagnósticos, historial y métricas de MTTR. Incluye documentación Swagger/Redoc. |
| `fase4_motor_causa_raiz.py` | 4 | Motor de inferencia de causa raíz (RCA): valida una matriz de 4 escenarios de falla de última milla contra las reglas de decisión del sistema. |
| `fase5_validacion_mttr.py` | 5 | Validación estadística: compara muestras de MTTR preprueba (manual) vs. posprueba (automatizado) mediante prueba T de Student. |
| `fase6_servidor_web.py` | 6-7 | Servidor web (consola NOC): expone el dashboard (`static/index.html`), gestión de dispositivos/tickets y diagnósticos en vivo vía SSH contra equipos reales. |

### Modelo de datos (`netauto_laboratorio.db`)

- **`cpe_devices`**: inventario de equipos CPE (hostname, IP, vendor, modelo, firmware, interfaz WAN, ubicación).
- **`diagnostic_runs`**: histórico de ejecuciones de autodiagnóstico (telemetría de las 3 capas, veredicto de causa raíz y recomendación de despacho).
- **`mttr_tickets`**: muestras de tickets usadas para la validación estadística del MTTR (fase preprueba vs. posprueba).

## Tecnologías

- **Python 3**
- **FastAPI** + **Uvicorn** — servidor API REST
- **SQLAlchemy** — ORM y persistencia
- **SQLite** (motor de BD de laboratorio; compatible con PostgreSQL vía `DATABASE_URL`)
- **Paramiko** — conexión SSH para telemetría en vivo
- **NumPy** / **SciPy** — análisis estadístico inferencial
- **Pydantic** — validación de esquemas de la API
- Dashboard frontend: HTML + Bootstrap 5 (`static/index.html`)

## Instalación

```bash
pip install fastapi uvicorn sqlalchemy pydantic numpy scipy paramiko
```

> El proyecto no incluye un archivo `requirements.txt`; instala las dependencias anteriores según el entorno de pruebas que se vaya a ejecutar.

## Uso

Ejecutar las fases en orden, desde la raíz del proyecto:

```bash
# Fase 1: inicializar la base de datos
python fase1_setup_db.py

# Fase 2: ejecutar un ciclo de autodiagnóstico simulado
python fase2_adaptador_telemetria.py

# Fase 3: levantar el servidor API REST (http://127.0.0.1:8000/docs)
python fase3_api_rest.py

# Fase 4: ejecutar la matriz de escenarios de causa raíz
python fase4_motor_causa_raiz.py

# Fase 5: ejecutar la validación estadística del MTTR
python fase5_validacion_mttr.py

# Fase 6/7: levantar la consola NOC con dashboard (http://127.0.0.1:8000)
python fase6_servidor_web.py
```

La variable de entorno `DATABASE_URL` permite apuntar a otro motor de base de datos (por defecto usa `sqlite:///netauto_laboratorio.db`).

## Evidencias

El repositorio incluye capturas de pantalla de cada fase como evidencia del desarrollo:

- `Evidencia_Fase1_Base_de_Datos.png`
- `Evidencia_Fase2_Autodiagnostico_Raisecom.png`
- `Evidencia_Fase3_APi Restfull.png`
- `Evidencia_Fase3_Swagger_UI.png`
- `Evidencia_Fase4_Matriz_Causa_Raiz.png`
- `Evidencia_Fase6_Consola_NOC_Dashboard.png`
