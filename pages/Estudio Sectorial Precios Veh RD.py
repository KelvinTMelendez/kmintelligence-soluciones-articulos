# ----------------------------------------------------------------------------------------
#------------------------------------ Importar Librerias ---------------------------------
# ----------------------------------------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd, os
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
st.set_page_config(page_title="Estudio Sectorial Vehículos RD", layout="wide", initial_sidebar_state="expanded")

@st.cache_resource
def datos_vehicular():
    datos = pd.read_excel("pages/Datos.xlsx", dtype={'PROV': str})
    return datos

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
  - [Conclusiones Resumen](#conclusiones-resumen)
  - [Modelo Estadístico de Validación de Precio](#modelo-estadistico-de-validacion-de-precio)
  """
)

st.title("Estudio Sectorial de los Precios de los Vehículos en República Dominicana")
st.caption("Análisis descriptivo del mercado vehicular dominicano a partir de datos obtenidos mediante web scraping.")

st.markdown("""
<div id='resumen-ejecutivo'></div>

### Resumen Ejecutivo
Este artículo presenta una lectura descriptiva del mercado de vehículos en República Dominicana, con énfasis en tres dimensiones: 
la oferta disponible por marca/modelo/versión, el comportamiento de precios y la distribución geográfica de las publicaciones. 
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

datos_vehicular_chart = pd.DataFrame({
    "Año": [2020, 2021, 2022, 2023, 2024, 2025],
    "Vehículos": [4842, 5152, 5464, 5810, 6194, 6641]
})
st.bar_chart(
    data=datos_vehicular_chart,
    x="Año",
    y="Vehículos",
    width=800
)

# Generar string de marcas dinámico para el alcance
marcas_unicas = sorted([str(m) for m in df_datos['Marca'].dropna().unique()])
marcas_str = ", ".join(marcas_unicas)

st.markdown(
    f"""
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
- Analizar descriptivamente cómo varía el precio de los vehículos en República Dominicana según provincia de venta, marca, modelo y versión.
- Brindar recomendaciones de compra de vehículos en RD.
- Disponibilizar una herramienta interactiva para identificar mejores ofertas en el mercado.

---
<div id='objetivos-especificos'></div>

## Objetivos Específicos
- Disponibilizar los siguientes reportes:
    - Top mejores provincias para comprar un vehículo.
    - Indicadores promedio de precios y cantidad de ofertas por provincia.
    - Oferta disponible por marca.
    - Precio sugerido por marca/modelo/versión/año con fines comparativos sobre datos del mercado.

---
<div id='alcance'></div>

## Alcance
Este estudio contempla las siguientes marcas:

{marcas_str}

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

df1 = df_datos['Marca'].value_counts().reset_index()
df1.columns = ['Marca', 'Cantidad']

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

st.dataframe(formato_tabla(df1, ['Cantidad']), use_container_width=True)


# ----------------------------------------------------------------------------------------
# ------------------------------- FILTROS DINÁMICOS SIDEBAR ------------------------------
# ----------------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros de Exploración Global")

# Filtro Marca (Requerido)
marca_seleccionada = st.sidebar.selectbox("Selecciona una Marca:", sorted(df_datos['Marca'].dropna().unique()))
df_filtrado = df_datos[df_datos['Marca'] == marca_seleccionada].copy()

# Filtro Modelo (Opcional - con "Todos")
modelos_disponibles = ["Todos"] + sorted([str(x) for x in df_filtrado['Modelo'].dropna().unique()])
modelo_seleccionado = st.sidebar.selectbox("Selecciona un Modelo:", modelos_disponibles)
if modelo_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Modelo'] == modelo_seleccionado]

# Filtro Versión (Opcional - con "Todas")
versiones_disponibles = ["Todas"] + sorted([str(x) for x in df_filtrado['Version'].dropna().unique()])
version_seleccionada = st.sidebar.selectbox("Selecciona una Versión:", versiones_disponibles)
if version_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Version'] == version_seleccionada]

# Filtro Año (Opcional - con "Todos")
anios_disponibles = ["Todos"] + sorted([str(int(x)) for x in df_filtrado['Anio'].dropna().unique()], reverse=True)
anio_seleccionado = st.sidebar.selectbox("Selecciona un Año:", anios_disponibles)
if anio_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Anio'] == int(anio_seleccionado)]

# String descriptivo de filtros aplicados
filtro_str = f"Marca: {marca_seleccionada} | Modelo: {modelo_seleccionado} | Versión: {version_seleccionada} | Año: {anio_seleccionado}"


# Variables globales para recopilar los insights para el resumen
resumen_oferta_precio = ""
resumen_geo = ""

# ----------------------------------------------------------------------------------------
# ------------------------------- GRÁFICOS Y TABLAS (CON df_filtrado) --------------------
# ----------------------------------------------------------------------------------------

st.markdown("---")
st.markdown("### Datos descriptivos generales")
st.caption(f"Exploración estadística afectada por los filtros actuales. ({filtro_str})")

if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para la combinación de filtros seleccionada. Por favor, amplía tu búsqueda.")
else:
    # Crear columna combinada de Modelo y Año para el Eje X
    df_filtrado['Modelo_Anio'] = df_filtrado['Modelo'].astype(str) + ' - ' + df_filtrado['Anio'].astype(str)

    col1, col2 = st.columns(2)

    with col1:
        col1.markdown(f"**Cantidad de vehículos por modelo y año**")
        df_cantidad_modelo = df_filtrado['Modelo_Anio'].value_counts().reset_index()
        df_cantidad_modelo.columns = ['Modelo_Anio', 'Cantidad']
        df_cantidad_modelo.sort_values(by='Cantidad', ascending=False, inplace=True)
        col1.bar_chart(df_cantidad_modelo, x='Modelo_Anio', y='Cantidad', use_container_width=True)

    with col2:
        col2.markdown(f"**Precio promedio por modelo y año (USD)**")
        df_promedio_precio_modelo = df_filtrado.groupby('Modelo_Anio', dropna=False)['Precio USD'].mean().reset_index()
        df_promedio_precio_modelo.columns = ['Modelo_Anio', 'Precio Promedio USD']
        col2.bar_chart(df_promedio_precio_modelo, x='Modelo_Anio', y='Precio Promedio USD', use_container_width=True)

    # Estadísticos
    temp_stats_modelo = df_filtrado.groupby(['Marca', 'Modelo', 'Version', 'Anio'])['Precio USD'].agg(['count', 'mean', 'median', 'min', 'max', 'std']).reset_index()
    temp_stats_modelo.columns = ['Marca', 'Modelo', 'Versión', 'Año', 'Cantidad Veh', 'Precio Promedio', 'Precio Mediana', 'Precio Mínimo', 'Precio Máximo', 'Desviación Estándar']

    st.markdown("---")
    st.markdown("**Resumen estadístico por selección (en USD):**")
    st.dataframe(
        formato_tabla(temp_stats_modelo, [
            'Cantidad Veh', 'Precio Promedio', 'Precio Mediana', 'Precio Mínimo', 'Precio Máximo', 'Desviación Estándar'
        ]),
        use_container_width=True,
        hide_index=True
    )

    # Top 10 Dispersión - FORMATO PROFESIONAL
    temp_disp = df_filtrado.groupby(['Marca', 'Modelo', 'Version', 'Anio'])['Precio USD'].std().reset_index()
    temp_disp.columns = ['Marca', 'Modelo', 'Versión', 'Año', 'Desviación Estándar (US$)']
    temp_disp = temp_disp.dropna(subset=['Desviación Estándar (US$)'])
    temp_disp.sort_values(by='Desviación Estándar (US$)', ascending=False, inplace=True)

    if not temp_disp.empty:
        st.markdown("### 🏆 Top combinaciones con mayor dispersión de precios")
        st.info("💡 **Insight:** Las siguientes combinaciones presentan la mayor variación en sus precios dentro de los filtros seleccionados, lo que indica un rango más amplio de opciones o diferencias significativas por la condición del vehículo.")
        
        st.dataframe(
            formato_tabla(temp_disp.head(10), ['Desviación Estándar (US$)']),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.markdown("### Distribución de precios")

    col1, col2 = st.columns(2)

    with col1:
        col1.markdown(f"**Histograma de precios**")
        fig_hist = px.histogram(df_filtrado, x="Precio USD", nbins=50, color_discrete_sequence=['#1f77b4'])
        fig_hist.update_layout(xaxis_title="Precio (USD)", yaxis_title="Cantidad de ofertas")
        col1.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        col2.markdown(f"**Curva de densidad de precios KDE**")
        precios_filtrados = df_filtrado['Precio USD'].dropna().tolist()
        
        # MANEJO DE ERROR LINALGERROR (MATRIZ SINGULAR KDE)
        # Verificamos que haya al menos 2 valores únicos para que exista variabilidad
        if len(precios_filtrados) > 1 and len(set(precios_filtrados)) > 1:
            try:
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
                    xaxis_title="Precio del Vehículo (USD)"
                )
                col2.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                col2.info("⚠️ No fue posible generar la curva de densidad para esta selección de datos debido a limitaciones estadísticas.")
        else:
            col2.warning("⚠️ **Variabilidad Insuficiente:** Los precios en esta selección son idénticos o no hay suficientes observaciones para trazar la curva de densidad.")

    # Scatter plot Cantidad vs Promedio Precios
    temp_scatter_plot = df_filtrado.groupby(['Marca', 'Modelo', 'Version', 'Anio'])['Precio USD'].agg(['mean', 'count']).reset_index()
    temp_scatter_plot.columns = ['Marca', 'Modelo', 'Version', 'Anio', 'Precio Promedio', 'Cantidad']
    temp_scatter_plot['Key'] = temp_scatter_plot['Marca'] + ' | ' + temp_scatter_plot['Modelo'] + ' | ' + temp_scatter_plot['Version'].astype(str) + ' | ' + temp_scatter_plot['Anio'].astype(str)

    st.markdown("**Cantidad de vehículos disponibles (X) vs precio promedio USD (Y)**")
    st.scatter_chart(
        temp_scatter_plot,
        x='Cantidad',
        y='Precio Promedio',
        use_container_width=True,
        color="Key"
    )

    # Cálculo de la pendiente (oferta vs precio)
    if len(temp_scatter_plot) > 1:
        z = np.polyfit(temp_scatter_plot['Cantidad'], temp_scatter_plot['Precio Promedio'], 1)
        pendiente = z[0]
        
        # Lógica de interpretación de la pendiente
        if pendiente > 50: # Tendencia al alza apreciable
            resumen_oferta_precio = "La cantidad de ofertas no presiona el precio a la baja; al contrario, a mayor cantidad de ofertas observamos precios más altos. Esto da a entender que **hay una demanda latente muy fuerte** (que no estamos midiendo) que absorbe la oferta y empuja los precios hacia arriba, o bien, los modelos de mayor precio son los que tienen mayor rotación en el mercado."
            st.success(f"📈 **Insight de Mercado:** Para los vehículos bajo los filtros actuales ({filtro_str}), {resumen_oferta_precio}")
        elif pendiente < -50: # Tendencia a la baja apreciable
            resumen_oferta_precio = "Una mayor cantidad de ofertas publicadas presiona el precio a la baja. Este es el **comportamiento esperado cuando abunda la oferta** y los vendedores deben competir por precio."
            st.info(f"📉 **Insight de Mercado:** Para los vehículos bajo los filtros actuales ({filtro_str}), {resumen_oferta_precio}")
        else: # Pendiente casi plana
            resumen_oferta_precio = "La oferta publicada no muestra una correlación fuerte con el precio promedio. Esto sugiere que **la cantidad de vehículos no influye fuertemente en su precio**, sino que otros factores (como el estado del vehículo, kilometraje o equipamiento) podrían estar dictando el precio final."
            st.info(f"⚖️ **Insight de Mercado:** Para los vehículos bajo los filtros actuales ({filtro_str}), {resumen_oferta_precio}")
    else:
        resumen_oferta_precio = "No hay suficientes puntos de datos en esta selección para determinar una tendencia clara entre cantidad y precio."
        st.write("💡 **Insight de Mercado:**", resumen_oferta_precio)


    #--------------------------------------------- Geografía -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Comportamiento de precios por geografía en RD")
    datos_stat_provincia_raw = df_filtrado[['PROV', 'Precio USD']].groupby('PROV').agg(['mean', 'count']).reset_index()
    datos_stat_provincia_raw.columns = ['PROV', 'Promedio', 'Cantidad']

    colormap = cm.LinearColormap(
        colors=['#fee0d2', '#67000d'],
        vmin=datos_stat_provincia_raw.Promedio.min() if not datos_stat_provincia_raw.empty else 0,
        vmax=datos_stat_provincia_raw.Promedio.max() if not datos_stat_provincia_raw.empty else 1
    )

    def style_function(feature):
        valor = feature['properties']['Promedio']
        return {
            'fillColor': colormap(valor) if valor is not None and not pd.isna(valor) else '#808080',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    mapa_geo = datosGeo[['PROV', 'geometry']].copy()
    mapa_geo = mapa_geo.merge(datos_stat_provincia_raw, on='PROV', how='left')
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
        st_folium(m, width=700, height=500, returned_objects=[])

    with col2:
        datos_stat_prov_display = df_filtrado[['Provincia', 'Precio USD']].groupby('Provincia').agg(['mean', 'count']).reset_index()
        datos_stat_prov_display.columns = ['Provincia', 'Precio US$ Promedio', 'Cantidad Veh en venta']
        st.dataframe(
            formato_tabla(datos_stat_prov_display, ['Precio US$ Promedio', 'Cantidad Veh en venta']),
            use_container_width=True,
            hide_index=True
        )

        datos_stat_zona = df_filtrado[['Provincia', 'Precio USD']].copy()
        datos_stat_zona['Provincia'] = np.where(
            datos_stat_zona['Provincia'].isin(['Distrito Nacional', 'Santo Domingo']),
            'Metropolitana',
            'Rural'
        )
        datos_stat_zona = datos_stat_zona.groupby('Provincia').agg(['mean', 'count']).reset_index()
        datos_stat_zona.columns = ['Zona', 'Precio US$ Promedio', 'Cantidad Veh en venta']
        
        st.markdown("**Comparación agregada entre zona Metropolitana y Rural**")
        st.dataframe(
            formato_tabla(datos_stat_zona, ['Precio US$ Promedio', 'Cantidad Veh en venta']),
            use_container_width=True,
            hide_index=True
        )
        
        # Insight de Porcentaje de Incremento Geográfico
        zonas_dict = datos_stat_zona.set_index('Zona').to_dict('index')
        if 'Metropolitana' in zonas_dict and 'Rural' in zonas_dict:
            precio_metro = zonas_dict['Metropolitana']['Precio US$ Promedio']
            cant_metro = zonas_dict['Metropolitana']['Cantidad Veh en venta']
            precio_rural = zonas_dict['Rural']['Precio US$ Promedio']
            cant_rural = zonas_dict['Rural']['Cantidad Veh en venta']
            
            if precio_rural > 0:
                variacion = ((precio_metro - precio_rural) / precio_rural) * 100
                if variacion > 0:
                    resumen_geo = f"La zona **Metropolitana** (con una muestra de {cant_metro:,.0f} vehículos) presenta un precio promedio un **{variacion:.1f}% más alto** que la zona **Rural** (que tiene {cant_rural:,.0f} vehículos en venta)."
                    st.success(f"📍 **Insight Geográfico:** {resumen_geo}")
                else:
                    resumen_geo = f"Sorprendentemente, la zona **Rural** (con una muestra de {cant_rural:,.0f} vehículos) presenta un precio promedio un **{abs(variacion):.1f}% más alto** que la zona **Metropolitana** (con {cant_metro:,.0f} vehículos en venta)."
                    st.info(f"📍 **Insight Geográfico:** {resumen_geo}")
        else:
            resumen_geo = "No hay datos suficientes en ambas zonas (Metropolitana y Rural) para calcular una variación de precios."

    # Top mejores ofertas Rurales / Metropolitanas (FORMATO PROFESIONAL)
    st.markdown("---")
    st.markdown("### 🗺️ Oportunidades por distribución geográfica")
    
    datos_stat_provincia_agg = df_filtrado.groupby(['Marca', 'Modelo', 'Version', 'Anio', 'Provincia'])['Precio USD'].mean().reset_index()
    datos_stat_provincia_agg.columns = ['Marca', 'Modelo', 'Versión', 'Año', 'Provincia', 'Precio Promedio']
    datos_stat_provincia_agg['Provincia'] = np.where(
        datos_stat_provincia_agg['Provincia'].isin(['Distrito Nacional', 'Santo Domingo']),
        'Metropolitana',
        'Rural'
    )
    datos_stat_provincia_pivot = datos_stat_provincia_agg.pivot_table(index=['Marca', 'Modelo', 'Versión', 'Año'], columns='Provincia', values='Precio Promedio').reset_index()

    if 'Metropolitana' in datos_stat_provincia_pivot.columns and 'Rural' in datos_stat_provincia_pivot.columns:
        
        col_r, col_m = st.columns(2)

        # Oportunidades Rurales
        top_rural = datos_stat_provincia_pivot.copy()
        top_rural['Indicador'] = (top_rural['Metropolitana'] - top_rural['Rural']) / top_rural['Rural']
        top_rural.sort_values(by='Indicador', ascending=False, inplace=True)
        top_rural = top_rural[(top_rural['Indicador'] > 0) & (top_rural['Indicador'] <= 0.3)]

        with col_r:
            st.success("🌾 **Mejores oportunidades en provincias Rurales**")
            st.caption("Vehículos cuyo precio es más económico en zonas rurales (hasta un 30% más baratos vs. la metrópolis).")
            if not top_rural.empty:
                st.dataframe(
                    formato_tabla(top_rural.head(10)[['Marca', 'Modelo', 'Versión', 'Año', 'Rural', 'Metropolitana']], ['Rural', 'Metropolitana']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.write("No se encontraron oportunidades destacables bajo estos filtros.")

        # Oportunidades Metropolitanas
        top_metro = datos_stat_provincia_pivot.copy()
        top_metro['Indicador'] = (top_metro['Rural'] - top_metro['Metropolitana']) / top_metro['Metropolitana']
        top_metro.sort_values(by='Indicador', ascending=False, inplace=True)
        top_metro = top_metro[(top_metro['Indicador'] > 0) & (top_metro['Indicador'] <= 0.3)]

        with col_m:
            st.info("🏙️ **Mejores oportunidades en provincias Metropolitanas**")
            st.caption("Vehículos cuyo precio es más económico en la ciudad (hasta un 30% más baratos vs. el interior).")
            if not top_metro.empty:
                st.dataframe(
                    formato_tabla(top_metro.head(10)[['Marca', 'Modelo', 'Versión', 'Año', 'Metropolitana', 'Rural']], ['Metropolitana', 'Rural']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.write("No se encontraron oportunidades destacables bajo estos filtros.")
    else:
        st.warning("⚠️ No hay suficientes datos para comparar Zona Metropolitana vs. Zona Rural con los filtros actuales.")


# ----------------------------------------------------------------------------------------
# ------------------------------- CONCLUSIONES RESUMEN -----------------------------------
# ----------------------------------------------------------------------------------------
st.markdown("---")
st.markdown("<div id='conclusiones-resumen'></div>", unsafe_allow_html=True)
st.markdown("## 📝 Conclusiones Resumen")

if not df_filtrado.empty:
    st.markdown(f"**Filtros de exploración aplicados:** `{filtro_str}`")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric(label="Volumen Total Analizado", value=f"{df_filtrado.shape[0]:,.0f} Vehículos")
    with col_c2:
        st.metric(label="Precio Promedio Global (USD)", value=f"US$ {df_filtrado['Precio USD'].mean():,.2f}")
    
    st.markdown("### Principales Hallazgos:")
    st.markdown(f"- **Dinámica de Oferta y Precio:** {resumen_oferta_precio}")
    st.markdown(f"- **Diferencia Geográfica:** {resumen_geo if resumen_geo else 'No hubo muestra suficiente en ambas zonas para determinar una diferencia de precios.'}")
else:
    st.info("No hay datos suficientes para generar conclusiones sobre esta selección.")


#--------------------------------------------- Modelo estadístico -------------------------------------------------------------
st.markdown("---")
st.markdown("<div id='modelo-estadistico-de-validacion-de-precio'></div>", unsafe_allow_html=True)
st.markdown("## 📊 Modelo estadístico de validación de precio")
st.markdown(
    """
Este módulo permite recibir un precio puntual para una combinación de **marca, modelo, versión y año**, 
y compararlo contra el histórico observado en la base entera. El objetivo no es predecir el precio, 
sino ubicar la oferta dentro de su distribución histórica usando dos métricas simples:

- **Percentil**: posición relativa del precio dentro del histórico.
- **Desviación estándar (z-score)**: distancia del precio respecto al promedio del grupo.

*Mientras mayor sea el percentil, más alto luce el precio frente a las ofertas comparables.*
    """
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    marca_est = st.selectbox("Marca", sorted(df_datos['Marca'].dropna().unique()), key='marca_estadistico')
base_marca_est = df_datos[df_datos['Marca'] == marca_est].copy()

with col2:
    modelo_est = st.selectbox("Modelo", sorted(base_marca_est['Modelo'].dropna().unique()), key='modelo_estadistico')
base_modelo_est = base_marca_est[base_marca_est['Modelo'] == modelo_est].copy()

with col3:
    version_est = st.selectbox("Versión", sorted([str(x) for x in base_modelo_est['Version'].dropna().unique()]), key='version_estadistico')
base_version_est = base_modelo_est[base_modelo_est['Version'] == version_est].copy()

with col4:
    anio_est = st.selectbox("Año", sorted(base_version_est['Anio'].dropna().unique()), key='anio_estadistico')

with col5:
    precio_consulta = st.number_input("Precio a evaluar (US$)", min_value=0.0, step=1000.0, value=20000.0)

historico_precio = df_datos[
    (df_datos['Marca'] == marca_est)
    & (df_datos['Modelo'] == modelo_est)
    & (df_datos['Version'].astype(str) == version_est)
    & (df_datos['Anio'] == anio_est)
].copy()

cantidad_historico = historico_precio.shape[0]

if cantidad_historico == 0:
    st.warning("No hay histórico disponible para esa combinación de marca, modelo, versión y año.")
else:
    media_precio = historico_precio['Precio USD'].mean()
    mediana_precio = historico_precio['Precio USD'].median()
    std_precio = historico_precio['Precio USD'].std()
    min_precio = historico_precio['Precio USD'].min()
    max_precio = historico_precio['Precio USD'].max()
    percentile_precio = (historico_precio['Precio USD'] <= precio_consulta).mean() * 100

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
            'Percentil del precio evaluado',
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
        use_container_width=True,
        hide_index=True
    )

    st.info(f"📌 **Conclusión:** {comentario_percentil(percentile_precio)}")

    if percentile_precio >= 90:
        mejores_ofertas = historico_precio[historico_precio['Precio USD'] < precio_consulta].copy()
        mejores_ofertas = mejores_ofertas.sort_values(by='Precio USD', ascending=True)
        cantidad_mejores = mejores_ofertas.shape[0]

        st.warning(f"🚨 **Alerta de Precio:** Existen {cantidad_mejores} ofertas vehiculares publicadas con mejores precios para las mismas especificaciones.")

        columnas_mostrar = [col for col in ['Marca', 'Modelo', 'Version', 'Anio', 'Precio USD', 'Provincia'] if col in mejores_ofertas.columns]
        if len(columnas_mostrar) > 0 and cantidad_mejores > 0:
            mejores_ofertas = mejores_ofertas[columnas_mostrar].copy()
            mejores_ofertas.rename(columns={
                'Precio USD': 'Precio US$',
                'Version': 'Versión',
                'Anio': 'Año'
            }, inplace=True)
            
            st.dataframe(
                formato_tabla(mejores_ofertas, ['Precio US$']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No fue posible listar ofertas con mejor precio para esta combinación.")
    else:
        st.success("✅ El precio evaluado es competitivo (no cae en el rango percentil 90 o superior). No se listan ofertas comparativas más baratas obligatorias.")