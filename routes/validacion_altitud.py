from flask import Blueprint, render_template
import csv
import os

# Crear blueprint para validación de altitud
bp = Blueprint(
    'validacion_altitud',
    __name__,
    url_prefix='/validacion-altitud'
)


@bp.route('/')
def index():
    """Página de validación de altitud teórica vs. real"""

    resultados = procesar_vuelos()   # Cargar csv + procesar altitud

    return render_template(
        'validacion_altitud.html',
        resultados=resultados
    )

# ===============================
#   PARÁMETROS
# ===============================
G = 9.78  # Gravedad Popayán


# ===============================
#   FUNCIÓN PRINCIPAL
# ===============================
def analizar_csv_lanzamiento(ruta_csv):
    tiempos = []
    alturas = []

    # Leer CSV
    with open(ruta_csv, "r") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            try:
                t = float(fila["time_s"])
                h = float(fila["altitude_m"])
            except:
                continue

            tiempos.append(t)
            alturas.append(h)

    if len(alturas) == 0:
        return None

    # ------------------------------------------
    # 1️⃣ Detectar altura máxima
    # ------------------------------------------
    altura_real = max(alturas)
    idx_apogeo = alturas.index(altura_real)

    # Tiempo de ascenso hasta el apogeo
    tiempo_ascenso = tiempos[idx_apogeo]

    # ------------------------------------------
    # 2️⃣ Calcular altura teórica real (Littlewood)
    # ------------------------------------------
    altura_teorica = (G * (tiempo_ascenso ** 2)) / 8

    # ------------------------------------------
    # 3️⃣ Error porcentual
    # ------------------------------------------
    error = abs((altura_teorica - altura_real) / altura_real) * 100

    # ------------------------------------------
    # 4️⃣ Detectar inicio real del ascenso
    # ------------------------------------------
    inicio_ascenso = None
    for i in range(1, len(alturas)):
        if alturas[i] > alturas[i - 1]:
            inicio_ascenso = i
            break

    return {
        "archivo": os.path.basename(ruta_csv),
        "tiempo_total": tiempos[-1],
        "altura_real": altura_real,
        "altura_teorica": altura_teorica,
        "error_porcentual": error,
        "tiempo_ascenso": tiempo_ascenso,     # <-- NUEVO
        "inicio_ascenso": inicio_ascenso,
        "tiempo_inicio_ascenso": tiempos[inicio_ascenso] if inicio_ascenso else None
    }


# ===============================
#   Cargar y procesar los 4 vuelos
# ===============================
def procesar_vuelos():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    base = os.path.abspath(base)

    resultados = []

    if not os.path.isdir(base):
        print("❌ Carpeta data NO encontrada:", base)
        return []

    for archivo in os.listdir(base):
        if archivo.endswith(".csv"):
            ruta = os.path.join(base, archivo)
            vuelo = analizar_csv_lanzamiento(ruta)
            if vuelo:
                resultados.append(vuelo)

    return resultados


# ===============================
#   Modo consola (debug)
# ===============================
if __name__ == "__main__":
    vuelos = procesar_vuelos()

    print("\n===== RESULTADOS =====\n")

    for v in vuelos:
        print(f"""
Archivo: {v["archivo"]}
Tiempo total: {v["tiempo_total"]:.2f} s
Tiempo ascenso real: {v["tiempo_ascenso"]:.2f} s
Altura real: {v["altura_real"]:.2f} m
Altura teórica: {v["altura_teorica"]:.2f} m
Error: {v["error_porcentual"]:.2f} %

Inicio real de ascenso (índice): {v["inicio_ascenso"]}
Tiempo inicio ascenso: {v["tiempo_inicio_ascenso"]} s
""")
