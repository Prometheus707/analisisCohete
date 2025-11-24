from flask import Blueprint, render_template
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# CORREGIDO: Cambié el nombre a 'prediccion_bp' para coincidir con tu registro
bp = Blueprint('prediccion', __name__, url_prefix='/prediccion')

def limpiar_valor(v):
    """Convierte valores a float limpiamente, incluso si vienen como strings raras."""
    try:
        return float(str(v).replace(",", ".").strip())
    except:
        return np.nan

def analizar_csv(path):
    """Función para analizar archivos CSV - copiada desde app.py"""
    import csv
    
    tiempos = []
    alturas = []

    with open(path, "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                tiempos.append(float(row["time_s"]))
                alturas.append(float(row["altitude_m"]))
            except:
                pass

    # Cálculo simple de altura máxima
    altura_real = max(alturas) if alturas else 0
    tiempo_total = tiempos[-1] if tiempos else 0

    return {
        "archivo": os.path.basename(path),
        "tiempo_total": round(tiempo_total, 2),
        "altura_real": round(altura_real, 2),
        "altura_teorica": 0,  # Placeholder
        "error_porcentual": 0  # Placeholder
    }

@bp.route("/")
def index():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    base = os.path.abspath(base)

    X = []  # features
    Y = []  # alturas reales

    for archivo in os.listdir(base):
        if archivo.endswith(".csv"):
            try:
                df = pd.read_csv(os.path.join(base, archivo))

                # --- Limpiar todas las columnas numéricas ---
                for col in df.columns:
                    df[col] = df[col].apply(limpiar_valor)

                # --- features de entrada ---
                features = []

                if "pressure_Pa" in df.columns:
                    features.append(df["pressure_Pa"].mean() / 100)  # hPa

                if "temperature_C" in df.columns:
                    features.append(df["temperature_C"].mean())

                if "accelZ" in df.columns:
                    features.append(df["accelZ"].max())

                if "velocity_m_s" in df.columns:
                    features.append(df["velocity_m_s"].max())

                if "time_s" in df.columns:
                    features.append(df["time_s"].iloc[-1])

                # Si no hay features válidas → omitir archivo
                if len(features) == 0 or np.isnan(features).any():
                    continue

                X.append(features)

                # Altura real (target)
                if "altitude_m" in df.columns:
                    altura = df["altitude_m"].max()
                    Y.append(limpiar_valor(altura))
            except Exception as e:
                print(f"Error procesando {archivo}: {e}")
                continue

    # Verificar que tenemos datos suficientes
    if len(X) < 2:
        return render_template(
            "prediccion.html",
            prediccion="No se pudo entrenar el modelo. Faltan datos válidos.",
            vuelos=len(Y) if 'Y' in locals() else 0,
            modelo_usado="No aplicable"
        )

    # Convertir a numpy y limpiar NaN
    X = np.array(X, dtype=float)
    Y = np.array(Y, dtype=float)

    # Eliminar filas con NaN
    mask = ~np.isnan(X).any(axis=1) & ~np.isnan(Y)
    X = X[mask]
    Y = Y[mask]

    if len(X) < 2:
        return render_template(
            "prediccion.html",
            prediccion="No se pudo entrenar el modelo. Faltan datos válidos después de limpieza.",
            vuelos=len(Y),
            modelo_usado="No aplicable"
        )

    # Entrenar modelo REAL
    modelo = RandomForestRegressor(n_estimators=500, random_state=42)
    modelo.fit(X, Y)

    # Predicción usando promedio global de features
    entrada = np.nanmean(X, axis=0).reshape(1, -1)
    prediccion_altura = modelo.predict(entrada)[0]

    return render_template(
        "prediccion.html",
        prediccion=round(float(prediccion_altura), 2),
        vuelos=len(Y),
        modelo_usado="Random Forest Regressor (500 árboles)"
    )

@bp.route("/resultados")
def resultados():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    base = os.path.abspath(base)
    
    vuelos = []
    X = []
    y = []

    # Leer CSVs y recolectar datos reales
    for archivo in os.listdir(base):
        if archivo.endswith(".csv"):
            info = analizar_csv(os.path.join(base, archivo))
            vuelos.append(info)

            # Entrenamiento: usamos tiempo_total como variable independiente
            X.append([info["tiempo_total"]])
            y.append(info["altura_real"])

    # Verificar que tenemos datos
    if len(X) < 2:
        return render_template(
            "prediccion.html",
            prediccion="No hay suficientes datos para predicción.",
            vuelos=len(vuelos),
            modelo_usado="No aplicable"
        )

    # Entrenar modelo ML avanzado
    modelo = RandomForestRegressor(n_estimators=500, random_state=42)
    modelo.fit(X, y)

    # Predicción para el tiempo promedio entre vuelos
    tiempo_prom = float(np.mean(X))

    prediccion = modelo.predict([[tiempo_prom]])[0]

    return render_template(
        "prediccion.html",  # Cambié a prediccion.html para consistencia
        prediccion=round(prediccion, 2),
        vuelos=len(vuelos),
        modelo_usado="Random Forest Regressor (500 árboles)"
    )