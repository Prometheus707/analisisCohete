from flask import Blueprint, render_template
import os
import csv

bp = Blueprint("formula_exito", __name__, url_prefix="/formula-exito")

# Parámetros constantes del laboratorio
PRESION_USADA = 60        # PSI
AGUA_USADA = 1.0          # Litros
CAPACIDAD_BOTELLA = 3.0   # Litros


def analizar_lanzamiento(path_csv):
    tiempos = []
    alturas = []

    with open(path_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t = float(row["time_s"])
                h = float(row["altitude_m"])
            except:
                continue

            tiempos.append(t)
            alturas.append(h)

    apogeo = max(alturas)
    tiempo_apogeo = tiempos[alturas.index(apogeo)]

    eficiencia = apogeo / AGUA_USADA  # m por litro

    return {
        "archivo": os.path.basename(path_csv),
        "apogeo": round(apogeo, 2),
        "tiempo_apogeo": round(tiempo_apogeo, 2),
        "presion": PRESION_USADA,
        "agua": AGUA_USADA,
        "eficiencia": round(eficiencia, 2)
    }


def procesar_formula_exito():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    base = os.path.abspath(base)

    resultados = []

    for archivo in os.listdir(base):
        if archivo.endswith(".csv"):
            ruta = os.path.join(base, archivo)
            resultados.append(analizar_lanzamiento(ruta))

    if not resultados:
        return None, []

    mejor = max(resultados, key=lambda x: x["apogeo"])

    return mejor, resultados


@bp.route("/")
def index():
    mejor, resultados = procesar_formula_exito()

    return render_template(
        "formula_exito.html",
        mejor=mejor,
        resultados=resultados
    )
