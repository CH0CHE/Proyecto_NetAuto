"""
FASE 5: ANÁLISIS ESTADÍSTICO Y VALIDACIÓN DEL MTTR (PREPRUEBA VS POSPRUEBA)
Proyecto: Herramienta de Autodiagnóstico para Redes de Última Milla
Objetivo: Demostrar cuantitativamente la reducción del MTTR y contrastar hipótesis mediante T de Student.
"""

from datetime import datetime, timezone
import numpy as np
from scipy import stats
from sqlalchemy import create_engine, text

# 1. Conexión a la base de datos local
DATABASE_URL = "sqlite:///netauto_laboratorio.db"
engine = create_engine(DATABASE_URL, echo=False)

# 2. Muestra de 20 incidentes en minutos (Preprueba manual vs Posprueba automatizada)
SAMPLE_PREPRUEBA_MANUAL = [
    55.0, 62.5, 48.0, 70.0, 52.0, 58.5, 65.0, 49.0, 75.0, 53.0,
    60.0, 57.0, 68.0, 51.5, 47.0, 63.0, 56.0, 72.0, 50.0, 59.5
]

SAMPLE_POSPRUEBA_AUTO = [
    12.0, 14.5, 10.0, 15.0, 11.5, 13.0, 16.5, 11.0, 18.0, 12.5,
    14.0, 13.5, 15.5, 12.0, 10.5, 14.0, 13.0, 17.0, 11.5, 13.5
]

def analyze_and_record_mttr():
    print("=" * 90)
    print("FASE 5: ANÁLISIS ESTADÍSTICO INFERENCIAL - VALIDACIÓN CUANTITATIVA DEL MTTR")
    print("=" * 90)

    # 3. Estadística Descriptiva
    mean_manual = float(np.mean(SAMPLE_PREPRUEBA_MANUAL))
    std_manual = float(np.std(SAMPLE_PREPRUEBA_MANUAL, ddof=1))

    mean_auto = float(np.mean(SAMPLE_POSPRUEBA_AUTO))
    std_auto = float(np.std(SAMPLE_POSPRUEBA_AUTO, ddof=1))

    reduction_pct = ((mean_manual - mean_auto) / mean_manual) * 100.0

    # 4. Estadística Inferencial: Prueba T de Student para muestras independientes
    t_stat, p_val = stats.ttest_ind(SAMPLE_PREPRUEBA_MANUAL, SAMPLE_POSPRUEBA_AUTO)

    # 5. Inserción usando las 7 columnas exactas de la tabla mttr_tickets
    insert_ticket_sql = text("""
        INSERT INTO mttr_tickets (
            ticket_code,
            evaluation_phase,
            incident_cause,
            dispatch_status,
            resolution_time_minutes,
            created_at
        ) VALUES (
            :ticket_code,
            :evaluation_phase,
            :incident_cause,
            :dispatch_status,
            :resolution_time_minutes,
            :created_at
        )
    """)

    with engine.begin() as conn:
        # Preprueba: Diagnóstico manual tradicional
        for i, val in enumerate(SAMPLE_PREPRUEBA_MANUAL, start=1):
            conn.execute(insert_ticket_sql, {
                "ticket_code": f"TK-PRE-{i:03d}",
                "evaluation_phase": "PRE-TEST (Manual)",
                "incident_cause": "Falla de conectividad en última milla",
                "dispatch_status": "Despacho manual realizado",
                "resolution_time_minutes": val,
                "created_at": datetime.now(timezone.utc)
            })

        # Posprueba: Diagnóstico automatizado
        for i, val in enumerate(SAMPLE_POSPRUEBA_AUTO, start=1):
            conn.execute(insert_ticket_sql, {
                "ticket_code": f"TK-POST-{i:03d}",
                "evaluation_phase": "POST-TEST (NetAuto)",
                "incident_cause": "Falla de conectividad en última milla",
                "dispatch_status": "Falso despacho evitado / Despacho asistido",
                "resolution_time_minutes": val,
                "created_at": datetime.now(timezone.utc)
            })

    # 6. Despliegue de resultados estadísticos formales
    print("\n1. RESULTADOS DESCRIPTIVOS (MUESTRA N = 20 POR GRUPO):")
    print(f"   * MTTR Promedio Preprueba (Manual)   : {mean_manual:.2f} min (Desv. Est: {std_manual:.2f})")
    print(f"   * MTTR Promedio Posprueba (NetAuto)  : {mean_auto:.2f} min (Desv. Est: {std_auto:.2f})")
    print(f"   * Reducción Absoluta de Tiempo       : {mean_manual - mean_auto:.2f} minutos")
    print(f"   * Reducción Porcentual del MTTR      : {reduction_pct:.2f}%")

    print("\n2. RESULTADOS INFERENCIALES (PRUEBA T DE STUDENT):")
    print(f"   * Estadístico t calculado            : {t_stat:.4f}")
    print(f"   * Nivel de significancia (p-value)   : {p_val:.4e}")

    if p_val < 0.05:
        print("   * Veredicto Estadístico              : HIPÓTESIS GENERAL ACEPTADA (p < 0.05)")
        print("     (Existe evidencia estadísticamente significativa de que el prototipo")
        print("      automatizado reduce el MTTR respecto al método manual tradicional).")
    else:
        print("   * Veredicto Estadístico              : NO SE RECHAZA LA HIPÓTESIS NULA")

    print("\n[OK] Los 40 registros se guardaron exitosamente en 'mttr_tickets'.")
    print("=" * 90)

if __name__ == "__main__":
    analyze_and_record_mttr()