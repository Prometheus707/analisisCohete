from flask import Blueprint, render_template

# Crear blueprint para fases del vuelo
bp = Blueprint('fases_vuelo', __name__, url_prefix='/fases-vuelo')

@bp.route('/')
def index():
    """Página de análisis de fases del vuelo"""
    return render_template('fases_vuelo.html')

# Aquí puedes agregar más rutas, por ejemplo:
# @bp.route('/graficar', methods=['POST'])
# def graficar():
#     # Lógica para identificar y graficar fases (ascenso, apogeo, descenso)
#     # datos_altitud = request.form.getlist('altitud')
#     # fases = identificar_fases(datos_altitud)
#     # grafico = generar_grafico_fases(fases)
#     return render_template('resultados_fases.html', grafico=grafico)
