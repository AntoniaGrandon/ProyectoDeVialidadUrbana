
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ══════════════════════════════════════════════════════════════════════════════
# CELDA 1 — PARÁMETROS GLOBALES DEL MODELO
# Todos los valores ajustados al Informe NABC del Grupo 7
# ══════════════════════════════════════════════════════════════════════════════

# ── Lugar de estudio ──────────────────────────────────────────────────────────
PLACE = 'San Miguel, Región Metropolitana, Chile'

# ── Parámetros económicos (notebook base del profesor) ───────────────────────
TASA_SOCIAL        = 0.06       # Tasa social MIDEPLAN (6%)
VALOR_TIEMPO_UF_H  = 0.005      # Valor tiempo en UF/hora (SECTRA)
DIAS_LABORALES_MES = 22         # Días laborables por mes
PRESUPUESTO_CLP    = 2_500_000_000  # Presupuesto comunal: 2.500 M CLP
UF_A_CLP           = 40_000     # CLP por UF (cmfchile.cl)
TIPO_CAMBIO_USD    = 950        # CLP por USD (bcentral.cl)

# ── Parámetros operacionales ──────────────────────────────────────────────────
CUADRILLAS_TOTAL   = 4          # Cuadrillas disponibles
ANCHO_PROMEDIO_M   = 7.0        # Ancho promedio calzada (m)

# ── Costos unitarios MOP 2025-2026 (mismos del notebook base) ────────────────
COSTOS_UNITARIOS = {
    'repavimentacion': 8_500,   # CLP/m²
    'ciclovía':       12_000,   # CLP/m²
    'señalización':    1_200,   # CLP/m²
    'iluminación':     3_500,   # CLP/m lineal
}

# ── Parámetros específicos del Tramo 7 (Informe NABC Grupo 7) ────────────────
# Fuente: Censo 2024 (BCN San Miguel) + diagnóstico Controles 2 y 3
LONGITUD_KM       = 4.0         # Longitud real del Tramo 7 (km)
ANCHO_VEREDA_M    = 4.0         # Ancho total de veredas (2 m c/lado)

# Datos comunales actualizados al Censo 2024
DATA_COMUNAL = {
    'poblacion_2024':          150_829,  # Censo 2024 (BCN)
    'poblacion_2017':          107_954,  # Censo 2017 (INE)
    'crecimiento_pct':            39.7,  # % crecimiento 2017-2024
    'adultos_mayores_65':       17_323,  # personas (Censo 2024)
    'pct_adultos_mayores':        11.5,  # % del total
    'adultos_discapacidad_est': 23_116,  # estimado: adultos × 19.1% RM (SENADIS 2023)
    'personas_no_videntes_est':  1_210,  # estimado: adultos × 1.0% (ENDIDE 2022)
    'densidad_vial_pct':          14.9,  # % superficie vial / área comunal (PRC)
    'trafico_exogeno_pct':          80,  # % tráfico de otras comunas (SECTRA)
    'accidentes_2024':           1_245,  # accidentes viales 2024 (CONASET)
    'red_km_comunal':              130,  # km red vial comunal estimada
    'estaciones_metro':              9,  # estaciones L2
}

print("✅ Parámetros del Tramo 7 — Grupo 7 cargados")
print(f"\n  Lugar              : {PLACE}")
print(f"  Longitud tramo     : {LONGITUD_KM} km")
print(f"  Población 2024     : {DATA_COMUNAL['poblacion_2024']:,} hab. (Censo 2024)")
print(f"  Crecimiento 17-24  : +{DATA_COMUNAL['crecimiento_pct']}%")
print(f"  Adultos mayores    : {DATA_COMUNAL['adultos_mayores_65']:,} personas")
print(f"  Adultos c/ discap. : ~{DATA_COMUNAL['adultos_discapacidad_est']:,} personas estimadas")
print(f"  Accidentes 2024    : {DATA_COMUNAL['accidentes_2024']:,}")
print(f"  Tasa social        : {TASA_SOCIAL*100:.0f}% (MIDEPLAN)")
print(f"  Presupuesto comunal: ${PRESUPUESTO_CLP/1e9:.2f} mil millones CLP")


# ══════════════════════════════════════════════════════════════════════════════
# N — NEED / DIAGNÓSTICO
# ICV Multicriterio del Tramo 7 (fuente: Control 2 y 3 del Grupo 7)
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("N — NEED: DIAGNÓSTICO DEL TRAMO 7")
print("="*65)

# ICV actual (Tabla 4.3 del Informe Control 2 y 3)
dimensiones_icv = pd.DataFrame({
    'Dimensión': [
        'Seguridad peatonal',
        'Accesibilidad universal',
        'Infraestructura peatonal',
        'Movilidad activa',
        'Iluminación y seguridad urbana',
    ],
    'Peso': [0.30, 0.25, 0.20, 0.15, 0.10],
    'Puntaje_actual': [2, 2, 2, 1, 1],
    'Puntaje_post':   [4, 4, 4, 1, 1],  # solo 3 dimensiones priorizadas mejoran
    'Problema_asociado': [
        'Elementos que obstruyen cruces (③)',
        'Cruces con accesibilidad incompleta (②)',
        'Veredas en mal estado (①)',
        'Sin intervención en esta fase',
        'Sin intervención en esta fase',
    ],
})

dimensiones_icv['Resultado_actual']  = dimensiones_icv['Peso'] * dimensiones_icv['Puntaje_actual']
dimensiones_icv['Resultado_post']    = dimensiones_icv['Peso'] * dimensiones_icv['Puntaje_post']
dimensiones_icv['Delta_ponderado']   = dimensiones_icv['Resultado_post'] - dimensiones_icv['Resultado_actual']

ICV_ACTUAL = dimensiones_icv['Resultado_actual'].sum()
ICV_POST   = dimensiones_icv['Resultado_post'].sum()
ICV_DELTA  = ICV_POST - ICV_ACTUAL
ICV_MEJORA_PCT = ICV_DELTA / ICV_ACTUAL * 100

print("\nICV Multicriterio — Tramo 7, Gran Avenida, San Miguel")
print("(Fuente: Control 2 y 3, Tabla 4.3)\n")
print(dimensiones_icv[['Dimensión','Peso','Puntaje_actual','Puntaje_post','Delta_ponderado','Problema_asociado']].to_string(index=False))
print(f"\n  ICV actual             : {ICV_ACTUAL:.2f} / 5,00  → Condición DEFICIENTE")
print(f"  ICV post intervención  : {ICV_POST:.2f} / 5,00  → Condición REGULAR-ALTA")
print(f"  Mejora absoluta        : +{ICV_DELTA:.2f} puntos")
print(f"  Mejora relativa        : +{ICV_MEJORA_PCT:.0f}%")
print(f"\n  Las 3 dimensiones priorizadas pesan el 75% del ICV (30+25+20%).")

# Usuarios vulnerables beneficiados (Tabla 2.2 del Informe NABC)
print("\n  Usuarios vulnerables beneficiados (Tramo 7):")
print(f"    Adultos mayores 65+     : {DATA_COMUNAL['adultos_mayores_65']:,} personas (Censo 2024)")
print(f"    Adultos c/ discap. est. : {DATA_COMUNAL['adultos_discapacidad_est']:,} personas (SENADIS 2023, 19.1% RM)")
print(f"    No videntes estimados   : {DATA_COMUNAL['personas_no_videntes_est']:,} personas (ENDIDE 2022, 1.0%)")
print(f"    Usuarios diarios tramo  : 20.000 usuarios/día (5.000/día·km × 4 km)")
print(f"    Desplazamientos/año     : 7,3 millones de viajes potencialmente beneficiados")


# ══════════════════════════════════════════════════════════════════════════════
# A — APPROACH / COSTOS DE INTERVENCIÓN
# Adaptado de Celda 9 del notebook base
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("A — APPROACH: COSTOS DE INTERVENCIÓN")
print("="*65)

# ── Cantidades ────────────────────────────────────────────────────────────────
AREA_VEREDA_M2     = LONGITUD_KM * 1000 * ANCHO_VEREDA_M   # 16.000 m²
N_CRUCES           = 10      # cruces accesibles a rediseñar
COSTO_CRUCE_CLP    = 12_000_000   # CLP/cruce (rebaje + podotáctil + demarcación)
N_OBSTACULOS       = 30      # puntos de retiro/reubicación
COSTO_OBSTACULO_CLP = 1_500_000  # CLP/punto
AREA_SEÑALIZACION_M2 = LONGITUD_KM * 1000 * ANCHO_PROMEDIO_M  # 28.000 m²

# ── Costos por ítem (escenario base del curso + cruces + obstáculos) ──────────
costo_veredas      = AREA_VEREDA_M2 * COSTOS_UNITARIOS['repavimentacion']
costo_cruces       = N_CRUCES * COSTO_CRUCE_CLP
costo_obstaculos   = N_OBSTACULOS * COSTO_OBSTACULO_CLP
costo_señalizacion = AREA_SEÑALIZACION_M2 * COSTOS_UNITARIOS['señalización']

subtotal           = costo_veredas + costo_cruces + costo_obstaculos + costo_señalizacion
contingencia_15pct = subtotal * 0.15
COSTO_TOTAL_BASE   = subtotal + contingencia_15pct

# Escenario benchmark municipal ($97.000/m² referencia Sector 4-A San Miguel)
COSTO_UNITARIO_BENCHMARK = 97_000  # CLP/m² (proyecto municipal real)
costo_bench_veredas      = AREA_VEREDA_M2 * COSTO_UNITARIO_BENCHMARK
costo_bench_subtotal     = costo_bench_veredas + costo_cruces + costo_obstaculos + costo_señalizacion
COSTO_TOTAL_BENCHMARK    = costo_bench_subtotal * 1.15

# ── Programación de obras ─────────────────────────────────────────────────────
RENDIMIENTO_M2_DIA = 50   # m²/día por cuadrilla (idéntico al notebook base)
dias_veredas       = AREA_VEREDA_M2 / (RENDIMIENTO_M2_DIA * CUADRILLAS_TOTAL)
meses_veredas      = dias_veredas / DIAS_LABORALES_MES

tabla_costos = pd.DataFrame({
    'Ítem': [
        'Rehabilitación de veredas',
        'Cruces accesibles (10 cruces)',
        'Retiro/reubicación obstáculos (30 puntos)',
        'Señalización y demarcación',
        'Subtotal',
        'Contingencia 15%',
        'TOTAL ESTIMADO',
    ],
    'Cantidad / cálculo': [
        f'{AREA_VEREDA_M2:,.0f} m² (4 m × 4.000 m)',
        f'{N_CRUCES} cruces × ${COSTO_CRUCE_CLP/1e6:.1f} M',
        f'{N_OBSTACULOS} puntos × ${COSTO_OBSTACULO_CLP/1e6:.1f} M',
        f'{AREA_SEÑALIZACION_M2:,.0f} m² × $1.200/m²',
        '—', '15% del subtotal', '—',
    ],
    'Costo base (M CLP)': [
        costo_veredas/1e6,
        costo_cruces/1e6,
        costo_obstaculos/1e6,
        costo_señalizacion/1e6,
        subtotal/1e6,
        contingencia_15pct/1e6,
        COSTO_TOTAL_BASE/1e6,
    ],
    'Problema que resuelve': [
        '① Veredas en mal estado',
        '② Cruces c/ acc. incompleta',
        '③ Elementos que obstruyen',
        'Cruces y seguridad peatonal',
        '—', '—', '—',
    ],
})

print("\nDesglose de costos (escenario base — costos unitarios notebook + cruces + obstáculos):\n")
print(tabla_costos.to_string(index=False, float_format=lambda x: f"${x:,.1f}"))
print(f"\n  Escenario benchmark alto ($97.000/m²) : ${COSTO_TOTAL_BENCHMARK/1e6:,.1f} M CLP")
print(f"  (Referencia: Proyecto Recambio Veredas Sector 4-A, San Miguel 2025)")
print(f"\n  Relación con presupuesto municipal 2025:")
print(f"    Costo base / presupuesto disponible (5.591,9 M) : {COSTO_TOTAL_BASE/5591.9e6*100:.1f}%")
print(f"    Costo base / monto adjudicado (3.847,9 M)       : {COSTO_TOTAL_BASE/3847.9e6*100:.1f}%")
print(f"\n  Programación (veredas, 4 cuadrillas):")
print(f"    Área a intervenir  : {AREA_VEREDA_M2:,.0f} m²")
print(f"    Días laborales     : {dias_veredas:.0f} días")
print(f"    Plazo estimado     : {meses_veredas:.1f} meses laborales (~{meses_veredas*1.2:.0f} meses calendario)")


# ══════════════════════════════════════════════════════════════════════════════
# B — BENEFIT / EVALUACIÓN ECONÓMICA SOCIAL
# Basado en la función evaluar_proyecto() de la Celda B1 del notebook base,
# adaptada con el escenario conservador del Informe NABC Grupo 7
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("B — BENEFIT: EVALUACIÓN ECONÓMICA SOCIAL")
print("="*65)

HORIZONTE_ANOS  = 20           # años (estándar MIDEPLAN)
COSTO_ACC_CLP   = 50_000_000   # Costo social por accidente (MIDEPLAN)
REDUCCION_ACC   = 0.25         # Reducción esperada de accidentes (25%)
USUARIOS_DIA_KM = 5_000        # Usuarios/día·km (EOD SECTRA)
AHORRO_MIN_KM   = 1.2          # Minutos ahorrados por km intervenido

# ── Beneficios anuales (escenario conservador del Informe NABC) ───────────────
# El informe aplica factores de descuento para no sobreestimar:
#   - 60% de la reducción de accidentes (solo impacto peatonal)
#   - 50% del ahorro de tiempo (solo beneficio peatonal, excluye vehículos)
#   - Se excluye COV vehicular (la intervención es peatonal)
FACTOR_ACC_CONSERVADOR    = 0.60   # 60% del beneficio total de accidentes
FACTOR_TIEMPO_CONSERVADOR = 0.50   # 50% del ahorro de tiempo

# Beneficio 1: Ahorro en tiempo de viaje (50% escenario conservador)
usuarios_dia   = USUARIOS_DIA_KM * LONGITUD_KM   # 20.000 usuarios/día
ahorro_horas   = AHORRO_MIN_KM / 60 * LONGITUD_KM
ben_tiempo_full = usuarios_dia * ahorro_horas * VALOR_TIEMPO_UF_H * UF_A_CLP * 365
BEN_TIEMPO = ben_tiempo_full * FACTOR_TIEMPO_CONSERVADOR

# Beneficio 2: Reducción de accidentes (60% escenario conservador)
acc_por_km     = DATA_COMUNAL['accidentes_2024'] / DATA_COMUNAL['red_km_comunal']
ben_acc_full   = acc_por_km * LONGITUD_KM * REDUCCION_ACC * COSTO_ACC_CLP
BEN_ACCIDENTES = ben_acc_full * FACTOR_ACC_CONSERVADOR

# Beneficio 3: COV excluido en escenario conservador (intervención peatonal)
BEN_COV = 0.0

BEN_ANUAL_CONSERVADOR = BEN_TIEMPO + BEN_ACCIDENTES + BEN_COV

# ── Función evaluar_proyecto() del notebook base, aplicada al Tramo 7 ────────
def evaluar_proyecto_nabc(costo_inversion, ben_anual, tasa=TASA_SOCIAL, horizonte=HORIZONTE_ANOS):
    """
    Calcula VAN, TIR y B/C para el Tramo 7.
    Misma lógica que evaluar_proyecto() de la Celda B1 del notebook base,
    pero recibe el beneficio anual ya calculado (escenario conservador).

    VAN y TIR calculados manualmente (compatible con cualquier versión de NumPy,
    sin usar np.npv/np.irr que fueron removidos).
    """
    flujos = [-costo_inversion] + [ben_anual] * horizonte

    # VAN (cálculo manual, idéntico al notebook base)
    van = sum(f / (1 + tasa)**t for t, f in enumerate(flujos))

    # TIR (bisección numérica, idéntico al notebook base)
    def van_en_tasa(r):
        return sum(f / (1+r)**t for t, f in enumerate(flujos))
    lo, hi = 0.001, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if van_en_tasa(mid) > 0:
            lo = mid
        else:
            hi = mid
    tir = (lo + hi) / 2

    # Ratio B/C
    ben_act  = sum(ben_anual / (1+tasa)**t for t in range(1, horizonte+1))
    ratio_bc = ben_act / costo_inversion if costo_inversion > 0 else 0

    # Payback simple
    payback  = costo_inversion / ben_anual if ben_anual > 0 else float('inf')

    return {
        'VAN': van,
        'TIR': tir,
        'ratio_bc': ratio_bc,
        'ben_act': ben_act,
        'payback': payback,
        'viable': van > 0 and ratio_bc > 1,
    }

# ── Escenario base (costos notebook) ─────────────────────────────────────────
res_base = evaluar_proyecto_nabc(COSTO_TOTAL_BASE, BEN_ANUAL_CONSERVADOR)

# ── Escenario benchmark alto (precios municipales reales) ────────────────────
res_bench = evaluar_proyecto_nabc(COSTO_TOTAL_BENCHMARK, BEN_ANUAL_CONSERVADOR)

print("\nBeneficios anuales — Escenario conservador:")
print(f"  Ahorro tiempo de viaje: ${BEN_TIEMPO/1e6:,.2f} M CLP/año")
print(f"  Reducción accidentes: ${BEN_ACCIDENTES/1e6:,.2f} M CLP/año")
print(f"  COV vehicular (excluido — interv. peat.): $0,00 M CLP/año")
print(f"  {'─'*50}")
print(f"  BENEFICIO ANUAL CONSERVADOR            : ${BEN_ANUAL_CONSERVADOR/1e6:,.2f} M CLP/año")
print(f"\n  Supuesto accidentes: {acc_por_km:.2f} acc/km × 4 km × 25% reducción × 60% factor = {acc_por_km*LONGITUD_KM*REDUCCION_ACC*FACTOR_ACC_CONSERVADOR:.1f} acc/año × $50M = ${BEN_ACCIDENTES/1e6:.1f} M")
print(f"  Usuarios/día: {usuarios_dia:,.0f}  |  Ahorro: {AHORRO_MIN_KM} min/km × 4 km = {AHORRO_MIN_KM*LONGITUD_KM:.1f} min totales")

print(f"\n{'─'*65}")
print(f"{'Indicador':<30} {'Esc. base':>15} {'Esc. benchmark':>15}")
print(f"{'─'*65}")
print(f"{'Inversión inicial':<30} ${COSTO_TOTAL_BASE/1e6:>12,.1f} M  ${COSTO_TOTAL_BENCHMARK/1e6:>12,.0f} M")
print(f"{'Beneficio anual conservador':<30} ${BEN_ANUAL_CONSERVADOR/1e6:>12,.1f} M  ${BEN_ANUAL_CONSERVADOR/1e6:>12,.1f} M")
print(f"{'VP beneficios (20a, 6%)':<30} ${res_base['ben_act']/1e6:>12,.1f} M  ${res_bench['ben_act']/1e6:>12,.1f} M")
print(f"{'VAN social':<30} ${res_base['VAN']/1e6:>12,.1f} M  ${res_bench['VAN']/1e6:>12,.1f} M")
print(f"{'TIR':<30} {res_base['TIR']*100:>13.1f}%  {res_bench['TIR']*100:>13.1f}%")
print(f"{'Ratio B/C':<30} {res_base['ratio_bc']:>15.1f}  {res_bench['ratio_bc']:>15.2f}")
print(f"{'Payback simple (años)':<30} {res_base['payback']:>15.1f}  {res_bench['payback']:>15.1f}")
print(f"{'Viable (VAN>0 y B/C>1)':<30} {'✅ Sí':>15}  {'✅ Sí':>15}")
print(f"{'─'*65}")
print(f"\n  VAN > 0 en ambos escenarios → proyecto socialmente rentable.")
print(f"  B/C > 1 incluso con precios municipales reales (benchmark $97.000/m²).")

# ── ICV proyectado ────────────────────────────────────────────────────────────
print(f"\nICV proyectado post intervención:")
print(f"  Antes : {ICV_ACTUAL:.2f} / 5,00  (deficiente)")
print(f"  Después: {ICV_POST:.2f} / 5,00  (regular-alta)")
print(f"  Mejora : +{ICV_DELTA:.2f} pts (+{ICV_MEJORA_PCT:.0f}%)")


# ══════════════════════════════════════════════════════════════════════════════
# B2 — ANÁLISIS DE SENSIBILIDAD ECONÓMICA
# Basado en Celda B2 del notebook base
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("B2 — ANÁLISIS DE SENSIBILIDAD (basado en Celda B2 del notebook)")
print("="*65)

resultados_sens = []
params = {
    'Tasa de descuento (3%-12%)': [
        (t, evaluar_proyecto_nabc(COSTO_TOTAL_BASE, BEN_ANUAL_CONSERVADOR, tasa=t)['VAN'])
        for t in [0.03, 0.06, 0.09, 0.12]
    ],
    'Beneficios ±30%': [
        (f, evaluar_proyecto_nabc(COSTO_TOTAL_BASE, BEN_ANUAL_CONSERVADOR*f)['VAN'])
        for f in [0.70, 1.00, 1.30]
    ],
    'Costos ±30%': [
        (f, evaluar_proyecto_nabc(COSTO_TOTAL_BASE*f, BEN_ANUAL_CONSERVADOR)['VAN'])
        for f in [0.70, 1.00, 1.30]
    ],
}

print("\n  Parámetro                        | Variación  | VAN (M CLP) | Resultado")
print("  " + "─"*65)
for param, casos in params.items():
    for val, van in casos:
        if param.startswith('Tasa'):
            desc = f"{val*100:.0f}%"
        else:
            desc = f"{(val-1)*100:+.0f}%"
        resultado = "✅ VAN > 0" if van > 0 else "❌ VAN < 0"
        print(f"  {param:<33} | {desc:>8}   | {van/1e6:>10,.1f}  | {resultado}")
    print("  " + "─"*65)

print(f"\n  → El proyecto mantiene VAN > 0 ante variaciones del ±30% en costos")
print(f"    y beneficios, y hasta tasas de descuento del ~12%. Modelo robusto.")


# ══════════════════════════════════════════════════════════════════════════════
# C — COMPETITION / COMPARACIÓN DE ALTERNATIVAS
# Basado en la lógica de comparación del Informe NABC y el notebook base
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("C — COMPETITION: COMPARACIÓN DE ALTERNATIVAS")
print("="*65)

# Alt. 0: No intervenir
BEN_ALT0 = 0.0
COSTO_ALT0 = 0.0
VAN_ALT0 = 0.0

# Alt. 1: Preservación táctica (solo demarcación + retiro puntual)
COSTO_ALT1 = 80_000_000   # ~$80 M CLP (estimado informe NABC)
BEN_ALT1   = BEN_ANUAL_CONSERVADOR * 0.35   # 35% de los beneficios (no resuelve estructura)
res_alt1   = evaluar_proyecto_nabc(COSTO_ALT1, BEN_ALT1)

# Alt. 2: Rehabilitación peatonal accesible (seleccionada)
res_alt2_base  = res_base   # escenario base del notebook
res_alt2_bench = res_bench  # escenario benchmark

tabla_comp = pd.DataFrame({
    'Criterio': [
        'Inversión',
        'Plazo implementación',
        'Veredas en mal estado',
        'Cruces accesibles',
        'Obstáculos en cruces',
        'ICV esperado',
        'Impacto PMR / no videntes',
        'VAN social (escenario base)',
        'Ratio B/C',
        'Riesgo costo futuro',
    ],
    'Alt. 0 — No intervenir': [
        '$0',
        'Sin plazo',
        'No resuelve',
        'No resuelve',
        'Persisten',
        '1,75/5',
        'Bajo',
        '$0',
        '—',
        'MUY ALTO',
    ],
    'Alt. 1 — Táctica': [
        '$80 M CLP aprox.',
        '0–3 meses',
        'Solo puntos críticos',
        'Demarcación parcial',
        'Retiro puntos críticos',
        '2,3–2,5/5',
        'Medio',
        f'${res_alt1["VAN"]/1e6:,.0f} M CLP',
        f'{res_alt1["ratio_bc"]:.1f}',
        'Medio',
    ],
    'Alt. 2 — Rehab. accesible ✅': [
        f'${COSTO_TOTAL_BASE/1e6:,.1f} M CLP (base)',
        '3–12 meses',
        '16.000 m² continuos',
        'Rebajes + podotáctil + legibilidad',
        'Retiro/reubicación sistemática',
        f'{ICV_POST:.2f}/5',
        'Alto',
        f'${res_alt2_base["VAN"]/1e6:,.0f} M CLP',
        f'{res_alt2_base["ratio_bc"]:.1f}',
        'Bajo',
    ],
})

print("\n")
print(tabla_comp.to_string(index=False))

# VAN incremental Alt. 2 vs Alt. 1
van_incremental = res_alt2_base['VAN'] - res_alt1['VAN']
print(f"\n  VAN incremental Alt. 2 vs Alt. 1: ${van_incremental/1e6:,.0f} M CLP")
print(f"  La Alt. 2 genera ${van_incremental/1e6:,.0f} M CLP más de valor social que la Alt. 1.")
print(f"\n  Regla $1/$4-5: no intervenir hoy implica costos futuros de")
print(f"  ${COSTO_TOTAL_BASE/1e6*4:,.0f}–${COSTO_TOTAL_BASE/1e6*5:,.0f} M CLP en reconstrucción.")


# ══════════════════════════════════════════════════════════════════════════════
# SÍNTESIS NABC — RESUMEN EJECUTIVO
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("SÍNTESIS NABC — GRUPO 7 · TRAMO 7, GRAN AVENIDA, SAN MIGUEL")
print("="*65)

print(f"""
N — NEED
  ICV = {ICV_ACTUAL:.2f}/5,00 (deficiente). Tres problemas de alta severidad
  afectan a 17.323 adultos mayores y ~23.116 adultos con discapacidad:
    ① Veredas en mal estado
    ② Cruces con accesibilidad incompleta
    ③ Elementos que obstruyen cruces

A — APPROACH
  Rehabilitación peatonal accesible en 2 etapas:
    Etapa 1 (0–3 meses) : Retiro obstáculos + demarcación → ${(costo_obstaculos+costo_señalizacion)/1e6:,.1f} M CLP
    Etapa 2 (3–12 meses): Veredas {AREA_VEREDA_M2:,.0f} m² + {N_CRUCES} cruces accesibles  → ${(costo_veredas+costo_cruces)/1e6:,.1f} M CLP
  Total (base): ${COSTO_TOTAL_BASE/1e6:,.1f} M CLP · 4 cuadrillas · ~{meses_veredas*1.2:.0f} meses calendario

B — BENEFIT
  Escenario conservador (6% tasa social, 20 años):
    VAN              = ${res_base['VAN']/1e6:,.1f} M CLP  [escenario base]
    VAN              = ${res_bench['VAN']/1e6:,.1f} M CLP  [escenario benchmark $97k/m²]
    TIR              = {res_base['TIR']*100:.1f}%  (>> 6% MIDEPLAN)
    Ratio B/C        = {res_base['ratio_bc']:.1f}  (base) / {res_bench['ratio_bc']:.2f} (benchmark)
    VAN > 0 en ambos escenarios → socialmente rentable
  ICV: {ICV_ACTUAL:.2f} → {ICV_POST:.2f} / 5,00  (+{ICV_MEJORA_PCT:.0f}%)

C — COMPETITION
  Alt. 2 supera a Alt. 1 en ${van_incremental/1e6:,.0f} M CLP de VAN adicional.
  Es la única que resuelve las causas estructurales: veredas, cruces y accesibilidad.
  Robusto: VAN > 0 hasta costos +30%, beneficios -30% y tasa social 12%.
""")
