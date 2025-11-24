from flask import Blueprint, render_template, request
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


bp = Blueprint('analisis_paracaidas', __name__, url_prefix='/analisis-paracaidas')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
LANZAMIENTOS = {
    '1': 'lanzamiento_1.csv',
    '2': 'lanzamiento_2.csv',
    '3': 'lanzamiento_3.csv',
    '4': 'lanzamiento_4.csv'
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def leer_csv_vuelo(csv_path):
    """Lee y limpia datos de CSV de vuelo"""
    df = pd.read_csv(csv_path)
    if df.iloc[0]['timestamp_ms'] == 'timestamp_ms':
        df = df.iloc[1:].reset_index(drop=True)
    df['time_s'] = pd.to_numeric(df['time_s'], errors='coerce')
    df['pressure_pa'] = pd.to_numeric(df['pressure_pa'], errors='coerce')
    df['altitude_m'] = pd.to_numeric(df['altitude_m'], errors='coerce')
    return df.dropna(subset=['time_s', 'pressure_pa'])

def calcular_tasa_cambio_presion(df):
    """Calcula la tasa de cambio de presión (derivada)"""
    df['delta_pressure'] = df['pressure_pa'].diff()
    df['delta_time'] = df['time_s'].diff()
    df['tasa_presion'] = df['delta_pressure'] / df['delta_time']
    df['tasa_suavizada'] = df['tasa_presion'].rolling(window=5, center=True).mean()
    return df

def detectar_despliegue_paracaidas(df):
    """Detecta apertura pasiva del paracaídas al inicio del descenso"""
    idx_apogeo = df['altitude_m'].idxmax()
    tiempo_apogeo = df.loc[idx_apogeo, 'time_s']
    
    # Paracaídas se abre pasivamente poco después del apogeo
    ventana_inicio = tiempo_apogeo + 0.3
    ventana_fin = tiempo_apogeo + 2.0
    
    descenso = df[(df['time_s'] >= ventana_inicio) & (df['time_s'] <= ventana_fin)].copy()
    
    if len(descenso) < 5:
        idx_estimado = df[df['time_s'] > tiempo_apogeo].head(5).index[-1] if len(df[df['time_s'] > tiempo_apogeo]) >= 5 else idx_apogeo + 3
        if idx_estimado >= len(df):
            idx_estimado = idx_apogeo + 1
        
        return {
            'idx_despliegue': idx_estimado,
            'tiempo_despliegue': df.loc[idx_estimado, 'time_s'],
            'altitud_despliegue': df.loc[idx_estimado, 'altitude_m'],
            'presion_despliegue': df.loc[idx_estimado, 'pressure_pa']
        }
    
    # Buscar donde la tasa se estabiliza (paracaídas totalmente abierto)
    tasa_suavizada = descenso['tasa_suavizada'].fillna(0)
    variacion = tasa_suavizada.rolling(window=3).std()
    
    if len(variacion.dropna()) > 0:
        idx_despliegue = variacion.idxmin()
    else:
        idx_despliegue = descenso.index[len(descenso)//2]
    
    return {
        'idx_despliegue': idx_despliegue,
        'tiempo_despliegue': df.loc[idx_despliegue, 'time_s'],
        'altitud_despliegue': df.loc[idx_despliegue, 'altitude_m'],
        'presion_despliegue': df.loc[idx_despliegue, 'pressure_pa']
    }

def crear_grafico_paracaidas(df, despliegue, titulo="🪂 Análisis del Paracaídas"):
    """Genera gráfico de presión y tasa de cambio con Plotly"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Presión Atmosférica', 'Tasa de Cambio de Presión'),
        vertical_spacing=0.12
    )
    
    # Gráfica 1: Presión vs Tiempo
    fig.add_trace(
        go.Scatter(
            x=df['time_s'], y=df['pressure_pa'],
            mode='lines', name='Presión',
            line=dict(color='#2196F3', width=2),
            hovertemplate='Tiempo: %{x:.2f}s<br>Presión: %{y:.0f} Pa<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Gráfica 2: Tasa de cambio
    fig.add_trace(
        go.Scatter(
            x=df['time_s'], y=df['tasa_suavizada'],
            mode='lines', name='Tasa de Cambio',
            line=dict(color='#FF9800', width=2),
            hovertemplate='Tiempo: %{x:.2f}s<br>Tasa: %{y:.1f} Pa/s<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Marcar despliegue
    if despliegue:
        t = despliegue['tiempo_despliegue']
        p = despliegue['presion_despliegue']
        
        fig.add_trace(
            go.Scatter(
                x=[t], y=[p],
                mode='markers+text',
                name='Apertura Paracaídas',
                marker=dict(color='red', size=15, symbol='star'),
                text=['Apertura'],
                textposition='top center'
            ),
            row=1, col=1
        )
        
        fig.add_vline(x=t, line_dash="dash", line_color="red", opacity=0.5)
    
    fig.update_layout(
        title={'text': titulo, 'x': 0.5, 'xanchor': 'center'},
        height=700,
        showlegend=True,
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="Tiempo (s)", showgrid=True)
    fig.update_yaxes(title_text="Presión (Pa)", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="Tasa (Pa/s)", row=2, col=1, showgrid=True)
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def calcular_estadisticas(df, despliegue):
    """Calcula estadísticas del análisis"""
    idx_apogeo = df['altitude_m'].idxmax()
    
    stats = {
        'apogeo_altitud': f"{df.loc[idx_apogeo, 'altitude_m']:.2f}",
        'apogeo_tiempo': f"{df.loc[idx_apogeo, 'time_s']:.2f}"
    }
    
    if despliegue:
        stats['despliegue_tiempo'] = f"{despliegue['tiempo_despliegue']:.2f}"
        stats['despliegue_altitud'] = f"{despliegue['altitud_despliegue']:.2f}"
        stats['despliegue_confirmado'] = "Sí"
    else:
        stats['despliegue_tiempo'] = "No detectado"
        stats['despliegue_altitud'] = "N/A"
        stats['despliegue_confirmado'] = "No"
    
    return stats

# ============================================================================
# RUTAS
# ============================================================================

@bp.route('/')
def index():
    """Página principal - Análisis de paracaídas"""
    lanzamiento_id = request.args.get('lanzamiento', '1')
    
    try:
        csv_file = LANZAMIENTOS.get(lanzamiento_id, LANZAMIENTOS['1'])
        csv_path = os.path.join('data', csv_file)
        
        df = leer_csv_vuelo(csv_path)
        df = calcular_tasa_cambio_presion(df)
        despliegue = detectar_despliegue_paracaidas(df)
        grafico = crear_grafico_paracaidas(df, despliegue, f"🪂 Lanzamiento {lanzamiento_id} - Análisis de Paracaídas")
        estadisticas = calcular_estadisticas(df, despliegue)
        
        return render_template('analisis_paracaidas.html',
                             grafico=grafico,
                             estadisticas=estadisticas,
                             lanzamientos=LANZAMIENTOS,
                             lanzamiento_actual=lanzamiento_id,
                             error=None)
    except Exception as e:
        return render_template('analisis_paracaidas.html',
                             grafico=None,
                             estadisticas=None,
                             lanzamientos=LANZAMIENTOS,
                             lanzamiento_actual=lanzamiento_id,
                             error=f"Error: {str(e)}")
