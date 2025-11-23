from flask import Blueprint, render_template

# Crear blueprint para análisis de trayectoria
bp = Blueprint('trayectoria', __name__, url_prefix='/trayectoria')

@bp.route('/')
def index():
    """Página de análisis de trayectoria"""
    return render_template('trayectoria.html')

# Aquí el compañero puede agregar más rutas, por ejemplo:
# @bp.route('/calcular', methods=['POST'])
# def calcular():
#     # Lógica de cálculo
#     return render_template('resultados.html', datos=resultados)
