from flask import Blueprint, render_template

# Crear blueprint para dashboard ambiental
bp = Blueprint('dashboard_ambiental', __name__, url_prefix='/dashboard-ambiental')

@bp.route('/')
def index():
    """Página de dashboard ambiental"""
    return render_template('dashboard_ambiental.html')

# Aquí puedes agregar más rutas, por ejemplo:
# @bp.route('/comparar', methods=['POST'])
# def comparar():
#     # Lógica para comparar datos del sensor con API meteorológica
#     # temp_sensor = request.form.get('temperatura')
#     # presion_sensor = request.form.get('presion')
#     # datos_externos = obtener_datos_meteorologicos()
#     return render_template('comparacion.html', datos=datos)
