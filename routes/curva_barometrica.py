from flask import Blueprint, render_template, jsonify
import csv
import os
from math import exp

bp = Blueprint("curva_barometrica", __name__, url_prefix="/curva-barometrica")

# Carpeta donde están los CSV
DATA_DIR = os.path.join(os.getcwd(), "data")


@bp.route("/")
def index():
    """Carga la vista principal con la lista de archivos CSV."""
    archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    return render_template("curva_barometrica.html", archivos=archivos)


def leer_csv(filepath):
    """Lee el CSV del vuelo y devuelve altitud y presión real."""
    altitudes = []
    presiones = []

    with open(filepath, "r", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        for row in rd:
            try:
                altitudes.append(float(row["altitude_m"]))
                presiones.append(float(row["pressure_pa"]))
            except:
                pass

    return altitudes, presiones


def presion_barometrica(h, p0=101325, T=288.15, L=0.0065):
    """Ecuación barométrica para presión teórica."""
    R = 287.05
    g = 9.80665
    return p0 * (1 - (L * h / T)) ** (g / (R * L))


@bp.route("/api/datos/<archivo>")
def api_datos(archivo):
    """Devuelve JSON con presión real y presión teórica."""
    
    filepath = os.path.join(DATA_DIR, archivo)
    print(">> Cargando archivo curva barométrica:", filepath)

    if not os.path.exists(filepath):
        return jsonify({"error": "Archivo no encontrado"}), 404

    altitudes, presiones_reales = leer_csv(filepath)
    presiones_teoricas = [presion_barometrica(h) for h in altitudes]

    return jsonify({
        "altitudes": altitudes,
        "presiones_reales": presiones_reales,
        "presiones_teoricas": presiones_teoricas
    })
