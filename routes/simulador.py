from flask import Blueprint, render_template, request, jsonify
import math
import statistics

bp = Blueprint("simulador1", __name__, url_prefix="/simulador")

# --- Datos reales para calibración ---
G = 9.78  # gravedad Popayán
ALTURAS_REALES = [19, 17, 16, 21, 14]  # tus vuelos reales
PSI_CALIB = 60.0  # presión real de tus vuelos

# ===============================================
# 🔵 CALIBRACIÓN FÍSICO–EMPÍRICA DEL MODELO
# ===============================================
h_mean = statistics.mean(ALTURAS_REALES)  # media de alturas reales

# Littlewood invertido → tiempo de ascenso
t_mean = math.sqrt(8 * h_mean / G)

# t = k * sqrt(PSI) → estimamos k
k_est = t_mean / math.sqrt(PSI_CALIB)

# h = (g/8) * k² * PSI → modelo lineal en PSI
A_coef = (G / 8.0) * (k_est ** 2)

# escalado empírico para corregir error del modelo
h_at_calib_model = A_coef * PSI_CALIB
h_at_calib_real = h_mean
scale = h_at_calib_real / h_at_calib_model

# Límites físicos reales
PSI_MIN = 0.0
PSI_MAX = 80.0

# ===============================================
# 🔵 FUNCIÓN PRINCIPAL DE PREDICCIÓN
# ===============================================
def predict_height_from_psi(psi):
    psi = max(PSI_MIN, min(PSI_MAX, float(psi)))

    h_basic = A_coef * psi
    h_final = h_basic * scale

    # ±5% incertidumbre natural
    uncert_pct = 0.05
    uncert = h_final * uncert_pct

    return {
        "psi_used": round(psi, 2),
        "height_m": round(h_final, 2),
        "height_min": round(max(0, h_final - uncert), 2),
        "height_max": round(h_final + uncert, 2),
        "model_info": {
            "A_coef": A_coef,
            "k_est": k_est,
            "h_mean": h_mean,
            "h_at_calib_model": h_at_calib_model,
            "h_at_calib_real": h_at_calib_real,
            "scale": scale
        }
    }

# ===============================================
# 🌐 RUTAS
# ===============================================

@bp.route("/", methods=["GET"])
def index():
    return render_template(
        "simulador1.html",   # <- NUEVA PLANTILLA 3D
        psi_min=PSI_MIN,
        psi_max=PSI_MAX,
        psi_calib=PSI_CALIB,
        h_mean=h_mean,
        A_coef=A_coef
    )



@bp.route("/calcular", methods=["POST"])
def calcular():
    data = request.get_json(silent=True) or {}

    psi = data.get("psi", None)
    if psi is None:
        return jsonify({"error": "Falta el parámetro 'psi'"}), 400

    try:
        psi_val = float(psi)
    except:
        return jsonify({"error": "PSI no es numérico"}), 400

    psi_clamped = max(PSI_MIN, min(PSI_MAX, psi_val))

    result = predict_height_from_psi(psi_clamped)

    explanation = (
        f"Modelo físico Littlewood + calibración con tus vuelos reales.\n"
        f"Fórmula aproximada: h ≈ A·PSI con A={A_coef:.4f}.\n"
        f"Altura media real a 60 PSI: {h_mean:.2f} m.\n"
        f"PSI recibido: {psi_val} PSI (limitado a {psi_clamped} PSI).\n"
        f"Altura estimada: {result['height_m']} m "
        f"(intervalo {result['height_min']} – {result['height_max']} m)."
    )

    return jsonify({
        "psi": result["psi_used"],
        "height_m": result["height_m"],
        "height_min": result["height_min"],
        "height_max": result["height_max"],
        "explanation": explanation,
        "model_info": result["model_info"]
    })
