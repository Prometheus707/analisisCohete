from flask import Blueprint, render_template

# Crear blueprint para densidad del aire
bp = Blueprint('densidad_aire', __name__, url_prefix='/densidad-aire')

@bp.route('/')
def index():
    """Página de análisis de densidad del aire"""
    return render_template('densidad_aire.html')

# Aquí puedes agregar más rutas, por ejemplo:
# @bp.route('/calcular', methods=['POST'])
# def calcular():
#     # Lógica para calcular densidad del aire
#     # temperatura = request.form.get('temperatura')
#     # presion = request.form.get('presion')
#     # densidad = calcular_densidad(temperatura, presion)
#     # efecto_rendimiento = analizar_efecto(densidad)
#     return render_template('resultados_densidad.html', densidad=densidad, efecto=efecto_rendimiento)
