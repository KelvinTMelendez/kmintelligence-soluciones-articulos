# ----------------------------------------------------------------------------------------
#------------------------------------ Importar Librerias ---------------------------------
# ----------------------------------------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd,os
from sqlalchemy import create_engine
import plotly.express as px
import plotly.figure_factory as ff
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
from dotenv import load_dotenv

load_dotenv()
# ----------------------------------------------------------------------------------------
# -------------------------------- Configuraciones Globales ------------------------------
# ----------------------------------------------------------------------------------------
#layout
st.set_page_config(page_title="Estudio Sectorial Vehículos RD", layout="wide")

#conextion db
usuario_db = os.getenv("USUARIO_DB")
password_db = os.getenv("PASSWORD_DB")
host_db = os.getenv("HOST_DB")
puerto_db = os.getenv("PUERTO_DB")
database_db = os.getenv("DATABASE_DB")

@st.cache_resource
def get_engine():
  return create_engine(f"postgresql+psycopg2://{usuario_db}:{password_db}@{host_db}:{puerto_db}/{database_db}")

@st.cache_resource
def datos_vehicular():
  engine = get_engine()
  with engine.connect() as conn:
    x = pd.read_sql_query("select * from articulos_academicos.webscrapping_precio_vehiculos_rd", conn)
    x['precio'] = x['precio'].apply(lambda x: x.replace(' ',''))
    x['precio'] = x['precio'].str.strip()
    x['precio'] = x['precio'].astype(float)
    x['precio'] = np.where(x['moneda'] == 'RD$',x['precio'],x['precio'] * 62)
    return x

@st.cache_resource
def datos_mapa():
  data = gpd.read_file(r"Mapas")
  if data.crs != "EPSG:4326":
    data = data.to_crs(epsg=4326)

  return data


def formato_tabla(df, columnas_numericas):
  formato_numero = "{:,.0f}"
  return df.style.format({col: formato_numero for col in columnas_numericas})


def comentario_percentil(percentil):
  if percentil >= 90:
    return "Precio alto respecto al histórico para este vehículo."
  elif percentil >= 75:
    return "Precio ligeramente por encima del comportamiento histórico."
  elif percentil >= 25:
    return "Precio alineado con el comportamiento histórico."
  else:
    return "Precio atractivo respecto al histórico observado."


engine = get_engine()
df_datos = datos_vehicular()
datosGeo = datos_mapa()
formato_numero = "{:,.0f}"

# ----------------------------------------------------------------------------------------
# ------------------------------- Construcción del Artículo ------------------------------
# ----------------------------------------------------------------------------------------

st.sidebar.title("Índice del artículo")
st.sidebar.markdown(
    """
  - [Resumen Ejecutivo](#resumen-ejecutivo)
  - [Introducción](#introduccion)
  - [Objetivos Generales](#objetivos-generales)
  - [Objetivos Específicos](#objetivos-especificos)
  - [Alcance](#alcance)
  - [Metodología de Investigación](#metodologia-de-investigacion)
  - [Fuentes de Información](#fuentes-de-informacion)
  - [Investigación](#investigacion)
  - [Modelo Estadístico de Validación de Precio](#modelo-estadistico-de-validacion-de-precio)
  """
)

st.title("Estudio Sectorial de los Precios de los Vehículos en República Dominicana")
st.caption("Análisis descriptivo del mercado vehicular dominicano a partir de datos obtenidos mediante web scraping.")

st.markdown("""
<div id='resumen-ejecutivo'></div>

### Resumen Ejecutivo
Este artículo presenta una lectura descriptiva del mercado de vehículos en República Dominicana, con énfasis en tres dimensiones: 
la oferta disponible por marca/modelo, el comportamiento de precios y la distribución geográfica de las publicaciones. 
El objetivo es convertir datos del mercado en una referencia útil para comparar ofertas y detectar precios fuera de rango.
""", unsafe_allow_html=True)

st.markdown("""
<div id='introduccion'></div>

## Introducción
En República Dominicana, el parque vehicular ha mostrado un crecimiento sostenido durante los últimos años. 
Entre 2020 y 2025 se observa un incremento aproximado de 36.1%, pasando de 4.84 a 6.5 millones de vehículos. 
Este crecimiento contempla múltiples categorías, incluyendo motocicletas, jeepetas, automóviles, camiones y autobuses. 
Dentro del total, alrededor del 27.58% corresponde a vehículos tipo jeepeta y automóvil.
""", unsafe_allow_html=True)

datos_vehicular = pd.DataFrame({
    "Año": [2020, 2021, 2022, 2023,2024,2025],
    "Vehículos": [4842,5152,5464,5810,6194,6641]
})
st.bar_chart(
  data = datos_vehicular
  ,x = "Año"
  , y = "Vehículos"
  ,width  = 800
)

st.markdown(
  """
El aumento del parque vehicular sugiere una demanda cada vez más dinámica. Entre los factores que podrían influir en este comportamiento se encuentran:
- Factores macroeconómicos del país
- Condiciones del sistema de transporte público
- Mayor capacidad adquisitiva en segmentos de la población

Aunque profundizar en estas causas está fuera del alcance de este artículo, sí es razonable asumir que una mayor demanda tiende a presionar los precios del mercado.

En ese contexto, surgen preguntas prácticas para compradores, analistas y actores del sector:
- ¿Dónde pueden encontrarse mejores precios de vehículos?
- ¿Cómo comparar el mismo vehículo entre distintas ubicaciones?
- ¿Qué marcas tienen mayor presencia en la oferta actual?

---
<div id='objetivos-generales'></div>

## Objetivos Generales
- Analizar descriptivamente cómo varía el precio de los vehículos en República Dominicana según provincia de venta, marca y modelo
- Brindar recomendaciones de compra de vehículos en RD
- Disponibilizar una herramienta interactiva para identificar mejores ofertas en el mercado

---
<div id='objetivos-especificos'></div>

## Objetivos Específicos
- Disponibilizar los siguientes reportes:
    - Top 5 mejores provincias para comprar un vehículo
    - Indicadores promedio de precios y cantidad de ofertas por provincia
    - Oferta disponible por marca
    - Precio sugerido por marca/modelo/año con fines comparativos sobre datos del mercado

---
<div id='alcance'></div>

## Alcance
Este estudio contempla las siguientes marcas:

Audi, BMW, Bestune, BYD, Cadillac, Changan, Chevrolet, Chery, Citroen, Dodge, Force, Ford, Forthing, GAC, Geely, Honda, Hyundai, Infiniti, Isuzu, Jac, Jeep, Jetour, Joylong, Kaiyi, Karry, KGM, Kia, KYC, Leapmotors, Lexus, Maxus, Mazda, Mercedes-Benz, MG, Mitsubishi, Mitsubishi Motors, Nissan, Peugeot, Porsche, Ram, Renault, Subaru, Suzuki, Toyota, Volkswagen, Volvo, JMC y ZXAUTO.

- Año: a partir de 1999

---
<div id='metodologia-de-investigacion'></div>

## Metodología de Investigación
El tipo de estudio implementado en esta investigación es **descriptivo**. 
La intención es entender cómo se comporta la oferta visible del mercado vehicular en República Dominicana, sin inferir causalidad.

---
<div id='fuentes-de-informacion'></div>

## Fuentes de Información
Los datos fueron obtenidos mediante técnica de web scraping sobre publicaciones de la plataforma [SuperCarros.com](https://www.supercarros.com/).

---
  """,
  unsafe_allow_html=True
)

#######################################################
# ---------------------- DATOS ------------------------

df1 = df_datos['marca'].value_counts().reset_index()
df1.columns = ['Marca','Cantidad']

###################### FIN DATOS ########################

st.markdown(
  """
  <div id='investigacion'></div>

  ## Investigación
  ### Panorama global del mercado vehicular en RD
  Comencemos observando la oferta actual de vehículos publicada en el estudio. 
  En el siguiente panel se resume la cantidad de vehículos disponibles por marca.
  """,
  unsafe_allow_html=True
)

st.dataframe(formato_tabla(df1,['Cantidad']), use_container_width=True)
st.markdown("**Marcas con mayor presencia en la oferta analizada:**")
for index,valor in df1.head(5).iterrows():
  st.markdown("- " + valor['Marca'])

#Display Graficos de Modelos por Marca
st.markdown("---")
st.markdown("### Datos descriptivos por marca y modelo")
st.caption("Exploración estadística por marca, año y modelo.")

marca_seleccionada = st.sidebar.selectbox("Selecciona una Marca:",[x for x in sorted(df_datos['marca'].dropna().unique())],width = 300)
temp_marca = df_datos[df_datos['marca'] == marca_seleccionada].copy()

anio_seleccionado = st.sidebar.selectbox("Selecciona un Año:",[x for x in sorted(temp_marca['anio'].dropna().unique())],width = 300)
if anio_seleccionado:
  temp_marca = temp_marca[temp_marca['anio'] == anio_seleccionado].copy()

col1, col2 = st.columns(2)

with col1:
  col1.markdown(f"**Cantidad de vehículos por modelo | Marca: {marca_seleccionada}**")
  df_cantidad_modelo = temp_marca['modelo'].value_counts().reset_index()
  df_cantidad_modelo.columns = ['Modelo','Cantidad']
  df_cantidad_modelo.sort_values(by = 'Cantidad',ascending = False,inplace = True)
  col1.bar_chart(df_cantidad_modelo,x = 'Modelo',y = 'Cantidad',use_container_width=True)

with col2:
  col2.markdown(f"**Precio promedio por modelo | Marca: {marca_seleccionada}**")
  df_promedio_precio_modelo = temp_marca.groupby('modelo', dropna=False)['precio'].mean().reset_index()
  df_promedio_precio_modelo.columns = ['Modelo','Precio Promedio RD$']
  col2.bar_chart(df_promedio_precio_modelo,x = 'Modelo',y = 'Precio Promedio RD$',use_container_width=True)

#Estadísticos por Modelo y Marca
temp_stats_modelo = temp_marca[['modelo','precio']].groupby('modelo').agg(['count','mean','median','min','max','std']).reset_index()
temp_stats_modelo.columns = ['Modelo','Cantidad Veh','Precio Promedio','Precio Mediana','Precio Mínimo','Precio Máximo','Desviación Estándar']

st.markdown("---")
st.markdown("**Resumen estadístico por modelo:**")
st.dataframe(
  formato_tabla(temp_stats_modelo,[
    'Cantidad Veh','Precio Promedio','Precio Mediana','Precio Mínimo','Precio Máximo','Desviación Estándar'
  ]),
  use_container_width=True
)

temp = df_datos[['modelo','precio','anio','marca']].groupby(['marca','modelo','anio']).std(numeric_only=True).reset_index()
temp.columns = ['Marca','Modelo','Anio','Desviación Estándar']
temp.sort_values(by = 'Desviación Estándar',ascending = False,inplace = True)
st.markdown("**Top 10 combinaciones marca-modelo-año con mayor dispersión de precios:**")
for index,valor in temp.head(10).iterrows():
  st.markdown("- " + valor['Marca'] + ' - ' + valor['Modelo'] + ' - ' + str(valor['Anio']) + ' - **RD$' + f"{valor['Desviación Estándar']:,.2f}" + "**")

st.markdown("---")
st.markdown("### Datos descriptivos por modelo")
modelo_seleccionado = st.sidebar.selectbox("Selecciona un Modelo:",[x for x in sorted(temp_marca['modelo'].dropna().unique())],width = 300)
temp_modelo = temp_marca[temp_marca['modelo'] == modelo_seleccionado].copy()

col1, col2 = st.columns(2)

with col1:
  col1.markdown(f"**Histograma de precios | {marca_seleccionada} - {modelo_seleccionado} - {anio_seleccionado}**")
  fig_hist = px.histogram(temp_modelo, x="precio", nbins=50, color_discrete_sequence=['#1f77b4'])
  fig_hist.update_layout(xaxis_title="Precio", yaxis_title="Cantidad de ofertas")
  col1.plotly_chart(fig_hist, use_container_width=True)

with col2:
  col2.markdown(f"**Curva de densidad de precios | {marca_seleccionada} - {modelo_seleccionado} - {anio_seleccionado}**")
  precios_filtrados = temp_modelo['precio'].dropna().tolist()
  if len(precios_filtrados) > 1:
    fig = ff.create_distplot(
        [precios_filtrados], 
        group_labels=['Precios'], 
        show_hist=False, 
        show_rug=False,
        colors=['#1f77b4']
    )
    fig.update_layout(
        title_x=0.5,
        yaxis_title="Densidad",
        xaxis_title="Precio del Vehículo"
    )
    col2.plotly_chart(fig, use_container_width=True)
  else:
    col2.info("No hay suficientes observaciones para construir la densidad KDE.")

#Scatter plot Cantidad vs Promedio Precios por anio
temp_scatter_plot = df_datos[['marca','modelo','anio','precio']].groupby(['marca','modelo','anio']).agg(['mean','count']).reset_index()
temp_scatter_plot.columns = ['Marca','Modelo','Anio','Precio Promedio','Cantidad']
temp_scatter_plot['Key'] = temp_scatter_plot['Marca'] + ' | ' + temp_scatter_plot['Modelo'] + ' | ' + temp_scatter_plot['Anio'].astype(str)

st.markdown("**Cantidad de vehículos disponibles (X) vs precio promedio (Y)**")
st.scatter_chart(
  temp_scatter_plot
  ,x = 'Cantidad'
  ,y = 'Precio Promedio'
  ,use_container_width=True
  ,color = "Key"
)

st.info("A nivel descriptivo, el gráfico no evidencia una relación lineal fuerte entre precio promedio y cantidad de ofertas disponibles.")

#--------------------------------------------- Geografia -------------------------------------------------------------
st.markdown("---")
st.markdown("### Comportamiento de precios por geografía en RD")
datos_stat_provinicia = temp_modelo[['PROV','precio']].groupby('PROV').agg(['mean','count']).reset_index()
datos_stat_provinicia.columns = ['PROV','Promedio','Cantidad']

colormap = cm.LinearColormap(
  colors=['#fee0d2', '#67000d'],
  vmin=datos_stat_provinicia.Promedio.min(),
  vmax=datos_stat_provinicia.Promedio.max()
)

def style_function(feature):
  valor = feature['properties']['Promedio']
  return {
    'fillColor': colormap(valor) if valor is not None and not pd.isna(valor) else '#808080',
    'color': 'black',
    'weight': 1,
    'fillOpacity': 0.7
  }

mapa_geo = datosGeo[['PROV','geometry']].copy()
mapa_geo = mapa_geo.merge(datos_stat_provinicia,on = 'PROV',how = 'left')
center = mapa_geo.geometry.centroid.iloc[0]
m = folium.Map(location=[center.y, center.x], zoom_start=7, tiles="cartodbpositron")
folium.GeoJson(
  mapa_geo,
  name="Provincias",
  tooltip=folium.GeoJsonTooltip(fields=['PROV'], aliases=["Nombre:"]),
  style_function=style_function
).add_to(m)

col1, col2 = st.columns(2)
with col1:
  st_folium(m, width=700, height=500)

with col2:
  datos_stat_provinicia = temp_modelo[['provincia','precio']].groupby('provincia').agg(['mean','count']).reset_index()
  datos_stat_provinicia.columns = ['provincia','Precio RD$ Promedio','Cantidad Veh en venta']
  st.dataframe(
    formato_tabla(datos_stat_provinicia,['Precio RD$ Promedio','Cantidad Veh en venta']),
    use_container_width=True
  )

  datos_stat_provinicia = temp_modelo[['provincia','precio']].copy()
  datos_stat_provinicia['provincia'] = np.where(
    datos_stat_provinicia['provincia'].isin(['Distrito Nacional','Santo Domingo'])
    ,'Metropolitana'
    ,'Rural'
  )
  datos_stat_provinicia = datos_stat_provinicia.groupby('provincia').agg(['mean','count']).reset_index()
  datos_stat_provinicia.columns = ['zona','Precio RD$ Promedio','Cantidad Veh en venta']
  st.markdown("**Comparación agregada entre zona Metropolitana y Rural**")
  st.dataframe(
    formato_tabla(datos_stat_provinicia,['Precio RD$ Promedio','Cantidad Veh en venta']),
    use_container_width=True
  )
  st.caption("En la selección actual, la zona Metropolitana tiende a mostrar precios promedio más elevados.")

datos_stat_provinicia = temp_marca[['marca','modelo','anio','provincia','precio']].groupby(['marca','modelo','anio','provincia']).agg(['mean']).reset_index()
datos_stat_provinicia.columns = ['Marca','Modelo','Anio','Provincia','Precio Promedio']
datos_stat_provinicia['Provincia'] = np.where(
  datos_stat_provinicia['Provincia'].isin(['Distrito Nacional','Santo Domingo'])
  ,'Metropolitana'
  ,'Rural'
)
datos_stat_provinicia = datos_stat_provinicia.pivot_table(index = ['Marca','Modelo','Anio'],columns = 'Provincia',values = 'Precio Promedio').reset_index()
st.markdown("**Comparativo de precio promedio entre zona Metropolitana y Rural**")
st.dataframe(
  formato_tabla(datos_stat_provinicia,['Metropolitana','Rural']),
  use_container_width=True
)

#Top mejores ofertas Rurales
datos_stat_provinicia = df_datos[['marca','modelo','anio','provincia','precio']].groupby(['marca','modelo','anio','provincia']).agg(['mean']).reset_index()
datos_stat_provinicia.columns = ['Marca','Modelo','Anio','Provincia','Precio Promedio']
datos_stat_provinicia['Provincia'] = np.where(
  datos_stat_provinicia['Provincia'].isin(['Distrito Nacional','Santo Domingo'])
  ,'Metropolitana'
  ,'Rural'
)
datos_stat_provinicia = datos_stat_provinicia.pivot_table(index = ['Marca','Modelo','Anio'],columns = 'Provincia',values = 'Precio Promedio').reset_index()
datos_stat_provinicia['Indicador'] = (datos_stat_provinicia['Metropolitana'] - datos_stat_provinicia['Rural']) / datos_stat_provinicia['Rural']
datos_stat_provinicia.sort_values(by = 'Indicador',ascending = False,inplace = True)
datos_stat_provinicia = datos_stat_provinicia[
  (datos_stat_provinicia['Indicador'] > 0)
  & (datos_stat_provinicia['Indicador'] <= 0.3)
]

st.markdown("**Mejores oportunidades estimadas en provincias rurales**")
for index,valor in datos_stat_provinicia.head(10).iterrows():
  st.markdown("* " + valor['Marca'] + '/' + valor['Modelo'] + '/' + str(valor['Anio']) + ':'+' Precio promedio Rural RD$' + f"{valor['Rural']:,.2f}" + " | Precio promedio Metropolitana RD$" + f"{valor['Metropolitana']:,.2f}")

#Top mejores ofertas Metropolitanas
datos_stat_provinicia = df_datos[['marca','modelo','anio','provincia','precio']].groupby(['marca','modelo','anio','provincia']).agg(['mean']).reset_index()
datos_stat_provinicia.columns = ['Marca','Modelo','Anio','Provincia','Precio Promedio']
datos_stat_provinicia['Provincia'] = np.where(
  datos_stat_provinicia['Provincia'].isin(['Distrito Nacional','Santo Domingo'])
  ,'Metropolitana'
  ,'Rural'
)
datos_stat_provinicia = datos_stat_provinicia.pivot_table(index = ['Marca','Modelo','Anio'],columns = 'Provincia',values = 'Precio Promedio').reset_index()
datos_stat_provinicia['Indicador'] = (datos_stat_provinicia['Rural'] - datos_stat_provinicia['Metropolitana']) / datos_stat_provinicia['Metropolitana']
datos_stat_provinicia.sort_values(by = 'Indicador',ascending = False,inplace = True)
datos_stat_provinicia = datos_stat_provinicia[
  (datos_stat_provinicia['Indicador'] > 0)
  & (datos_stat_provinicia['Indicador'] <= 0.3)
]

st.markdown("**Mejores oportunidades estimadas en provincias metropolitanas**")
for index,valor in datos_stat_provinicia.head(10).iterrows():
  st.markdown("* " + valor['Marca'] + '/' + valor['Modelo'] + '/' + str(valor['Anio']) + ':'+' Precio promedio Rural RD$' + f"{valor['Rural']:,.2f}" + " | Precio promedio Metropolitana RD$" + f"{valor['Metropolitana']:,.2f}")

#--------------------------------------------- Modelo estadistico -------------------------------------------------------------
st.markdown("---")
st.markdown("<div id='modelo-estadistico-de-validacion-de-precio'></div>", unsafe_allow_html=True)
st.markdown("## Modelo estadístico de validación de precio")
st.markdown(
  """
Este módulo permite recibir un precio puntual para una combinación de **marca, modelo y año**, 
y compararlo contra el histórico observado en la base. El objetivo no es predecir el precio, 
sino ubicar la oferta dentro de su distribución histórica usando dos métricas simples:

- **Percentile**: posición relativa del precio dentro del histórico
- **Desviación estándar (z-score)**: distancia del precio respecto al promedio del grupo

Mientras mayor sea el percentile, más alto luce el precio frente a las ofertas comparables.
  """
)

col1, col2, col3, col4 = st.columns(4)
with col1:
  marca_modelo = st.selectbox("Marca para validar precio", [x for x in sorted(df_datos['marca'].dropna().unique())], key='marca_modelo_estadistico')

base_marca = df_datos[df_datos['marca'] == marca_modelo].copy()
with col2:
  modelo_modelo = st.selectbox("Modelo para validar precio", [x for x in sorted(base_marca['modelo'].dropna().unique())], key='modelo_estadistico')

base_modelo = base_marca[base_marca['modelo'] == modelo_modelo].copy()
with col3:
  anio_modelo = st.selectbox("Año para validar precio", [int(x) for x in sorted(base_modelo['anio'].dropna().unique())], key='anio_estadistico')

with col4:
  precio_consulta = st.number_input("Precio a evaluar (RD$)", min_value = 0.0, step = 10000.0, value = 1000000.0)

historico_precio = df_datos[
  (df_datos['marca'] == marca_modelo)
  & (df_datos['modelo'] == modelo_modelo)
  & (df_datos['anio'] == anio_modelo)
].copy()

cantidad_historico = historico_precio.shape[0]

if cantidad_historico == 0:
  st.warning("No hay histórico disponible para esa combinación de marca, modelo y año.")
else:
  media_precio = historico_precio['precio'].mean()
  mediana_precio = historico_precio['precio'].median()
  std_precio = historico_precio['precio'].std()
  min_precio = historico_precio['precio'].min()
  max_precio = historico_precio['precio'].max()
  percentile_precio = (historico_precio['precio'] <= precio_consulta).mean() * 100

  if pd.isna(std_precio) or std_precio == 0:
    z_score = 0
  else:
    z_score = (precio_consulta - media_precio) / std_precio

  resumen_modelo = pd.DataFrame({
    'Indicador': [
      'Cantidad de ofertas históricas',
      'Precio promedio histórico',
      'Precio mediana histórica',
      'Precio mínimo histórico',
      'Precio máximo histórico',
      'Percentile del precio evaluado',
      'Desviación estándar histórica',
      'Z-Score del precio evaluado'
    ],
    'Valor': [
      cantidad_historico,
      media_precio,
      mediana_precio,
      min_precio,
      max_precio,
      percentile_precio,
      std_precio if not pd.isna(std_precio) else 0,
      z_score
    ]
  })

  st.dataframe(
    resumen_modelo.style.format({
      'Valor': lambda x: f"{x:,.2f}" if isinstance(x, (int, float, np.floating)) else x
    }),
    use_container_width=True
  )

  st.info(comentario_percentil(percentile_precio))

  if percentile_precio >= 90:
    mejores_ofertas = historico_precio[historico_precio['precio'] < precio_consulta].copy()
    mejores_ofertas = mejores_ofertas.sort_values(by='precio', ascending=True)
    cantidad_mejores = mejores_ofertas.shape[0]

    st.warning(f"Existen {cantidad_mejores} ofertas vehiculares con mejores precios.")

    columnas_mostrar = [col for col in ['marca','modelo','anio','precio','provincia'] if col in mejores_ofertas.columns]
    if len(columnas_mostrar) > 0 and cantidad_mejores > 0:
      mejores_ofertas = mejores_ofertas[columnas_mostrar].copy()
      mejores_ofertas.rename(columns={
        'marca':'Marca',
        'modelo':'Modelo',
        'anio':'Anio',
        'precio':'Precio RD$',
        'provincia':'Provincia'
      }, inplace=True)
      st.dataframe(
        formato_tabla(mejores_ofertas,['Precio RD$']),
        use_container_width=True
      )
    else:
      st.write("No fue posible listar ofertas con mejor precio para esta combinación.")
  else:
    st.success("El precio evaluado no cae en el rango percentil 90 o superior, por lo que no se listan ofertas comparativas más baratas.")
