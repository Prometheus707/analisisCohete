from flask import Flask, render_template
import os
import importlib
import csv

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

#metodo littlewood

G = 9.78


def calcular_altura_littlewood(t):
    return (G * (t ** 2)) / 8


def calcular_error(ht, hr):
    return abs(ht - hr) / hr * 100


def analizar_csv(path):
    tiempos = []
    alturas = []

    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                tiempos.append(float(row["time_s"]))
                alturas.append(float(row["altitude_m"]))
            except:
                pass

    inicio = None
    for i in range(1, len(alturas)):
        if alturas[i] > 0 and alturas[i] > alturas[i - 1]:
            inicio = i
            break

    altura_real = max(alturas)
    tiempo_total = tiempos[-1]

    altura_teo = calcular_altura_littlewood(tiempo_total)
    error = calcular_error(altura_teo, altura_real)

    return {
        "archivo": os.path.basename(path),
        "tiempo_total": round(tiempo_total, 2),
        "altura_real": round(altura_real, 2),
        "altura_teorica": round(altura_teo, 2),
        "error_porcentual": round(error, 2),
        "inicio_ascenso": inicio,
        "tiempo_inicio_ascenso": tiempos[inicio] if inicio else None
    }


@app.get("/")
def index():
    return render_template("index.html", title="Inicio")


@app.get("/resultados")
def resultados():
    base = "data"
    vuelos = []

    for archivo in os.listdir(base):
        if archivo.endswith(".csv"):
            vuelos.append(analizar_csv(os.path.join(base, archivo)))

    return render_template("resultados.html",
                           title="Resultados",
                           vuelos=vuelos)


if __name__ == "__main__":
    app.run(debug=True)
if __name__ == '__main__':
    # Ejecutar servidor en modo desarrollo
    print("\n" + "="*50)
    print("🔥 Servidor Flask iniciado")
    print("📍 URL: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
