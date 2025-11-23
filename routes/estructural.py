from flask import Blueprint, render_template

# Crear blueprint para análisis estructural
bp = Blueprint('estructural', __name__, url_prefix='/estructural')

@bp.route('/')
def index():
    """Página de análisis estructural"""
    return render_template('estructural.html')

# Aquí el compañero puede agregar más rutas, por ejemplo:
# @bp.route('/calcular', methods=['POST'])
# def calcular():
#     # Lógica de cálculo
#     return render_template('resultados.html', datos=resultados)
