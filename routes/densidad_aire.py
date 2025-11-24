from flask import Blueprint, render_template
import os
import csv

bp = Blueprint("densidad_aire", __name__, url_prefix="/densidad-aire")

# Constante física del gas ideal (aire)
R = 287.05


def calcular_densidad_air(pressure_pa, temp_c):
    temp_k = temp_c + 273.15
    if temp_k <= 0:
        return None
    return pressure_pa / (R * temp_k)


def analizar_csv_densidad(path_csv):
    densidades = []
    tiempos = []

    with open(path_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                p = float(row["pressure_pa"])
                t = float(row["temp_c"])

                time = float(row["time_s"])
            except:
                continue

            rho = calcular_densidad_air(p, t)
            if rho is not None:
                densidades.append(rho)
                tiempos.append(time)

    if not densidades:
        return None

    dens_prom = sum(densidades) / len(densidades)
    dens_min = min(densidades)
    dens_max = max(densidades)

    # Explicación automática basada en densidad promedio
    explicacion = ""
    if dens_prom > 1.15:
        explicacion = (
            "La densidad del aire fue relativamente alta durante el vuelo, "
            "lo cual aumenta la resistencia aerodinámica y reduce el apogeo alcanzado."
        )
    elif dens_prom < 1.05:
        explicacion = (
            "La densidad del aire fue baja, generando menor resistencia aerodinámica "
            "y permitiendo un mejor rendimiento en altura."
        )
    else:
        explicacion = (
            "La densidad del aire estuvo en un rango normal. "
            "La influencia sobre el apogeo fue moderada."
        )

    return {
        "archivo": os.path.basename(path_csv),
        "dens_promedio": round(dens_prom, 4),
        "dens_min": round(dens_min, 4),
        "dens_max": round(dens_max, 4),
        "explicacion": explicacion
    }


def procesar_densidades():
    # Ruta correcta EXACTA (misma usada en los otros módulos)
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
    base = os.path.abspath(base)

    print("📂 Leyendo CSV desde:", base)  # DEBUG
    print("Archivos encontrados:", os.listdir(base))  # DEBUG

    resultados = []

    for archivo in os.listdir(base):
        if archivo.endswith(".csv"):
            ruta = os.path.join(base, archivo)
            analisis = analizar_csv_densidad(ruta)
            if analisis:
                resultados.append(analisis)

    return resultados




@bp.route("/")
def index():
    resultados = procesar_densidades()

    return render_template(
        "densidad_aire.html",
        resultados=resultados
    )
