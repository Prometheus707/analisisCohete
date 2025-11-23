from flask import Blueprint, render_template

# Crear blueprint para visualizaciones
bp = Blueprint('visualizaciones', __name__, url_prefix='/visualizaciones')

@bp.route('/')
def index():
    """Página de visualizaciones y gráficos"""
    return render_template('visualizaciones.html')

# Aquí el compañero puede agregar más rutas, por ejemplo:
# @bp.route('/grafico/<tipo>')
# def mostrar_grafico(tipo):
#     # Generar y mostrar gráfico
#     return render_template('grafico.html', tipo=tipo)
