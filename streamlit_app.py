import streamlit as st
import pandas as pd
import time
import boto3
import plotly.express as px
from datetime import datetime, timezone, timedelta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

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
  
def main():
  # Obtenemos los datos
  df_orig = get_data()

  row1_col1,row0_spacer, row1_col2 = st.columns((6, 0.1, 2))
  with row1_col1:
    fig = px.line(data_frame=df_orig, x='Date', y='Value',markers=True)
    fig.update_layout(xaxis_title="Date", yaxis_title="Amper",width=1000,height=500)
    st.plotly_chart(fig)

  with row1_col2:
    st.write('Maximo registro')
    st.metric(df_orig['Value'].max())
    st.write('Producido el')
    st.metric(df_orig.loc[df_orig['Value'].idxmax(), 'Date_num'])
    
    
  #print(df_orig.head())
  #fig.update_yaxes(range=[0, 10]) 

  # Obtener la fecha actual
  #hoy = datetime.date.today()
  #hoy = datetime.now(zona_horaria).date()

  # Calcular el día de la semana actual (0 es lunes, 6 es domingo)
  #dia_semana_actual = hoy.weekday()

  # Calcular el desplazamiento necesario para llegar al lunes (inicio de semana laboral)
  #inicio_semana_laboral = hoy - datetime.timedelta(days=dia_semana_actual)
  #inicio_semana_laboral = hoy - timedelta(days=dia_semana_actual)

  # Calcular el desplazamiento necesario para llegar al viernes (final de semana laboral)
  #fin_semana_laboral = hoy + datetime.timedelta(days=(4 - dia_semana_actual))
  #fin_semana_laboral = hoy + timedelta(days=(4 - dia_semana_actual))
  
  # Obtener el primer día del mes actual
  #inicio_mes = hoy.replace(day=1)

  # Obtener el último día del mes actual
  #if hoy.month == 12:  # Si el mes actual es diciembre
  #    siguiente_mes = inicio_mes.replace(year=inicio_mes.year + 1, month=1)
  #else:
  #    siguiente_mes = inicio_mes.replace(month=inicio_mes.month + 1)
  #fin_mes = siguiente_mes - datetime.timedelta(days=1)
  #fin_mes = siguiente_mes - timedelta(days=1)

  #Main, Maq1, Maq2, Maq3, Maq4, Maq5, Maq6 = st.tabs(["Resumen", "Maquina 1", "Maquina 2", "Maquina 3", "Maquina 4", "Maquina 5", "Maquina 6"])

 # with Main:
 #   row1_col1, row1_col2, row1_col3 = st.columns(3)
 #   with row1_col1:
 #     d_ini = pd.to_datetime(hoy).date()
 #     d_fin = pd.to_datetime(hoy).date()
 #     fig = line_graphic_main(df_orig,"maq1",d_ini,d_fin)
 #     fig.update_layout(yaxis_title="Productividad Diaria [%] - Maquina 1")
 #     st.write(fig)
 #   with row1_col2:
 #     d_ini = pd.to_datetime(hoy).date()
 #     d_fin = pd.to_datetime(hoy).date()
 #     fig = line_graphic_main(df_orig,"maq2",d_ini,d_fin) 
 #     fig.update_layout(yaxis_title="Productividad Diaria [%] - Maquina 2")
 #     st.write(fig)
 #   with row1_col3:
 #     d_ini = pd.to_datetime(hoy).date()
 #     d_fin = pd.to_datetime(hoy).date()
 #     fig = line_graphic_main(df_orig,"maq3",d_ini,d_fin)
 #     fig.update_layout(yaxis_title="Productividad Diaria [%] - Maquina 3")
 #     st.write(fig)
 #   row3_col1, row3_col2, row3_col3 = st.columns(3)
 #   with row3_col1:
 #     d_ini = pd.to_datetime(hoy).date()
 #     d_fin = pd.to_datetime(hoy).date()
 #     fig = line_graphic_main(df_orig,"maq4",d_ini,d_fin)
 #     fig.update_layout(yaxis_title="Productividad Diaria [%] - Maquina 4")
 #     st.write(fig)
 #   with row3_col2:
 #     d_ini = pd.to_datetime(hoy).date()
 #     d_fin = pd.to_datetime(hoy).date()
 #     fig = line_graphic_main(df_orig,"maq5",d_ini,d_fin) 
 #     fig.update_layout(yaxis_title="Productividad Diaria [%] - Maquina 5")
 #     st.write(fig)
 #   with row3_col3:
 #     d_ini = pd.to_datetime(hoy).date()
 #     d_fin = pd.to_datetime(hoy).date()
 #     fig = line_graphic_main(df_orig,"maq6",d_ini,d_fin)
 #     fig.update_layout(yaxis_title="Productividad Diaria [%] - Maquina 6")
 #     st.write(fig)
    
 # with Maq1:
 #   Maquina = "maq1" 

 #   row0_col1, row0_spacer2, row0_col2 = st.columns((6, 0.1, 2))
 #   with row0_col1:
 #     d_ini = pd.to_datetime(hoy).date()
 #     d_fin = pd.to_datetime(hoy).date()
 #     fig, last_ratio_daily = line_graphic_maq(df_orig,Maquina,d_ini,d_fin)
 #     fig.update_layout(xaxis_title="Date", yaxis_title="Productividad Diaria [%]",width=1400,height=350)
 #     st.write(fig)
 #     row1_col1, row1_col2 = st.columns((3, 3))
 #     with row1_col1:
 #       d_ini = pd.to_datetime(inicio_semana_laboral).date()
 #       d_fin = pd.to_datetime(fin_semana_laboral).date()
 #       fig, last_ratio_weekly = line_graphic_maq(df_orig,Maquina,d_ini,d_fin)
 #       fig.update_layout(yaxis_title="Productividad Semanal [%]")
 #       st.write(fig)
 #     with row1_col2:
 #       d_ini = pd.to_datetime(inicio_mes).date()
 #       d_fin = pd.to_datetime(fin_mes).date()
 #       fig, last_ratio_monthly = line_graphic_maq(df_orig,Maquina,d_ini,d_fin)
 #       fig.update_layout(yaxis_title="Productividad Mensual [%]")
 #       st.write(fig)
 #   with row0_col2:
 #     fig1 = go.Figure(go.Indicator(mode = "gauge+number+delta",value = last_ratio_daily, domain = {'x': [0, 1], 'y': [0, 1]}, delta = {'reference': 40}, title = {'text': "Diaria"}, gauge = {'axis': {'range': [0, 100]}}))
 #     fig1.update_layout(width=500,height=200,margin=dict(l=20, r=20, b=20, t=50))
      
 #     fig2 = go.Figure(go.Indicator(mode = "gauge+number+delta",value = last_ratio_weekly,domain = {'x': [0, 1], 'y': [0, 1]},delta = {'reference': 45},title = {'text': "Semanal"}, gauge = {'axis': {'range': [0, 100]}}))
 #     fig2.update_layout(width=500,height=200,margin=dict(l=20, r=20, b=20, t=50))
      
 #     fig3 = go.Figure(go.Indicator(mode = "gauge+number+delta",value = last_ratio_monthly,domain = {'x': [0, 1], 'y': [0, 1]},delta = {'reference': 35},title = {'text': "Mensual"}, gauge = {'axis': {'range': [0, 100]}}))
 #     fig3.update_layout(width=500,height=200,margin=dict(l=20, r=20, b=20, t=50))
      
 #     st.write(fig1,fig2,fig3)

st.dataframe(main())   
