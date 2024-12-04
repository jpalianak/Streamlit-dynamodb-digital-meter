import streamlit as st
import pandas as pd
import time
import boto3
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(layout="wide")

# Agregar título y descripción
st.title("Simulación en Tiempo Real del Consumo de Corriente")
st.markdown("Este sistema simula el ingreso de datos en tiempo real desde dos modelos diferentes: **SSD-MobileNet** y **OpenCV**.")

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
start_date = datetime(2024, 10, 7, 21, 50, 0)  # 1 de diciembre, 08:00:00
end_date = datetime(2024, 10, 7, 23, 20, 0)   # 1 de diciembre, 20:00:00
df_cnn_filtered = df_orig_cnn[(df_orig_cnn['Date'] >= start_date) & (df_orig_cnn['Date'] <= end_date)]
df_opencv_filtered = df_orig_opencv[(df_orig_opencv['Date'] >= start_date) & (df_orig_opencv['Date'] <= end_date)]

# Aplicar desplazamiento a la curva OpenCV (e.g., retraso de 10 minutos)
time_shift = timedelta(seconds=5)
df_opencv_filtered['Date'] = df_opencv_filtered['Date'] + time_shift

# Crear un contenedor para el gráfico
placeholder = st.empty()

# Configuración del gráfico inicial
fig = go.Figure()
fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Corriente (Amper)",
    width=1700,
    height=600,
    title="Comparación de Valores entre SSD-MobileNet y OpenCV",
    legend_title="Modelo de Detección"
)

# Ajustes de simulación
factor = 10  # Factor de escala
delay = 0.5  # Delay entre actualizaciones en segundos
max_points = max(len(df_cnn_filtered), len(df_opencv_filtered))  # Máximo número de puntos

# Iteración sincronizada para las dos curvas
for i in range(1,2):# max_points + 1):
    # Progresión de puntos (sin exceder el índice máximo)
    cnn_data = df_cnn_filtered.iloc[:min(i, len(df_cnn_filtered))]
    opencv_data = df_opencv_filtered.iloc[:min(i, len(df_opencv_filtered))]

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
    placeholder.plotly_chart(fig, use_container_width=True)

    # Pausa para simular el ingreso de datos
    time.sleep(delay)

# Footer
st.markdown("---")
st.markdown("**Desarrollado por: [Tu Nombre o Empresa](https://github.com/jpalianak)** - Proyecto de Monitoreo de Consumo de Corriente con IA y AWS.")



