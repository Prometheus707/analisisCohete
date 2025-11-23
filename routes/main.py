from flask import Blueprint, render_template

# Crear blueprint para la ruta principal
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Página principal con menú/dashboard"""
    return render_template('index.html')
