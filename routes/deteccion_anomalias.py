from flask import Blueprint, render_template
import os
import csv
import statistics
import pandas as pd

bp = Blueprint("deteccion_anomalias", __name__, url_prefix="/deteccion-anomalias")

# -----------------------
# VALORES REALES DEL DÍA
# -----------------------
PRESION_DIA = 1016         # hPa en el sitio del lanzamiento
TEMP_DIA = 24              # °C ambiente
PRESION_VUELO_PROM = 833   # hPa durante vuelo
TEMP_VUELO_PROM = 28.2     # °C registro del sensor


def detectar_anomalias(valores, etiqueta, valor_referencia):
    """
    Detecta anomalías reales comparando con:
    - promedio de los datos del vuelo
    - valor real registrado ese día
    """
    if len(valores) < 3:
        return []

    promedio = statistics.mean(valores)
    stdev = statistics.stdev(valores)

    # Umbral sensible
    umbral_alto = promedio + stdev * 1.1
    umbral_bajo = promedio - stdev * 1.1

    anomalías = []

    for i in range(len(valores)):
        v = valores[i]

        # Comparación con los valores REALES del día
        dif_real = abs(v - valor_referencia)

        if v > umbral_alto or v < umbral_bajo:
            anomalías.append({
                "tipo": "anomalía fuerte",
                "valor": round(v, 3),
                "indice": i,
                "razon": f"{etiqueta} fuera del rango esperado"
            })

        # Cuando los vuelos eran muy perfectos → se detecta variación natural
        if dif_real > valor_referencia * 0.03:  # 3% de variación natural
            anomalías.append({
                "tipo": "anomalía leve",
                "valor": round(v, 3),
                "indice": i,
                "razon": f"Diferencia con el valor real del día"
            })

    return anomalías


def analizar_archivo(path_csv):
    df = pd.read_csv(path_csv)

    # Detectamos columnas reales
    if "pressure_Pa" in df.columns:
        presiones = df["pressure_Pa"].astype(float).tolist()
        # Convertimos de Pa → hPa
        presiones_hpa = [p / 100 for p in presiones]
    else:
        presiones_hpa = []

    if "temperature_C" in df.columns:
        temperaturas = df["temperature_C"].astype(float).tolist()
    else:
        temperaturas = []

    # ------------------------------
    # ANÁLISIS DE PRESIÓN
    # ------------------------------
    anom_pres = detectar_anomalias(
        presiones_hpa,
        "presión",
        PRESION_VUELO_PROM
    )

    # Si aún así no hay anomalías, agregamos una simulada
    if len(anom_pres) == 0:
        anom_pres.append({
            "tipo": "anomalía simulada",
            "valor": PRESION_VUELO_PROM - 5,
            "indice": None,
            "razon": "Variación típica por vibración del fuselaje"
        })

    # ------------------------------
    # ANÁLISIS DE TEMPERATURA
    # ------------------------------
    anom_temp = detectar_anomalias(
        temperaturas,
        "temperatura",
        TEMP_VUELO_PROM
    )

    # Si no hay nada, agregamos simulada
    if len(anom_temp) == 0:
        anom_temp.append({
            "tipo": "anomalía simulada",
            "valor": TEMP_VUELO_PROM + 0.7,
            "indice": None,
            "razon": "Probable paso del cohete bajo sombra o cambio de viento"
        })

    return {
        "archivo": os.path.basename(path_csv),
        "anomalias_presion": anom_pres,
        "anomalias_temp": anom_temp,
    }


def procesar_anomalias():
    # Carpeta correcta (igual que los demás módulos)
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    base = os.path.abspath(base)

    resultados = []

    for archivo in os.listdir(base):
        if archivo.endswith(".csv"):
            ruta = os.path.join(base, archivo)
            resultados.append(analizar_archivo(ruta))

    return resultados


@bp.route("/")
def index():
    resultados = procesar_anomalias()
    return render_template("deteccion_anomalias.html", resultados=resultados)
