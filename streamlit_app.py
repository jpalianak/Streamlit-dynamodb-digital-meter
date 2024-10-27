import streamlit as st
import pandas as pd
import time
import boto3
import plotly.express as px
from datetime import datetime, timezone, timedelta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from PIL import Image

st.set_page_config(layout="wide")

# Auto refresh (primer número son los minutos)
st_autorefresh(interval=1440 * 1000 * 60 * 1000, key="dataframerefresh")

zona_horaria = timezone(timedelta(hours=-4))

# Placeholder inicial vacío
spacer = st.empty()

header_html = """
<style>
.header {
    position: fixed;
    top: 30px;
    left: 30px;
    width: 100%;
    background-color: white;
    color: black;
    text-align: left;
    display: flex;
    align-items: center;
}
.header img {
    height: 100px;
    margin-right: 100px;
}
</style>
<div class="header">
    <img src="https://raw.githubusercontent.com/jpalianak/Streamlit-dynamodb-digital-meter/main/airbiz.png" alt="Descripción de la imagen" style="display: none;">
    <div>
        <h1 class="title">Monitoreo de la evolución del consumo de corriente</h1>
        <p style="font-size: 20px;">Sistema de monitoreo en tiempo real del consumo de corriente procesando imágenes con IA</p>
    </div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

def get_data(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = response['Items']
    df = pd.DataFrame(items)
    df['Date_num'] = pd.to_datetime(df['Date']).astype('int64') // 10**9
    df['Date'] = pd.to_datetime(df['Date'])
    df['Value'] = pd.to_numeric(df['Value'])
    df = df.sort_values(by='Date_num')
    return df

# Obtenemos los datos
df_orig_cnn = get_data('DynamoDBTable-SAM-Digital-Meter-SSD')
df_orig_opencv = get_data('DynamoDBTable-SAM-Digital-Meter-OpenCV')

# Inicializar el valor en session_state para que persista entre recargas
if 'start_date' not in st.session_state:
    st.session_state['start_date'] = df_orig_cnn['Date'].min().date()

# Barra lateral para opciones de visualización
st.sidebar.header("Opciones de visualización")

# Separación para las curvas a graficar
st.sidebar.markdown("### Curvas a graficar")
show_cnn = st.sidebar.checkbox('Mostrar curva SSD-MobileNet', value=True)
show_opencv = st.sidebar.checkbox('Mostrar curva OpenCV', value=True)

# Espacio entre secciones
st.sidebar.markdown("---")  # Línea divisoria para separar secciones

# Separación para la selección de fecha
#st.sidebar.markdown("### Selección de fecha")
#start_date = st.sidebar.date_input("Fecha de inicio", st.session_state['start_date'])
start_date = datetime(2024, 09, 28) 

# Filtrar los datos a partir de la fecha seleccionada
df_cnn_filtered = df_orig_cnn[df_orig_cnn['Date'] >= pd.to_datetime(start_date)]
df_opencv_filtered = df_orig_opencv[df_orig_opencv['Date'] >= pd.to_datetime(start_date)]

# Espacio entre secciones
st.sidebar.markdown("---")  # Otra línea divisoria

# Separación para el factor de escala
st.sidebar.markdown("### Factor de escala")
factor = st.sidebar.slider('Valor', min_value=1, max_value=20, value=10, step=1)

# Crear el gráfico con Plotly Express
fig = px.line()

# Añadir traza para CNN
if show_cnn:
    fig.add_scatter(
        x=df_cnn_filtered['Date'],
        y=df_cnn_filtered['Value']*factor,
        mode='lines+markers',
        line=dict(color='blue', shape='linear'),
        name='SSD-MobileNet'
    )

# Añadir traza para OpenCV
if show_opencv:
    fig.add_scatter(
        x=df_opencv_filtered['Date'] + pd.Timedelta(seconds=5),
        y=df_opencv_filtered['Value']*factor,
        mode='lines+markers',
        line=dict(color='red', shape='linear'),
        name='OpenCV'
    )

# Configuración del layout del gráfico
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Amper",
    width=1700,
    height=600,
    title='Comparación de valores entre SSD-MobileNet y OpenCV',
    legend_title="Modelo de Detección"
)

st.plotly_chart(fig)

# Métricas para CNN
if show_cnn:
    row1_col1, row0_spacer, row1_col2, row1_spacer, row1_col3 = st.columns((0.3, 0.05, 0.3, 0.05, 0.3))
    with row1_col1:
        max_event = round(df_cnn_filtered['Value'].max() * factor, 2)
        st.markdown(f'<h4 style="font-size: 20px;"><strong>Máximo valor CNN:</strong> {max_event} Amp</h4>', unsafe_allow_html=True)

    with row1_col2:
        fecha_event = df_cnn_filtered.loc[df_cnn_filtered['Value'].idxmax(), 'Date_num']
        fecha_event = pd.to_datetime(fecha_event * 10**9)
        st.markdown(f'<h4 style="font-size: 20px;"><strong>Fecha máximo valor CNN:</strong> {fecha_event}</h4>', unsafe_allow_html=True)

    with row1_col3:
        mean_event = round(df_cnn_filtered['Value'].mean() * factor, 2)
        st.markdown(f'<h4 style="font-size: 20px;"><strong>Valor promedio CNN:</strong> {mean_event} Amp</h4>', unsafe_allow_html=True)

# Métricas para OpenCV
if show_opencv:
    row2_col1, row2_spacer, row2_col2, row2_spacer, row2_col3 = st.columns((0.3, 0.05, 0.3, 0.05, 0.3))
    with row2_col1:
        max_event_opencv = round(df_opencv_filtered['Value'].max() * factor, 2)
        st.markdown(f'<h4 style="font-size: 20px;"><strong>Máximo valor OpenCV:</strong> {max_event_opencv} Amp</h4>', unsafe_allow_html=True)

    with row2_col2:
        fecha_event_opencv = df_opencv_filtered.loc[df_opencv_filtered['Value'].idxmax(), 'Date_num']
        fecha_event_opencv = pd.to_datetime(fecha_event_opencv * 10**9)
        st.markdown(f'<h4 style="font-size: 20px;"><strong>Fecha máximo valor OpenCV:</strong> {fecha_event_opencv}</h4>', unsafe_allow_html=True)

    with row2_col3:
        mean_event_opencv = round(df_opencv_filtered['Value'].mean() * factor, 2)
        st.markdown(f'<h4 style="font-size: 20px;"><strong>Valor promedio OpenCV:</strong> {mean_event_opencv} Amp</h4>', unsafe_allow_html=True)

