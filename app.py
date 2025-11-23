from flask import Flask
import os
import importlib

# Inicializar aplicación Flask
app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'

# ============================================
# REGISTRO AUTOMÁTICO DE BLUEPRINTS
# ============================================
# Buscar y registrar automáticamente todos los blueprints en la carpeta 'routes/'
routes_dir = os.path.join(os.path.dirname(__file__), 'routes')

# Obtener todos los archivos .py en la carpeta routes/
for filename in os.listdir(routes_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        # Nombre del módulo sin la extensión .py
        module_name = filename[:-3]
        
        # Importar dinámicamente el módulo
        module = importlib.import_module(f'routes.{module_name}')
        
        # Si el módulo tiene un blueprint llamado 'bp', registrarlo
        if hasattr(module, 'bp'):
            app.register_blueprint(module.bp)
            print(f"✓ Blueprint registrado: {module_name}")

print(f"\n🚀 Total de blueprints registrados: {len(app.blueprints) - 1}")  # -1 porque Flask tiene un blueprint interno

if __name__ == '__main__':
    # Ejecutar servidor en modo desarrollo
    print("\n" + "="*50)
    print("🔥 Servidor Flask iniciado")
    print("📍 URL: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
