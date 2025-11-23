from flask import Blueprint, render_template

# Crear blueprint para curva barométrica
bp = Blueprint('curva_barometrica', __name__, url_prefix='/curva-barometrica')

@bp.route('/')
def index():
    """Página de análisis de curva barométrica"""
    return render_template('curva_barometrica.html')

# Aquí puedes agregar más rutas, por ejemplo:
# @bp.route('/graficar', methods=['POST'])
# def graficar():
#     # Lógica para graficar altitud vs. presión
#     # Comparar con ecuación barométrica
#     # altitudes = request.form.getlist('altitudes')
#     # presiones = request.form.getlist('presiones')
#     # grafico = generar_curva_barometrica(altitudes, presiones)
#     return render_template('grafico.html', grafico=grafico)
