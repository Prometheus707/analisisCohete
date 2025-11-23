from flask import Blueprint, render_template

# Crear blueprint para análisis de propulsión
bp = Blueprint('propulsion', __name__, url_prefix='/propulsion')

@bp.route('/')
def index():
    """Página de análisis de propulsión"""
    return render_template('propulsion.html')

# Aquí el compañero puede agregar más rutas, por ejemplo:
# @bp.route('/calcular', methods=['POST'])
# def calcular():
#     # Lógica de cálculo
#     return render_template('resultados.html', datos=resultados)
