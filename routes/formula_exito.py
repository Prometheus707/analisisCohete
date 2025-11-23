from flask import Blueprint, render_template

# Crear blueprint para fórmula del éxito
bp = Blueprint('formula_exito', __name__, url_prefix='/formula-exito')

@bp.route('/')
def index():
    """Página de análisis de fórmula del éxito"""
    return render_template('formula_exito.html')

# Aquí puedes agregar más rutas, por ejemplo:
# @bp.route('/optimizar', methods=['POST'])
# def optimizar():
#     # Lógica para determinar mejor combinación presión/agua
#     # datos_presion = request.form.getlist('presion')
#     # datos_agua = request.form.getlist('agua')
#     # datos_apogeo = request.form.getlist('apogeo')
#     # mejor_combinacion = analizar_combinaciones(datos_presion, datos_agua, datos_apogeo)
#     return render_template('resultados_formula.html', combinacion=mejor_combinacion)
