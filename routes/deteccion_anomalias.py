from flask import Blueprint, render_template

# Crear blueprint para detección de anomalías
bp = Blueprint('deteccion_anomalias', __name__, url_prefix='/deteccion-anomalias')

@bp.route('/')
def index():
    """Página de detección de anomalías"""
    return render_template('deteccion_anomalias.html')

# Aquí puedes agregar más rutas, por ejemplo:
# @bp.route('/analizar', methods=['POST'])
# def analizar():
#     # Lógica para detectar anomalías en datos
#     # datos_temperatura = request.form.getlist('temperatura')
#     # datos_presion = request.form.getlist('presion')
#     # anomalias = detectar_anomalias(datos_temperatura, datos_presion)
#     # causas_probables = proponer_causas(anomalias)
#     return render_template('resultados_anomalias.html', anomalias=anomalias, causas=causas_probables)
