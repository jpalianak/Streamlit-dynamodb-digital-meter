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


# auto refresh el primer numero son la cantidad de minutos
st_autorefresh(interval=1440 * 1000 * 60 * 1000, key="dataframerefresh")

zona_horaria = timezone(timedelta(hours=-4))

# Creamos un placeholder inicial vacío
spacer = st.empty()

header_html = """
<style>
.header {
    position: fixed;
    top: 30px;
    left: 30px; /* Ajuste la posición izquierda según sea necesario */
    width: 100%;
    background-color: white;
    color: black;
    text-align: left;
    display: flex;
    align-items: center; /* Centra verticalmente los elementos */
}

.header img {
    height: 100px; /* Ajuste la altura de la imagen según sea necesario */
    margin-right: 100px; /* Espacio entre la imagen y el texto */
}

</style>
<div class="header">
    <!-- Comentamos la línea de la imagen para ocultarla -->
    <img src="https://raw.githubusercontent.com/jpalianak/Streamlit-dynamodb-digital-meter/main/airbiz.png" alt="Descripción de la imagen">
    <div>
        <h1 class="title">Monitoreo de la evolución del consumo de corriente</h1>
        <p style="font-size: 20px;">Sistema de monitoreo en tiempo real del consumo de corriente procesando imágenes con IA</p>
    </div>
</div>
"""

# Footer
footer="""<style>
a:link , a:visited{color: blue;background-color: transparent;text-decoration: underline;}
a:hover,  a:active {color: red;background-color: transparent;text-decoration: underline;}
.footer {position: fixed;left: 0;bottom: 0;width: 100%;background-color: white;color: black;text-align: center;}
</style>
<div class="footer">
<p>Developed by AIRBIZ <a style='display: block; text-align: center;' href="https://www.airbiz.com.ar/" target="_blank">www.airbiz.com.ar</a></p>
</div>
"""

st.markdown(header_html,unsafe_allow_html=True)
#st.markdown(footer,unsafe_allow_html=True)

def get_data(table_name):
  # Crear el cliente de DynamoDB usando boto3
  dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Reemplaza 'tu_region' con la región de tu tabla

  # Obtener la tabla de DynamoDB
  table = dynamodb.Table(table_name)

  # Escanear toda la tabla
  response = table.scan()
  items = response['Items']

  # Convertir los datos a un DataFrame de Pandas
  df = pd.DataFrame(items)
  df['Date_num'] = pd.to_datetime(df['Date']).astype('int64') // 10**9
  df['Value'] = pd.to_numeric(df['Value'])
  df = df.sort_values(by='Date_num')
  return df

# Obtenemos los datos
df_orig_cnn = get_data('DynamoDBTable-SAM-Digital-Meter-SSD')
df_orig_opencv = get_data('DynamoDBTable-SAM-Digital-Meter-OpenCV')

st.write('')   

# Crear el gráfico con Plotly Express
fig = px.line()

# Añadir traza para CNN
fig.add_scatter(
    x=df_orig_cnn['Date'],
    y=df_orig_cnn['Value']*10,
    mode='lines+markers',
    line=dict(color='blue', shape='spline'),  # Color azul para CNN
    name='SSD-MobileNet'  # Nombre para la leyenda
)

# Añadir traza para OpenCV
fig.add_scatter(
    x=df_orig_opencv['Date'],
    y=df_orig_opencv['Value']*10,
    mode='lines+markers',
    line=dict(color='red', shape='spline'),  # Color rojo para OpenCV
    name='OpenCV'  # Nombre para la leyenda
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

row1_col1,row0_spacer, row1_col2,row1_spacer, row1_col3= st.columns((0.3, 0.05, 0.3,0.05,0.3))
with row1_col1:
    max_event = df_orig_cnn['Value'].max()
    st.write(f'<h3><span style="font-weight: bold;">Máximo valor CNN:</span> <span style="font-style: italic;">{max_event} Amp</span></h3>', unsafe_allow_html=True)  

with row1_col2:
    fecha_event = df_orig_cnn.loc[df_orig_cnn['Value'].idxmax(), 'Date_num']
    fecha_event = pd.to_datetime(fecha_event * 10**9)
    st.write(f'<h3><span style="font-weight: bold;">Fecha máximo valor CNN:</span> <span style="font-style: italic;">{fecha_event}</span></h3>', unsafe_allow_html=True)

with row1_col3:
    mean_event = round(df_orig_cnn['Value'].mean(), 2)
    st.write(f'<h3><span style="font-weight: bold;">Valor promedio CNN:</span> <span style="font-style: italic;">{mean_event} Amp</span></h3>', unsafe_allow_html=True)

# Mostrar métricas para OpenCV
row2_col1, row2_spacer, row2_col2, row2_spacer, row2_col3 = st.columns((0.3, 0.05, 0.3, 0.05, 0.3))

with row2_col1:
    max_event_opencv = df_orig_opencv['Value'].max()
    st.write(f'<h3><span style="font-weight: bold;">Máximo valor OpenCV:</span> <span style="font-style: italic;">{max_event_opencv} Amp</span></h3>', unsafe_allow_html=True)  

with row2_col2:
    fecha_event_opencv = df_orig_opencv.loc[df_orig_opencv['Value'].idxmax(), 'Date_num']
    fecha_event_opencv = pd.to_datetime(fecha_event_opencv * 10**9)
    st.write(f'<h3><span style="font-weight: bold;">Fecha máximo valor OpenCV:</span> <span style="font-style: italic;">{fecha_event_opencv}</span></h3>', unsafe_allow_html=True)

with row2_col3:
    mean_event_opencv = round(df_orig_opencv['Value'].mean(), 2)
    st.write(f'<h3><span style="font-weight: bold;">Valor promedio OpenCV:</span> <span style="font-style: italic;">{mean_event_opencv} Amp</span></h3>', unsafe_allow_html=True)
