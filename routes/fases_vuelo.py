from flask import Blueprint, render_template, request
import pandas as pd
import plotly.graph_objects as go
import os

bp = Blueprint('fases_vuelo', __name__, url_prefix='/fases-vuelo')

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
    # Limpiar header duplicado si existe
    if df.iloc[0]['timestamp_ms'] == 'timestamp_ms':
        df = df.iloc[1:].reset_index(drop=True)
    # Convertir a numérico
    df['time_s'] = pd.to_numeric(df['time_s'], errors='coerce')
    df['altitude_m'] = pd.to_numeric(df['altitude_m'], errors='coerce')
    return df.dropna(subset=['time_s', 'altitude_m'])

def identificar_fases(df):
    """Identifica las fases del vuelo basándose en altitud"""
    idx_apogeo = df['altitude_m'].idxmax()
    idx_despegue = df[df['altitude_m'] > 1.0].first_valid_index() or 0
    idx_aterrizaje = df[df['altitude_m'] < 1.0].last_valid_index()
    if idx_aterrizaje is None or idx_aterrizaje <= idx_apogeo:
        idx_aterrizaje = len(df) - 1
    
    return {
        'idx_despegue': idx_despegue,
        'idx_apogeo': idx_apogeo,
        'idx_aterrizaje': idx_aterrizaje,
        'altitud_maxima': df.loc[idx_apogeo, 'altitude_m'],
        'tiempo_apogeo': df.loc[idx_apogeo, 'time_s'],
        'tiempo_despegue': df.loc[idx_despegue, 'time_s'],
        'tiempo_aterrizaje': df.loc[idx_aterrizaje, 'time_s']
    }

def crear_grafico_fases(df, fases, titulo="🚀 Análisis de Fases del Vuelo"):
    """Genera gráfico interactivo de fases del vuelo con Plotly"""
    fig = go.Figure()
    
    # Fase Ascenso
    ascenso = df.iloc[fases['idx_despegue']:fases['idx_apogeo']+1]
    fig.add_trace(go.Scatter(
        x=ascenso['time_s'], y=ascenso['altitude_m'],
        mode='lines', name='Ascenso',
        line=dict(color='#1E88E5', width=3),
        hovertemplate='<b>Ascenso</b><br>Tiempo: %{x:.2f}s<br>Altitud: %{y:.2f}m<extra></extra>'
    ))
    
    # Fase Descenso
    descenso = df.iloc[fases['idx_apogeo']:fases['idx_aterrizaje']+1]
    fig.add_trace(go.Scatter(
        x=descenso['time_s'], y=descenso['altitude_m'],
        mode='lines', name='Descenso',
        line=dict(color='#FFA726', width=3),
        hovertemplate='<b>Descenso</b><br>Tiempo: %{x:.2f}s<br>Altitud: %{y:.2f}m<extra></extra>'
    ))
    
    # Marcadores
    fig.add_trace(go.Scatter(
        x=[fases['tiempo_despegue']], y=[df.loc[fases['idx_despegue'], 'altitude_m']],
        mode='markers+text', name='Despegue',
        marker=dict(color='green', size=12, symbol='triangle-up'),
        text=['Despegue'], textposition='top center'
    ))
    fig.add_trace(go.Scatter(
        x=[fases['tiempo_apogeo']], y=[fases['altitud_maxima']],
        mode='markers+text', name='Apogeo',
        marker=dict(color='red', size=15, symbol='star'),
        text=[f"Apogeo: {fases['altitud_maxima']:.2f}m"], textposition='top center'
    ))
    fig.add_trace(go.Scatter(
        x=[fases['tiempo_aterrizaje']], y=[df.loc[fases['idx_aterrizaje'], 'altitude_m']],
        mode='markers+text', name='Aterrizaje',
        marker=dict(color='purple', size=12, symbol='triangle-down'),
        text=['Aterrizaje'], textposition='bottom center'
    ))
    
    # Diseño del gráfico
    fig.update_layout(
        title={'text': titulo, 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#1565C0'}},
        xaxis_title='Tiempo (s)', yaxis_title='Altitud (m)',
        hovermode='closest', template='plotly_white', height=500,
        showlegend=True, 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def calcular_estadisticas(fases):
    """Calcula estadísticas del vuelo"""
    return {
        'altitud_maxima': f"{fases['altitud_maxima']:.2f}",
        'tiempo_apogeo': f"{fases['tiempo_apogeo']:.2f}",
        'duracion_ascenso': f"{fases['tiempo_apogeo'] - fases['tiempo_despegue']:.2f}",
        'duracion_descenso': f"{fases['tiempo_aterrizaje'] - fases['tiempo_apogeo']:.2f}",
        'duracion_total': f"{fases['tiempo_aterrizaje'] - fases['tiempo_despegue']:.2f}"
    }

# ============================================================================
# RUTAS
# ============================================================================

@bp.route('/')
def index():
    """Página principal - Análisis de fases del vuelo"""
    lanzamiento_id = request.args.get('lanzamiento', '1')
    
    try:
        # Cargar datos del lanzamiento seleccionado
        csv_file = LANZAMIENTOS.get(lanzamiento_id, LANZAMIENTOS['1'])
        csv_path = os.path.join('data', csv_file)
        
        # Procesar datos
        df = leer_csv_vuelo(csv_path)
        fases = identificar_fases(df)
        grafico = crear_grafico_fases(df, fases, f"🚀 Lanzamiento {lanzamiento_id} - Fases del Vuelo")
        estadisticas = calcular_estadisticas(fases)
        
        return render_template('fases_vuelo.html', 
                             grafico=grafico,
                             estadisticas=estadisticas,
                             lanzamientos=LANZAMIENTOS,
                             lanzamiento_actual=lanzamiento_id,
                             error=None)
    except Exception as e:
        return render_template('fases_vuelo.html', 
                             grafico=None, 
                             estadisticas=None,
                             lanzamientos=LANZAMIENTOS,
                             lanzamiento_actual=lanzamiento_id,
                             error=f"Error: {str(e)}")
