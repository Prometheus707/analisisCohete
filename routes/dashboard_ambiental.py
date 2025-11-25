from flask import Blueprint, render_template, jsonify
import csv
import os
import requests
from statistics import mean

bp = Blueprint('dashboard_ambiental', __name__, url_prefix='/dashboard-ambiental')

DATA_DIR = os.path.join(os.getcwd(), "data")

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


@bp.route('/')
def index():
    archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    return render_template('dashboard_ambiental.html', archivos=archivos)


def obtener_datos_meteorologicos(lat=2.4448, lon=-76.6147):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,surface_pressure",
            "timezone": "America/Bogota"
        }

        r = requests.get(WEATHER_API_URL, params=params, timeout=5)
        data = r.json().get("current", {})

        return {
            "temperatura": data.get("temperature_2m"),
            "presion": data.get("surface_pressure", 0) * 100,
            "timestamp": data.get("time"),
            "exito": True
        }

    except:
        return {"temperatura": None, "presion": None, "timestamp": None, "exito": False}


def analizar_csv(filepath):
    datos = {
        'tiempos': [],
        'temperaturas': [],
        'presiones': [],
        'altitudes': []
    }

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                datos['tiempos'].append(float(row.get('time_s', 0)))
                datos['temperaturas'].append(float(row.get('temp_c', 0)))
                datos['presiones'].append(float(row.get('pressure_pa', 0)))
                datos['altitudes'].append(float(row.get('altitude_m', 0)))

        est = {
            'temp_promedio': round(mean(datos['temperaturas']), 2),
            'temp_min': min(datos['temperaturas']),
            'temp_max': max(datos['temperaturas']),
            'presion_promedio': round(mean(datos['presiones']), 2),
            'presion_min': min(datos['presiones']),
            'presion_max': max(datos['presiones']),
            'altitud_max': max(datos['altitudes']),
            'duracion': max(datos['tiempos'])
        }

        return datos, est

    except Exception as e:
        print("Error CSV:", e)
        return None, None


# @bp.route('/api/datos/<archivo>')
@bp.route('/api/datos/<path:archivo>')
def api_datos(archivo):

    filepath = os.path.join(DATA_DIR, archivo)
    print("Cargando archivo:", filepath)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "Archivo no encontrado"}), 404

    datos_csv, est = analizar_csv(filepath)

    if datos_csv is None:
        return jsonify({"error": "Error procesando CSV"}), 500

    meteo = obtener_datos_meteorologicos()

    comparacion = {
        "diff_temperatura": None,
        "diff_temperatura_porcentaje": None,
        "diff_presion": None,
        "diff_presion_porcentaje": None
    }

    if meteo["exito"]:
        if meteo["temperatura"] is not None:
            diff = est["temp_promedio"] - meteo["temperatura"]
            comparacion["diff_temperatura"] = round(diff, 2)
            comparacion["diff_temperatura_porcentaje"] = round((diff / meteo["temperatura"]) * 100, 2)

        if meteo["presion"] is not None:
            diff = est["presion_promedio"] - meteo["presion"]
            comparacion["diff_presion"] = round(diff, 2)
            comparacion["diff_presion_porcentaje"] = round((diff / meteo["presion"]) * 100, 2)

    return jsonify({
        "csv": {
            **datos_csv,
            "estadisticas": est
        },
        "meteorologico": meteo,
        "comparacion": comparacion
    })
