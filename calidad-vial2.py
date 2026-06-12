import geopandas as gpd
import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------
# 1. CONFIGURACIÓN Y RUTAS (Actualizadas según tu sistema)
# ---------------------------------------------------------
ruta = r"C:\Users\anton\Documents\capas\indice_vial.gpkg"
salida = r"C:\Users\anton\Documents\capas\ICV_Final-nodos_SanMiguel.gpkg"
crs_utm = "EPSG:32719"

def cargar(capa):
    return gpd.read_file(ruta, layer=capa).to_crs(crs_utm)

print("🚀 Iniciando el Modelo de Calidad Vial sobre Nodos Reales...")

# ---------------------------------------------------------
# 2. CARGA DE INFRAESTRUCTURA Y SINIESTRALIDAD
# ---------------------------------------------------------
cruces = cargar("highway_crossing")
semaforos = cargar("highway_traffic_signals")
lomos = cargar("traffic_calming_hump")
luces = cargar("highway_street_lamp")
veredas = cargar("highway_footway_lineas")
acc_list = [
    "layer_puntos_criticos_de_accidentes_ano_2016_20220311033027",
    "layer_puntos_criticos_de_accidentes_ano_2015_20220311033014",
    "layer_puntos_criticos_de_accidentes_ano_2014_20220311032959",
    "layer_puntos_criticos_de_accidentes_ano_2013_20230921045334"
]
accidentes_gdfs = []
for l in acc_list:
    try:
        accidentes_gdfs.append(gpd.read_file(ruta, layer=l))
    except:
        continue
accidentes = pd.concat(accidentes_gdfs, ignore_index=True)
accidentes = gpd.GeoDataFrame(accidentes, geometry="geometry", crs=cruces.crs).to_crs(crs_utm)

# ---------------------------------------------------------
# 3. CARGA DE TUS NODOS Y CREACIÓN DE BUFFERS
# ---------------------------------------------------------
nodos = cargar("nodos_viales")
if "id_nodo" not in nodos.columns:
    nodos["id_nodo"] = nodos.index
nodos_buffer = nodos.copy()
nodos_buffer["geometry"] = nodos_buffer.buffer(120)

# ---------------------------------------------------------
# 4. CÁLCULO DE INDICADORES ESPACIALES
# ---------------------------------------------------------
def contar(base, capa, nombre):
    join = gpd.sjoin(base, capa, how="left", predicate="intersects")
    return join.groupby(join.index).size().fillna(0)

print("📊 Analizando entorno de cada nodo vial...")
nodos["c_cruces"] = contar(nodos_buffer, cruces, "c_cruces")
nodos["c_semaforos"] = contar(nodos_buffer, semaforos, "c_semaforos")
nodos["c_lomos"] = contar(nodos_buffer, lomos, "c_lomos")
nodos["c_luces"] = contar(nodos_buffer, luces, "c_luces")
nodos["c_accidentes"] = contar(nodos_buffer, accidentes, "c_accidentes")
inter_v = gpd.overlay(nodos_buffer, veredas, how='intersection', keep_geom_type=False)
inter_v = inter_v[inter_v.geometry.type.isin(['LineString', 'MultiLineString'])]
inter_v['l'] = inter_v.geometry.length
nodos["m_veredas"] = inter_v.groupby(level=0)['l'].sum().fillna(0)

# ---------------------------------------------------------
# 5. NORMALIZACIÓN E ICV (CON IMPACTO SOCIAL)
# ---------------------------------------------------------
def norm(col):
    return (col - col.min()) / (col.max() - col.min()) if col.max() != col.min() else 0
indicadores = ["c_cruces", "c_semaforos", "c_lomos", "c_luces", "c_accidentes", "m_veredas"]
for ind in indicadores:
    nodos[f"{ind}_n"] = norm(nodos[ind])
nodos["icv_base"] = (
    0.20 * nodos["c_cruces_n"] + 
    0.20 * nodos["c_semaforos_n"] + 
    0.15 * nodos["c_luces_n"] + 
    0.15 * nodos["m_veredas_n"] + 
    0.10 * nodos["c_lomos_n"] - 
    0.20 * nodos["c_accidentes_n"]
)
factor_crecimiento = 1.397
nodos["icv_social"] = nodos["icv_base"] * factor_crecimiento

# ---------------------------------------------------------
# 6. EXPORTACIÓN PARA QGIS (CORREGIDA PARA EVITAR DUPLICADOS)
# ---------------------------------------------------------
columnas_deseadas = ["geometry", "icv_base", "icv_social", "c_accidentes"] + indicadores
nodos_final = nodos.loc[:, ~nodos.columns.duplicated()].copy()
nodos_final = nodos_final[nodos_final.columns.intersection(columnas_deseadas)]
nodos_final.to_file(salida, layer="ICV_Nodos_Comunales", driver="GPKG")

print(f"✅ ¡Éxito! Se han procesado {len(nodos_final)} nodos.")
print(f"Archivo generado en: {salida}")
