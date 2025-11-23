from flask import Blueprint, render_template

# Crear blueprint para validación de altitud
bp = Blueprint('validacion_altitud', __name__, url_prefix='/validacion-altitud')

@bp.route('/')
def index():
    """Página de validación de altitud teórica vs. real"""
    return render_template('validacion_altitud.html')

# Aquí puedes agregar más rutas, por ejemplo:
# @bp.route('/calcular', methods=['POST'])
# def calcular():
#     # Lógica para calcular error usando fórmula de Littlewood
#     # altura_teorica = request.form.get('altura_teorica')
#     # altura_real = request.form.get('altura_real')
#     # error = calcular_error_littlewood(altura_teorica, altura_real)
#     return render_template('resultados.html', error=error)
