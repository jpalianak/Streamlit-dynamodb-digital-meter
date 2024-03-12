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

# Header  
st.header(r"$\normalsize  \color{black} \textbf{Monitoreo de la evolucion del consumo de corriente}$" , divider='gray')
st.header(r"$\tiny  \color{black} \textbf{Sistema de monitoreo en tiempo real del consumo de corriente procesando imagenes del amperimetro}$")
#st.write('')

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
st.markdown(footer,unsafe_allow_html=True)

def get_data():
  # Crear el cliente de DynamoDB usando boto3
  dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Reemplaza 'tu_region' con la región de tu tabla
  table_name = 'DynamoDBTableDigital'  # Reemplaza 'nombre_de_la_tabla' con el nombre de tu tabla en DynamoDB

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

image = Image.open("logo.png")
st.sidebar.header("Company name")
st.sidebar.image(image)

# Obtenemos los datos
df_orig = get_data()

row1_col1,row0_spacer, row1_col2 = st.columns((8, 0.1, 2))
with row1_col1:
  fig = px.line(data_frame=df_orig, x='Date', y='Value',markers=True)
  fig.update_layout(xaxis_title="Date", yaxis_title="Amper",width=1300,height=500)
  st.plotly_chart(fig)

with row1_col2:
  st.metric('Maximo registro',df_orig['Value'].max())
  st.metric('Producido el', df_orig.loc[df_orig['Value'].idxmax(), 'Date_num']) 
