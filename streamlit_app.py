import streamlit as st
import pandas as pd
import time
import boto3
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(layout="wide")

# Función para obtener los datos de DynamoDB
def get_data(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = response['Items']
    df = pd.DataFrame(items)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Value'] = pd.to_numeric(df['Value'])
    df = df.sort_values(by='Date')
    return df

# Cargar los datos de DynamoDB
df_orig_cnn = get_data('DynamoDBTable-SAM-Digital-Meter-SSD')
df_orig_opencv = get_data('DynamoDBTable-SAM-Digital-Meter-OpenCV')

# Selección de fecha inicial y final para los datos
start_date = datetime(2024, 12, 1)
end_date = datetime(2024, 12, 3)
df_cnn_filtered = df_orig_cnn[(df_orig_cnn['Date'] >= start_date) & (df_orig_cnn['Date'] <= end_date)]
df_opencv_filtered = df_orig_opencv[(df_orig_opencv['Date'] >= start_date) & (df_orig_opencv['Date'] <= end_date)]

# Crear un contenedor para el gráfico
placeholder = st.empty()

# Configuración del gráfico inicial
fig = go.Figure()
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Amper",
    width=1700,
    height=600,
    title='Simulación en tiempo real: SSD-MobileNet y OpenCV',
    legend_title="Modelo de Detección"
)

# Iteración para simular la entrada de datos
factor = 100  # Factor de escala
delay = 0.5  # Delay entre actualizaciones en segundos

for i in range(1, len(df_cnn_filtered) + 1):
    # Filtrar datos progresivamente
    cnn_data = df_cnn_filtered.iloc[:i]
    opencv_data = df_opencv_filtered.iloc[:i]

    # Actualizar las trazas del gráfico
    fig.data = []  # Limpiar trazas previas
    fig.add_scatter(
        x=cnn_data['Date'],
        y=cnn_data['Value'] * factor,
        mode='lines+markers',
        line=dict(color='blue', shape='linear'),
        name='SSD-MobileNet'
    )
    fig.add_scatter(
        x=opencv_data['Date'],
        y=opencv_data['Value'] * factor,
        mode='lines+markers',
        line=dict(color='red', shape='linear'),
        name='OpenCV'
    )

    # Mostrar el gráfico en el contenedor
    placeholder.plotly_chart(fig)

    # Pausa para simular el ingreso de datos
    time.sleep(delay)


