# =============================================================================
# app.py — Dashboard Interactivo: Sequía e Incendios en Corrientes, Argentina
# Capa Gold — Proyecto Capstone de Ingeniería en Sistemas
# Autor: Agus Meneses | Fuentes: NASA FIRMS · INTA SIGA
# =============================================================================

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES — Nombres de meses en español
# ─────────────────────────────────────────────────────────────────────────────
MESES_ESP_ABREV = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

MESES_ESP_FULL = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL DE LA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Corrientes — Sequía e Incendios Forestales",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# TEMA VISUAL PERSONALIZADO (CSS inyectado)
# ─────────────────────────────────────────────────────────────────────────────
_CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Variables globales ── */
:root {
    --bg-primary:    #0a0e17;
    --bg-card:       #111827;
    --bg-card-alt:   #1a2236;
    --accent-fire:   #ef4444;
    --accent-rain:   #3b82f6;
    --accent-gold:   #f59e0b;
    --accent-teal:   #14b8a6;
    --text-primary:  #f1f5f9;
    --text-muted:    #94a3b8;
    --text-label:    #cbd5e1;
    --border-subtle: rgba(148, 163, 184, 0.08);
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1629 0%, #111827 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

/* Sidebar labels: forzar visibilidad de todos los textos de widgets */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}

/* Sidebar slider tick values */
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"],
[data-testid="stSidebar"] .stSlider div[data-testid] > div {
    color: #e2e8f0 !important;
}

/* ── KPI Cards: contenedor flex con alto uniforme ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-alt) 100%);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    min-height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}

/* KPI label: permitir wrap y nunca truncar */
[data-testid="stMetricLabel"] {
    color: var(--text-label) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.35 !important;
    min-height: 2.4em;
    display: flex !important;
    align-items: flex-end !important;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] > div > div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    font-size: 1.9rem !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    margin-bottom: 10px;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary span {
    color: #e2e8f0 !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border-subtle) !important;
}

/* ── Plotly charts ── */
.stPlotlyChart {
    border-radius: 16px;
    overflow: hidden;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
}

/* ── Info / Warning / Error banners ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Columnas de KPI: forzar altura igual ── */
[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div {
    height: 100%;
}
[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div > [data-testid="stMetric"] {
    height: 100%;
}
</style>
"""
st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CARGA Y PREPROCESAMIENTO DEL DATASET (con caché)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos satelitales y climáticos...")
def cargar_datos() -> pd.DataFrame:
    """
    Lee el CSV final (Capa Gold) y genera la columna `Fecha` como datetime
    para facilitar el uso en gráficos de series de tiempo.
    """
    ruta_csv = os.path.join(
        os.path.dirname(__file__),
        "data", "data products", "Google Capstone - result.csv",
    )

    try:
        df = pd.read_csv(ruta_csv)
    except FileNotFoundError:
        st.error(
            "**No se encontró el archivo de datos.**\n\n"
            f"Ruta esperada: `{ruta_csv}`\n\n"
            "Asegurate de que el CSV esté en "
            "`data/data products/Google Capstone - result.csv`."
        )
        st.stop()

    # Crear columna de fecha para eje X (día = 1 de cada mes)
    df["Fecha"] = pd.to_datetime(
        df["Anio"].astype(str) + "-" + df["Mes"].astype(str).str.zfill(2) + "-01"
    )

    # Columna de etiqueta en español para hovers y ejes
    df["Mes_Nombre"] = df["Mes"].apply(lambda m: MESES_ESP_ABREV[m - 1])
    df["Etiqueta_Fecha"] = df["Mes_Nombre"] + " " + df["Anio"].astype(str)

    df.sort_values("Fecha", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


df_completo = cargar_datos()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Filtros interactivos y «Acerca de»
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding sin emojis — barra decorativa con gradiente
    st.markdown(
        """
        <div style="text-align:center; padding: 8px 0 16px 0;">
            <div style="width:40px; height:4px; margin:0 auto 12px auto;
                        background: linear-gradient(90deg, #f59e0b, #ef4444);
                        border-radius: 2px;"></div>
            <h2 style="margin:0; font-size:1.15rem; color:#f1f5f9;
                        letter-spacing:0.02em;">
                Corrientes · Fire Analytics
            </h2>
            <p style="margin:4px 0 0 0; font-size:0.75rem; color:#94a3b8;">
                Panel de Análisis Climático e Incendios
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Filtro de rango de años ──
    anio_min = int(df_completo["Anio"].min())
    anio_max = int(df_completo["Anio"].max())
    rango_anios = st.slider(
        "Rango de años",
        min_value=anio_min,
        max_value=anio_max,
        value=(anio_min, anio_max),
        help="Arrastrá los extremos para delimitar el período de análisis.",
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Selector de variable climática ──
    variable_climatica = st.selectbox(
        "Variable climática vs. Fuego",
        options=["Lluvia Total (mm)", "Temperatura Máxima (°C)"],
        index=0,
        help=(
            "Seleccioná qué variable climática comparar contra "
            "los Focos de Calor en el gráfico principal."
        ),
    )

    st.divider()

    # ── Acerca de ──
    st.markdown(
        """
        <div style="padding:2px 0;">
            <h4 style="font-size:0.85rem; color:#f59e0b; margin-bottom:8px;">
                Acerca de este proyecto
            </h4>
            <p style="font-size:0.78rem; color:#cbd5e1; line-height:1.55;">
                Análisis de la correlación histórica entre variables climáticas
                (sequía) y la catástrofe de incendios forestales en la provincia
                de <strong style="color:#f1f5f9;">Corrientes, Argentina</strong>
                (2016–2026).
            </p>
            <p style="font-size:0.78rem; color:#cbd5e1; line-height:1.55; margin-top:8px;">
                <strong style="color:#3b82f6;">Fuentes de datos:</strong>
            </p>
            <ul style="font-size:0.75rem; color:#cbd5e1; line-height:1.6; padding-left:18px;">
                <li><strong style="color:#f1f5f9;">NASA FIRMS</strong>
                    — Satélites VIIRS / MODIS
                    <br><span style="font-size:0.68rem; color:#94a3b8;">
                    Anomalías térmicas y FRP</span></li>
                <li><strong style="color:#f1f5f9;">INTA SIGA</strong>
                    — Estaciones meteorológicas
                    <br><span style="font-size:0.68rem; color:#94a3b8;">
                    Precipitaciones y temperaturas</span></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(
        """
        <p style="text-align:center; font-size:0.68rem; color:#94a3b8; margin:0;">
            Capstone Project · Ingeniería en Sistemas<br>
            <span style="color:#cbd5e1;">Agus Meneses · 2026</span>
        </p>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# FILTRADO DEL DATASET SEGÚN LA SELECCIÓN DEL USUARIO
# ─────────────────────────────────────────────────────────────────────────────
df = df_completo[
    (df_completo["Anio"] >= rango_anios[0])
    & (df_completo["Anio"] <= rango_anios[1])
].copy()


# ─────────────────────────────────────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding: 12px 0 4px 0;">
        <h1 style="font-size:2.1rem; margin:0; line-height:1.2;
                    background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;">
            Sequía e Incendios Forestales en Corrientes
        </h1>
        <p style="color:#cbd5e1; font-size:0.92rem; margin:6px 0 0 0;">
            Análisis histórico de correlación climática · Período
            <strong style="color:#f1f5f9;">{inicio}</strong> –
            <strong style="color:#f1f5f9;">{fin}</strong>
        </p>
    </div>
    """.format(inicio=rango_anios[0], fin=rango_anios[1]),
    unsafe_allow_html=True,
)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)





# ─────────────────────────────────────────────────────────────────────────────
# HELPER — Determinar el formato inteligente del eje X según el rango
# ─────────────────────────────────────────────────────────────────────────────
def configurar_eje_x_inteligente(fig, anio_inicio: int, anio_fin: int):
    """
    Ajusta dtick y tickformat del eje X según la cantidad de años mostrados.
    - 1 año:   cada mes   → "Ene 2020"
    - 2-3 años: trimestral → "Ene 2020"
    - 4-6 años: semestral  → "Ene 2020"
    - 7+ años:  anual      → "2020"
    """
    span = anio_fin - anio_inicio + 1

    if span <= 1:
        dtick_val = "M1"
        fmt = "%b %Y"  # será post-procesado a español vía ticktext
    elif span <= 3:
        dtick_val = "M3"
        fmt = "%b %Y"
    elif span <= 6:
        dtick_val = "M6"
        fmt = "%b %Y"
    else:
        dtick_val = "M12"
        fmt = "%Y"

    fig.update_xaxes(
        dtick=dtick_val,
        tickformat=fmt,
        tickangle=-45,
        gridcolor="rgba(148, 163, 184, 0.06)",
        tickfont=dict(size=10, color="#cbd5e1"),
    )

    # Generar ticks manuales en español cuando se muestran meses
    if fmt != "%Y":
        import datetime as _dt

        tick_vals = []
        tick_texts = []
        # Determinar intervalo en meses
        interval = int(dtick_val.replace("M", ""))
        current = _dt.date(anio_inicio, 1, 1)
        end = _dt.date(anio_fin, 12, 31)

        while current <= end:
            tick_vals.append(current.strftime("%Y-%m-%d"))
            mes_nombre = MESES_ESP_ABREV[current.month - 1]
            tick_texts.append(f"{mes_nombre} {current.year}")
            # Avanzar al siguiente tick
            new_month = current.month + interval
            new_year = current.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            current = _dt.date(new_year, new_month, 1)

        fig.update_xaxes(
            tickmode="array",
            tickvals=tick_vals,
            ticktext=tick_texts,
        )


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — Formato hover en español para fechas
# ─────────────────────────────────────────────────────────────────────────────
def fecha_hover_es(row):
    """Devuelve 'Ene 2020' para una fila con columnas Anio y Mes."""
    return f"{MESES_ESP_ABREV[row['Mes'] - 1]} {row['Anio']}"


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO PRINCIPAL — Doble Eje Y (Variable Climática vs. Focos de Calor)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h3 style="font-size:1.15rem; color:#e2e8f0; margin-bottom:2px;">
        Correlación Temporal: Variable Climática vs. Focos de Calor
    </h3>
    <p style="font-size:0.78rem; color:#94a3b8; margin-top:0;">
        Gráfico de doble eje &mdash; Las barras representan la variable climática
        seleccionada y la línea roja los focos de calor detectados por satélite.
    </p>
    """,
    unsafe_allow_html=True,
)

# Determinar columna y etiquetas según selección del usuario
if variable_climatica == "Lluvia Total (mm)":
    col_clima = "Lluvia_Total_mm"
    nombre_clima = "Lluvia Total"
    unidad_clima = "mm"
    color_barras = "#3b82f6"
    color_barras_alpha = "rgba(59, 130, 246, 0.7)"
else:
    col_clima = "Temp_Max_Mes"
    nombre_clima = "Temp. Máxima"
    unidad_clima = "°C"
    color_barras = "#14b8a6"
    color_barras_alpha = "rgba(20, 184, 166, 0.7)"

# Preparar hover texts en español
hover_fechas = df.apply(fecha_hover_es, axis=1)

# Construir el gráfico de doble eje
fig_principal = make_subplots(
    specs=[[{"secondary_y": True}]],
)

# Barras — Variable climática (Eje Y primario, izquierdo)
fig_principal.add_trace(
    go.Bar(
        x=df["Fecha"],
        y=df[col_clima],
        name=f"{nombre_clima} ({unidad_clima})",
        marker_color=color_barras_alpha,
        marker_line=dict(width=0),
        customdata=hover_fechas,
        hovertemplate=(
            f"<b>{nombre_clima}</b><br>"
            "Fecha: %{customdata}<br>"
            f"Valor: %{{y:.1f}} {unidad_clima}<extra></extra>"
        ),
    ),
    secondary_y=False,
)

# Línea — Focos de Calor (Eje Y secundario, derecho)
fig_principal.add_trace(
    go.Scatter(
        x=df["Fecha"],
        y=df["Total_Focos_Calor"],
        name="Focos de Calor",
        mode="lines+markers",
        line=dict(color="#ef4444", width=2.5),
        marker=dict(
            size=5,
            color="#ef4444",
            line=dict(width=1, color="#fca5a5"),
        ),
        customdata=hover_fechas,
        hovertemplate=(
            "<b>Focos de Calor</b><br>"
            "Fecha: %{customdata}<br>"
            "Focos: %{y:,.0f}<extra></extra>"
        ),
    ),
    secondary_y=True,
)

# ── Anotación de la crisis Feb 2022 — flecha vertical hacia arriba ──
crisis_feb_2022 = df[(df["Anio"] == 2022) & (df["Mes"] == 2)]
if not crisis_feb_2022.empty:
    fecha_crisis = crisis_feb_2022["Fecha"].iloc[0]
    focos_crisis = crisis_feb_2022["Total_Focos_Calor"].iloc[0]
    fig_principal.add_annotation(
        x=fecha_crisis,
        y=focos_crisis,
        yref="y2",
        text="<b>Crisis Feb 2022</b><br>1.185 focos",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#fbbf24",
        ax=0,       # Sin desplazamiento horizontal → flecha vertical
        ay=-80,     # Etiqueta bien arriba del punto
        font=dict(size=11, color="#fbbf24", family="Inter"),
        bgcolor="rgba(17, 24, 39, 0.9)",
        bordercolor="#fbbf24",
        borderwidth=1,
        borderpad=6,
    )

# ── Anotación de ago 2020 — flecha vertical hacia arriba ──
crisis_ago_2020 = df[(df["Anio"] == 2020) & (df["Mes"] == 8)]
if not crisis_ago_2020.empty:
    fecha_ago = crisis_ago_2020["Fecha"].iloc[0]
    focos_ago = crisis_ago_2020["Total_Focos_Calor"].iloc[0]
    fig_principal.add_annotation(
        x=fecha_ago,
        y=focos_ago,
        yref="y2",
        text="<b>Ago 2020</b><br>1.518 focos",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#f97316",
        ax=0,       # Sin desplazamiento horizontal → flecha vertical
        ay=-80,     # Etiqueta bien arriba del punto
        font=dict(size=11, color="#f97316", family="Inter"),
        bgcolor="rgba(17, 24, 39, 0.9)",
        bordercolor="#f97316",
        borderwidth=1,
        borderpad=6,
    )

# Layout del gráfico principal
fig_principal.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17, 24, 39, 0.6)",
    font=dict(family="Inter", color="#94a3b8"),
    height=560,
    margin=dict(l=60, r=60, t=80, b=60),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=12, color="#e2e8f0"),
        bgcolor="rgba(0,0,0,0)",
    ),
    hovermode="x unified",
    bargap=0.15,
)

# Eje X inteligente: colapsa meses en años según el rango seleccionado
configurar_eje_x_inteligente(fig_principal, rango_anios[0], rango_anios[1])

fig_principal.update_yaxes(
    title_text=f"{nombre_clima} ({unidad_clima})",
    secondary_y=False,
    gridcolor="rgba(148, 163, 184, 0.06)",
    title_font=dict(color=color_barras, size=13),
    tickfont=dict(color=color_barras, size=11),
)

fig_principal.update_yaxes(
    title_text="Focos de Calor (N)",
    secondary_y=True,
    gridcolor="rgba(0,0,0,0)",
    title_font=dict(color="#ef4444", size=13),
    tickfont=dict(color="#ef4444", size=11),
)

st.plotly_chart(
    fig_principal, width="stretch", config={"displayModeBar": False}
)


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO DE LÍNEA FRP — Intensidad Real: La Verdadera Devastación
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <h3 style="font-size:1.15rem; color:#e2e8f0; margin-bottom:2px;">
        La Verdadera Devastación: Intensidad del Fuego (FRP)
    </h3>
    <p style="font-size:0.78rem; color:#94a3b8; margin-top:0;">
        La línea muestra la <em>Intensidad Radiativa Total</em>
        (Fire Radiative Power, en MW) mes a mes &mdash; no cuántos focos hubo,
        sino la <strong style="color:#fbbf24;">energía real liberada por el
        fuego</strong>. El color de cada punto va de
        <span style="color:#3b82f6;">frío</span> a
        <span style="color:#fbbf24;">caliente</span> según la intensidad.
    </p>
    """,
    unsafe_allow_html=True,
)

# Preparar datos
df_frp = df.copy()
df_frp["Hover_Fecha"] = df_frp.apply(fecha_hover_es, axis=1)
frp_max = df_frp["Intensidad_Total_FRP"].max() if not df_frp.empty else 1

fig_frp = go.Figure()

# ── Área de relleno bajo la línea (gradiente sutil) ──
fig_frp.add_trace(
    go.Scatter(
        x=df_frp["Fecha"],
        y=df_frp["Intensidad_Total_FRP"],
        mode="lines",
        line=dict(width=0),
        fill="tozeroy",
        fillgradient=dict(
            type="vertical",
            colorscale=[
                [0.0, "rgba(239, 68, 68, 0.0)"],
                [0.3, "rgba(239, 68, 68, 0.05)"],
                [0.6, "rgba(249, 115, 22, 0.12)"],
                [1.0, "rgba(251, 191, 36, 0.22)"],
            ],
        ),
        showlegend=False,
        hoverinfo="skip",
    )
)

# ── Línea continua (blanca semitransparente) ──
fig_frp.add_trace(
    go.Scatter(
        x=df_frp["Fecha"],
        y=df_frp["Intensidad_Total_FRP"],
        mode="lines",
        line=dict(color="rgba(226, 232, 240, 0.35)", width=2, shape="spline"),
        showlegend=False,
        hoverinfo="skip",
    )
)

# ── Marcadores coloreados por intensidad (frío → caliente) ──
fig_frp.add_trace(
    go.Scatter(
        x=df_frp["Fecha"],
        y=df_frp["Intensidad_Total_FRP"],
        mode="markers",
        marker=dict(
            size=np.where(
                df_frp["Intensidad_Total_FRP"] > frp_max * 0.5, 14,
                np.where(df_frp["Intensidad_Total_FRP"] > frp_max * 0.15, 10, 6)
            ),
            color=df_frp["Intensidad_Total_FRP"],
            colorscale=[
                [0.0,  "#1e293b"],   # Gris oscuro — sin actividad
                [0.08, "#3b82f6"],   # Azul — frío
                [0.25, "#8b5cf6"],   # Violeta — tibio
                [0.50, "#ef4444"],   # Rojo — caliente
                [0.75, "#f97316"],   # Naranja — muy caliente
                [1.0,  "#fbbf24"],   # Dorado — catastrófico
            ],
            colorbar=dict(
                title=dict(
                    text="FRP (MW)",
                    font=dict(size=12, color="#94a3b8"),
                ),
                tickfont=dict(color="#94a3b8", size=10),
                thickness=14,
                len=0.85,
                bgcolor="rgba(0,0,0,0)",
            ),
            line=dict(width=1, color="rgba(255,255,255,0.2)"),
            opacity=0.92,
        ),
        customdata=np.column_stack([
            df_frp["Hover_Fecha"],
            df_frp["Intensidad_Total_FRP"].round(0),
            df_frp["Total_Focos_Calor"],
        ]),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Intensidad FRP: <b>%{customdata[1]:,.0f} MW</b><br>"
            "Focos de Calor: %{customdata[2]:,.0f}"
            "<extra></extra>"
        ),
        showlegend=False,
    )
)

# ── Anotación: Feb 2022 (pico dorado) ──
frp_feb_2022 = df_frp[(df_frp["Anio"] == 2022) & (df_frp["Mes"] == 2)]
if not frp_feb_2022.empty:
    fig_frp.add_annotation(
        x=frp_feb_2022["Fecha"].iloc[0],
        y=frp_feb_2022["Intensidad_Total_FRP"].iloc[0],
        text="<b>Feb 2022</b><br>14.807 MW",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#fbbf24",
        ax=0,
        ay=-80,
        font=dict(size=11, color="#fbbf24", family="Inter"),
        bgcolor="rgba(17, 24, 39, 0.92)",
        bordercolor="#fbbf24",
        borderwidth=1,
        borderpad=6,
    )

# ── Anotación: Ago 2020 (pico naranja) ──
frp_ago_2020 = df_frp[(df_frp["Anio"] == 2020) & (df_frp["Mes"] == 8)]
if not frp_ago_2020.empty:
    fig_frp.add_annotation(
        x=frp_ago_2020["Fecha"].iloc[0],
        y=frp_ago_2020["Intensidad_Total_FRP"].iloc[0],
        text="<b>Ago 2020</b><br>13.395 MW",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#f97316",
        ax=0,
        ay=-80,
        font=dict(size=11, color="#f97316", family="Inter"),
        bgcolor="rgba(17, 24, 39, 0.92)",
        bordercolor="#f97316",
        borderwidth=1,
        borderpad=6,
    )

fig_frp.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17, 24, 39, 0.6)",
    font=dict(family="Inter", color="#94a3b8"),
    height=480,
    margin=dict(l=60, r=60, t=40, b=60),
    xaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.06)",
        tickfont=dict(size=10, color="#cbd5e1"),
    ),
    yaxis=dict(
        title="Intensidad Radiativa Total — FRP (MW)",
        gridcolor="rgba(148, 163, 184, 0.06)",
        title_font=dict(color="#f97316", size=13),
        tickfont=dict(color="#f97316", size=11),
    ),
    showlegend=False,
    hovermode="x unified",
)

# Eje X inteligente consistente con el gráfico principal
configurar_eje_x_inteligente(fig_frp, rango_anios[0], rango_anios[1])

st.plotly_chart(
    fig_frp, width="stretch", config={"displayModeBar": False}
)




# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO SECUNDARIO — Estacionalidad (Heatmap mensual)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <h3 style="font-size:1.15rem; color:#e2e8f0; margin-bottom:2px;">
        Estacionalidad de Incendios — Mapa de Calor
    </h3>
    <p style="font-size:0.78rem; color:#94a3b8; margin-top:0;">
        Distribución de focos de calor por mes y año. Las celdas más intensas
        revelan la temporada alta histórica de incendios (agosto–septiembre) y
        los picos catastróficos.
    </p>
    """,
    unsafe_allow_html=True,
)

# Preparar la matriz pivote: filas = Año, columnas = Mes (en español)
pivot_estacional = df.pivot_table(
    values="Total_Focos_Calor",
    index="Anio",
    columns="Mes",
    aggfunc="sum",
    fill_value=0,
)
for m in range(1, 13):
    if m not in pivot_estacional.columns:
        pivot_estacional[m] = 0
pivot_estacional = pivot_estacional[sorted(pivot_estacional.columns)]

fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=pivot_estacional.values,
        x=MESES_ESP_ABREV,
        y=pivot_estacional.index.astype(str),
        colorscale=[
            [0.0,  "#0a0e17"],
            [0.05, "#1e1b4b"],
            [0.15, "#4c1d95"],
            [0.30, "#7c3aed"],
            [0.50, "#ef4444"],
            [0.75, "#f97316"],
            [1.0,  "#fbbf24"],
        ],
        colorbar=dict(
            title=dict(text="Focos", font=dict(size=12, color="#94a3b8")),
            tickfont=dict(color="#94a3b8", size=10),
            bgcolor="rgba(0,0,0,0)",
            thickness=14,
            len=0.9,
        ),
        hovertemplate=(
            "<b>%{y} · %{x}</b><br>"
            "Focos de Calor: %{z:,.0f}<extra></extra>"
        ),
        xgap=3,
        ygap=3,
    )
)

fig_heatmap.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8"),
    height=380,
    margin=dict(l=60, r=30, t=20, b=40),
    xaxis=dict(tickfont=dict(size=11, color="#cbd5e1"), side="bottom"),
    yaxis=dict(tickfont=dict(size=11, color="#cbd5e1"), autorange="reversed"),
)

st.plotly_chart(
    fig_heatmap, width="stretch", config={"displayModeBar": False}
)





# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN DE CONCLUSIONES — Hallazgos del EDA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <h3 style="font-size:1.15rem; color:#e2e8f0; margin-bottom:4px;">
        Hallazgos Clave del Análisis Exploratorio (EDA)
    </h3>
    <p style="font-size:0.78rem; color:#94a3b8; margin-top:0; margin-bottom:12px;">
        Tres fenómenos físicos y ambientales descubiertos durante el análisis
        que demuestran que la relación entre sequía e incendios
        <strong style="color:#cbd5e1;">no es lineal ni inmediata</strong>.
    </p>
    """,
    unsafe_allow_html=True,
)

# ── Hallazgo A: Efecto Esponja ──
with st.expander(
    "Hallazgo A — El Efecto Esponja (Latencia del Suelo)", expanded=True
):
    col_texto_a, col_dato_a = st.columns([3, 2])
    with col_texto_a:
        st.markdown(
            """
            **¿Qué observamos?** Existen meses con precipitaciones extremadamente
            bajas (por ejemplo, **abril de 2018** con apenas **21,9 mm**) que
            registraron **0 focos de calor**.

            **¿Por qué sucede?** Las lluvias torrenciales de los meses previos
            (enero de 2018: **327,8 mm**, marzo: **245,8 mm**) saturaron los
            humedales y esteros de la región. El suelo actúa como una *esponja*
            que retiene la humedad durante semanas o meses.

            **Implicancia:** La sequía no genera fuego inmediato si hay
            **retención hídrica previa**. Esto introduce un *desfase temporal*
            (lag) entre la caída de lluvias y la aparición de incendios,
            invalidando correlaciones lineales simplistas.
            """
        )
    with col_dato_a:
        st.info("**Caso emblemático: Abril 2018**")
        st.markdown(
            """
            | Variable | Valor |
            |:---------|------:|
            | Lluvia del mes | **21,9 mm** (seco) |
            | Focos de calor | **0** |
            | Lluvia Ene 2018 | **327,8 mm** |
            | Lluvia Mar 2018 | **245,8 mm** |
            """
        )

# ── Hallazgo B: Agotamiento de Biomasa ──
with st.expander(
    "Hallazgo B — Agotamiento de Biomasa (El Trauma Post-2022)", expanded=True
):
    col_texto_b, col_dato_b = st.columns([3, 2])
    with col_texto_b:
        st.markdown(
            """
            **¿Qué observamos?** Durante **enero y febrero de 2022** se
            registraron picos catastróficos sin precedentes: **887** y
            **1.185 focos mensuales** respectivamente, con intensidades
            radiativas (FRP) que superaron los **10.000 y 14.800 MW**.

            Sin embargo, en los meses inmediatamente posteriores (junio
            2022), los incendios cayeron a **0 focos** a pesar de que las
            condiciones climáticas seguían siendo secas (43,4 mm de lluvia).

            **¿Por qué?** El fuego de la crisis consumió **totalmente** el
            material orgánico disponible (vegetación, hojarasca, materia
            muerta). Sin *combustible biológico*, no hay ignición posible.

            **Implicancia:** Tras un mega-incendio, existe un período de
            *inmunidad post-trauma* donde el territorio ya no puede arder,
            independientemente del clima. Este fenómeno distorsiona los
            modelos predictivos clásicos.
            """
        )
    with col_dato_b:
        st.warning("**Crisis Enero–Febrero 2022**")
        st.markdown(
            """
            | Mes | Focos | FRP (MW) | Lluvia |
            |:----|------:|---------:|-------:|
            | Ene 2022 | **887** | 10.093 | 5,8 mm |
            | Feb 2022 | **1.185** | 14.807 | 13,4 mm |
            | Jun 2022 | **0** | 0 | 43,4 mm |
            | Jul 2022 | **1** | 0,33 | 30,6 mm |
            """
        )

# ── Hallazgo C: Ceguera Satelital ──
with st.expander(
    "Hallazgo C — Ceguera Satelital y Falsos Ceros", expanded=True
):
    col_texto_c, col_dato_c = st.columns([3, 2])
    with col_texto_c:
        st.markdown(
            """
            **¿Qué observamos?** Meses con precipitaciones extremas (como
            **noviembre de 2018** con **298,4 mm** y **diciembre de 2018**
            con **252,2 mm**) registraron **0 focos de calor**.

            **¿Es solo porque el suelo está mojado?** No. El fenómeno tiene
            una segunda causa técnica: las gruesas **capas de nubes
            cumulonimbus** que acompañan las tormentas bloquean los
            **sensores infrarrojos** de los satélites VIIRS y MODIS de la
            NASA.

            Esto significa que en un mes de tormentas persistentes, los
            satélites son *ciegos* al fuego que podría estar ocurriendo bajo
            la cobertura nubosa. Esos ceros no son necesariamente
            *verdaderos ceros*.

            **Implicancia:** Los datos satelitales tienen un **sesgo de
            observación** inherente. Cualquier modelo predictivo debe
            considerar esta limitación instrumental como un factor de
            incertidumbre.
            """
        )
    with col_dato_c:
        st.error("**Sesgo de observación satelital**")
        st.markdown(
            """
            | Mes | Lluvia | Focos | Nubes |
            |:----|-------:|------:|:-----:|
            | Nov 2018 | **298,4 mm** | 0 | Sí |
            | Dic 2018 | **252,2 mm** | 0 | Sí |
            | Ene 2019 | **552,4 mm** | 1 | Sí |
            """
        )
        st.markdown(
            """
            <p style="font-size:0.75rem; color:#cbd5e1; margin-top:8px;">
                Los satélites infrarrojos no pueden penetrar las nubes de
                tormenta (cumulonimbus). Los ceros pueden ser
                <strong>artefactos instrumentales</strong>, no ausencia
                real de fuego.
            </p>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
st.divider()
st.markdown(
    """
    <div style="text-align:center; padding:16px 0 24px 0;">
        <p style="font-size:0.78rem; color:#94a3b8; margin:0;">
            Dashboard desarrollado como producto final (Capa Gold) del
            <strong style="color:#cbd5e1;">
            Capstone Project — Google Data Analytics</strong>
        </p>
        <p style="font-size:0.72rem; color:#64748b; margin:4px 0 0 0;">
            Datos: NASA FIRMS (VIIRS/MODIS) · INTA SIGA · Período 2016–2026 ·
            Procesamiento: Databricks (PySpark) &rarr; Streamlit + Plotly
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
