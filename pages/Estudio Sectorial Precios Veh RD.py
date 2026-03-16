# ----------------------------------------------------------------------------------------
#------------------------------------ Importar Librerias ---------------------------------
# ----------------------------------------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.figure_factory as ff
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
# ----------------------------------------------------------------------------------------
# -------------------------------- Configuraciones Globales ------------------------------
# ----------------------------------------------------------------------------------------
#layout
st.set_page_config(page_title="Estudio Sectorial Vehículos RD", layout="wide", initial_sidebar_state="expanded")

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_FILE = BASE_DIR / "Datos.xlsx"
MAP_DIR_CANDIDATES = [BASE_DIR / "Mapas", PROJECT_DIR / "Mapas"]
REQUIRED_DATA_COLUMNS = {"Marca", "Modelo", "Version", "Anio", "Precio USD", "PROV", "Provincia"}


def resolver_ruta_mapa():
    for ruta in MAP_DIR_CANDIDATES:
        if ruta.exists():
            return ruta
    raise FileNotFoundError(
        f"No se encontro la carpeta de mapas. Rutas revisadas: {[str(r) for r in MAP_DIR_CANDIDATES]}"
    )


@st.cache_data
def datos_vehicular():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"No se encontro el archivo de datos en: {DATA_FILE}")

    datos = pd.read_excel(DATA_FILE, dtype={"PROV": str})
    columnas_faltantes = REQUIRED_DATA_COLUMNS.difference(set(datos.columns))
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas en la base: {sorted(columnas_faltantes)}")

    datos["PROV"] = datos["PROV"].astype(str).str.zfill(2)
    datos["Precio USD"] = pd.to_numeric(datos["Precio USD"], errors="coerce")
    datos["Anio"] = pd.to_numeric(datos["Anio"], errors="coerce")
    return datos

@st.cache_data
def datos_mapa():
    ruta_mapa = resolver_ruta_mapa()
    data = gpd.read_file(ruta_mapa)
    if "PROV" not in data.columns or "geometry" not in data.columns:
        raise ValueError("El mapa no contiene las columnas requeridas: 'PROV' y 'geometry'.")

    data["PROV"] = data["PROV"].astype(str).str.zfill(2)

    if data.crs is None:
        data = data.set_crs(epsg=4326)
    elif data.crs.to_epsg() != 4326:
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


try:
    df_datos = datos_vehicular()
    datosGeo = datos_mapa()
except Exception as exc:
    st.error(f"No fue posible cargar los datos del estudio: {exc}")
    st.stop()

if df_datos.empty:
    st.warning("La base de datos esta vacia. Revisa el archivo Datos.xlsx.")
    st.stop()

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

st.dataframe(formato_tabla(df1, ['Cantidad']), width="stretch")


# ----------------------------------------------------------------------------------------
# ------------------------------- FILTROS DINÁMICOS SIDEBAR ------------------------------
# ----------------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros de Exploracion Global")

# Filtro Marca (Con opción "Todas")
marcas_disponibles = ["Todas"] + sorted([str(m) for m in df_datos['Marca'].dropna().unique()])
marca_seleccionada = st.sidebar.selectbox("Selecciona una Marca:", marcas_disponibles)

if marca_seleccionada != "Todas":
    df_filtrado = df_datos[df_datos['Marca'].astype(str) == marca_seleccionada].copy()
else:
    df_filtrado = df_datos.copy()

# Filtro Modelo (Opcional - con "Todos")
modelos_disponibles = ["Todos"] + sorted([str(x) for x in df_filtrado['Modelo'].dropna().unique()])
modelo_seleccionado = st.sidebar.selectbox("Selecciona un Modelo:", modelos_disponibles)
if modelo_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Modelo'].astype(str) == modelo_seleccionado]

# Filtro Versión (Opcional - con "Todas")
versiones_disponibles = ["Todas"] + sorted([str(x) for x in df_filtrado['Version'].dropna().unique()])
version_seleccionada = st.sidebar.selectbox("Selecciona una Versión:", versiones_disponibles)
if version_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Version'].astype(str) == version_seleccionada]

# Filtro Año (Opcional - con "Todos")
anios_unicos = pd.to_numeric(df_filtrado["Anio"], errors="coerce").dropna().unique()
anios_disponibles = ["Todos"] + sorted([str(int(x)) for x in anios_unicos], reverse=True)
anio_seleccionado = st.sidebar.selectbox("Selecciona un Año:", anios_disponibles)
if anio_seleccionado != "Todos":
    df_filtrado = df_filtrado[pd.to_numeric(df_filtrado["Anio"], errors="coerce") == int(anio_seleccionado)]

# String descriptivo de filtros aplicados
filtro_str = f"Marca: {marca_seleccionada} | Modelo: {modelo_seleccionado} | Versión: {version_seleccionada} | Año: {anio_seleccionado}"


# Variables globales para recopilar los insights para el resumen
resumen_oferta_precio = ""
resumen_geo = ""
top_rural = pd.DataFrame()
top_metro = pd.DataFrame()

# ----------------------------------------------------------------------------------------
# ------------------------------- GRÁFICOS Y TABLAS (CON df_filtrado) --------------------
# ----------------------------------------------------------------------------------------

st.markdown("---")
st.markdown("### Datos descriptivos generales")
st.caption(f"Exploración estadística afectada por los filtros actuales. ({filtro_str})")

if df_filtrado.empty:
    st.warning("No hay datos disponibles para la combinacion de filtros seleccionada. Por favor, amplia tu busqueda.")
else:
    df_filtrado = df_filtrado.dropna(subset=['Precio USD']).copy()
    if df_filtrado.empty:
        st.warning("No hay precios validos para la combinacion de filtros seleccionada.")
        st.stop()

    # Crear columna combinada de Modelo y Año para el Eje X
    df_filtrado['Modelo_Anio'] = df_filtrado['Modelo'].astype(str) + ' - ' + df_filtrado['Anio'].astype(str)

    col1, col2 = st.columns(2)

    with col1:
        col1.markdown(f"**Cantidad de vehículos por modelo y año**")
        df_cantidad_modelo = df_filtrado['Modelo_Anio'].value_counts().reset_index()
        df_cantidad_modelo.columns = ['Modelo_Anio', 'Cantidad']
        df_cantidad_modelo.sort_values(by='Cantidad', ascending=False, inplace=True)
        # Tomamos el top 30 para evitar que el gráfico colapse si seleccionan "Todas"
        col1.bar_chart(df_cantidad_modelo.head(30), x='Modelo_Anio', y='Cantidad', width="stretch")

    with col2:
        col2.markdown(f"**Precio promedio por modelo y año (USD)**")
        df_promedio_precio_modelo = df_filtrado.groupby('Modelo_Anio', dropna=False)['Precio USD'].mean().reset_index()
        df_promedio_precio_modelo.columns = ['Modelo_Anio', 'Precio Promedio USD']
        # Tomamos el top 30 para mantener consistencia visual
        col2.bar_chart(df_promedio_precio_modelo.head(30), x='Modelo_Anio', y='Precio Promedio USD', width="stretch")

    # Estadísticos
    temp_stats_modelo = df_filtrado.groupby(['Marca', 'Modelo', 'Version', 'Anio'])['Precio USD'].agg(['count', 'mean', 'median', 'min', 'max', 'std']).reset_index()
    temp_stats_modelo.columns = ['Marca', 'Modelo', 'Versión', 'Año', 'Cantidad Veh', 'Precio Promedio', 'Precio Mediana', 'Precio Mínimo', 'Precio Máximo', 'Desviación Estándar']

    st.markdown("---")
    st.markdown("**Resumen estadístico por selección (en USD):**")
    st.dataframe(
        formato_tabla(temp_stats_modelo, [
            'Cantidad Veh', 'Precio Promedio', 'Precio Mediana', 'Precio Mínimo', 'Precio Máximo', 'Desviación Estándar'
        ]),
        width="stretch",
        hide_index=True
    )

    # Top 10 Dispersión
    temp_disp = df_filtrado.groupby(['Marca', 'Modelo', 'Version', 'Anio'])['Precio USD'].std().reset_index()
    temp_disp.columns = ['Marca', 'Modelo', 'Versión', 'Año', 'Desviación Estándar (US$)']
    temp_disp = temp_disp.dropna(subset=['Desviación Estándar (US$)'])
    temp_disp.sort_values(by='Desviación Estándar (US$)', ascending=False, inplace=True)

    if not temp_disp.empty:
        st.markdown("### Top combinaciones con mayor dispersion de precios")
        st.info("**Insight:** Las siguientes combinaciones presentan la mayor variacion en sus precios dentro de los filtros seleccionados, lo que indica un rango mas amplio de opciones o diferencias significativas por la condicion del vehiculo.")
        
        st.dataframe(
            formato_tabla(temp_disp.head(10), ['Desviación Estándar (US$)']),
            width="stretch",
            hide_index=True
        )

    st.markdown("---")
    st.markdown("### Distribución de precios")

    col1, col2 = st.columns(2)

    with col1:
        col1.markdown(f"**Histograma de precios**")
        fig_hist = px.histogram(df_filtrado, x="Precio USD", nbins=50, color_discrete_sequence=['#1f77b4'])
        fig_hist.update_layout(xaxis_title="Precio (USD)", yaxis_title="Cantidad de ofertas")
        col1.plotly_chart(fig_hist, width="stretch")

    with col2:
        col2.markdown(f"**Curva de densidad de precios KDE**")
        precios_filtrados = df_filtrado['Precio USD'].dropna().tolist()
        
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
                col2.plotly_chart(fig, width="stretch")
            except Exception as e:
                col2.info("No fue posible generar la curva de densidad para esta seleccion de datos debido a limitaciones estadisticas.")
        else:
            col2.warning("**Variabilidad Insuficiente:** Los precios en esta seleccion son identicos o no hay suficientes observaciones para trazar la curva de densidad.")

    # Scatter plot Cantidad vs Promedio Precios
    temp_scatter_plot = df_filtrado.groupby(['Marca', 'Modelo', 'Version', 'Anio'])['Precio USD'].agg(['mean', 'count']).reset_index()
    temp_scatter_plot.columns = ['Marca', 'Modelo', 'Version', 'Anio', 'Precio Promedio', 'Cantidad']
    temp_scatter_plot['Key'] = temp_scatter_plot['Marca'] + ' | ' + temp_scatter_plot['Modelo'] + ' | ' + temp_scatter_plot['Version'].astype(str) + ' | ' + temp_scatter_plot['Anio'].astype(str)
    temp_scatter_valido = temp_scatter_plot.dropna(subset=['Precio Promedio', 'Cantidad']).copy()

    st.markdown("**Cantidad de vehículos disponibles (X) vs precio promedio USD (Y)**")
    st.scatter_chart(
        temp_scatter_valido,
        x='Cantidad',
        y='Precio Promedio',
        width="stretch",
        color="Key"
    )

    # Insight local: Cálculo de la pendiente (oferta vs precio) agrupado
    if len(temp_scatter_valido) > 1 and temp_scatter_valido['Cantidad'].nunique() > 1:
        z = np.polyfit(temp_scatter_valido['Cantidad'], temp_scatter_valido['Precio Promedio'], 1)
        pendiente = z[0]
        
        if pendiente > 50: 
            resumen_oferta_precio = "La cantidad de ofertas no presiona el precio a la baja; al contrario, combinaciones con mayor volumen tienden a mostrar precios más altos. Esto indica una **demanda latente muy fuerte** que absorbe la oferta y eleva el mercado, o que los modelos más costosos son los de mayor rotación."
            st.success(f"**Insight de Mercado:** Para los vehiculos bajo los filtros actuales ({filtro_str}), {resumen_oferta_precio}")
        elif pendiente < -50: 
            resumen_oferta_precio = "Una mayor cantidad de ofertas publicadas presiona el precio promedio a la baja. Este es el **comportamiento natural de competencia** donde la abundancia de oferta obliga a los vendedores a ajustar sus precios."
            st.info(f"**Insight de Mercado:** Para los vehiculos bajo los filtros actuales ({filtro_str}), {resumen_oferta_precio}")
        else: 
            resumen_oferta_precio = "La oferta publicada no muestra una correlación fuerte con el precio promedio. Esto sugiere que **el volumen no es el factor que dicta el precio**, sino variables intrínsecas (estado, uso, equipamiento)."
            st.info(f"**Insight de Mercado:** Para los vehiculos bajo los filtros actuales ({filtro_str}), {resumen_oferta_precio}")
    else:
        resumen_oferta_precio = "No hay suficientes agrupaciones en esta selección para determinar una tendencia matemática clara entre cantidad y precio."
        st.write("**Insight de Mercado:**", resumen_oferta_precio)


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
    m = None
    if not mapa_geo.empty:
        center = mapa_geo.dissolve().representative_point().iloc[0]
        m = folium.Map(location=[center.y, center.x], zoom_start=7, tiles="cartodbpositron")
        folium.GeoJson(
            mapa_geo,
            name="Provincias",
            tooltip=folium.GeoJsonTooltip(fields=['PROV'], aliases=["Nombre:"]),
            style_function=style_function
        ).add_to(m)

    col1, col2 = st.columns(2)
    with col1:
        if m is not None:
            st_folium(m, width=700, height=500, returned_objects=[])
        else:
            st.warning("No hay datos geográficos disponibles para visualizar el mapa.")

    with col2:
        datos_stat_prov_display = df_filtrado[['Provincia', 'Precio USD']].groupby('Provincia').agg(['mean', 'count']).reset_index()
        datos_stat_prov_display.columns = ['Provincia', 'Precio US$ Promedio', 'Cantidad Veh en venta']
        st.dataframe(
            formato_tabla(datos_stat_prov_display, ['Precio US$ Promedio', 'Cantidad Veh en venta']),
            width="stretch",
            hide_index=True
        )

    # Insight y Cálculo Geográfico (Basado en el cruce de Marca/Modelo/Versión/Año para evitar sesgos)
    df_geo_conclusiones = df_filtrado.copy()
    df_geo_conclusiones['Zona'] = np.where(df_geo_conclusiones['Provincia'].isin(['Distrito Nacional', 'Santo Domingo']), 'Metropolitana', 'Rural')
    
    # Tabla resumen por zona
    st.markdown("**Comparación agregada entre zona Metropolitana y Rural**")
    datos_stat_zona = df_geo_conclusiones.groupby('Zona').agg(
        Precio_Promedio=('Precio USD', 'mean'),
        Cantidad=('Precio USD', 'count')
    ).reset_index()
    datos_stat_zona.columns = ['Zona', 'Precio US$ Promedio', 'Cantidad Veh en venta']
    st.dataframe(
        formato_tabla(datos_stat_zona, ['Precio US$ Promedio', 'Cantidad Veh en venta']),
        width="stretch",
        hide_index=True
    )

    # Cálculo preciso controlando por vehículo (Marca, Modelo, Versión, Año)
    geo_agg = df_geo_conclusiones.groupby(['Marca', 'Modelo', 'Version', 'Anio', 'Zona'])['Precio USD'].mean().reset_index()
    geo_pivot = geo_agg.pivot_table(index=['Marca', 'Modelo', 'Version', 'Anio'], columns='Zona', values='Precio USD').reset_index()
    
    if 'Metropolitana' in geo_pivot.columns and 'Rural' in geo_pivot.columns:
        promedio_metro_real = geo_pivot['Metropolitana'].mean()
        promedio_rural_real = geo_pivot['Rural'].mean()
        
        if pd.notna(promedio_metro_real) and pd.notna(promedio_rural_real) and promedio_rural_real > 0:
            variacion = ((promedio_metro_real - promedio_rural_real) / promedio_rural_real) * 100
            if variacion > 0:
                resumen_geo = f"Comparando estrictamente vehículos equivalentes (misma marca, modelo, versión y año), la zona **Metropolitana** es en promedio un **{variacion:.1f}% más cara** que la zona Rural."
                st.success(f"**Insight Geografico:** {resumen_geo}")
            elif variacion < 0:
                resumen_geo = f"Comparando estrictamente vehículos equivalentes, sorprendentemente la zona **Rural** es en promedio un **{abs(variacion):.1f}% más cara** que la zona Metropolitana."
                st.info(f"**Insight Geografico:** {resumen_geo}")
            else:
                resumen_geo = "No se observan diferencias significativas de precio entre las zonas Metropolitana y Rural para vehículos equivalentes."
                st.write(f"**Insight Geografico:** {resumen_geo}")
        else:
            resumen_geo = "No existen suficientes coincidencias de vehículos exactos en ambas zonas para trazar una media comparativa."
            st.write(f"**Insight Geografico:** {resumen_geo}")
    else:
        resumen_geo = "No existen ofertas en ambas zonas (Metropolitana y Rural) para realizar la comparativa bajo los filtros actuales."
        st.write(f"**Insight Geografico:** {resumen_geo}")

    # Top mejores ofertas Rurales / Metropolitanas (En la sección de Geografía)
    st.markdown("---")
    st.markdown("### Oportunidades por distribucion geografica")
    
    if 'Metropolitana' in geo_pivot.columns and 'Rural' in geo_pivot.columns:
        col_r, col_m = st.columns(2)

        # Oportunidades Rurales
        top_rural = geo_pivot[geo_pivot['Rural'] > 0].copy()
        top_rural['Indicador'] = (top_rural['Metropolitana'] - top_rural['Rural']) / top_rural['Rural']
        top_rural = top_rural.replace([np.inf, -np.inf], np.nan).dropna(subset=['Indicador'])
        top_rural.sort_values(by='Indicador', ascending=False, inplace=True)
        top_rural = top_rural[(top_rural['Indicador'] > 0) & (top_rural['Indicador'] <= 0.3)]

        with col_r:
            st.success("**Mejores ofertas en zona Rural (vs. Metropolis)**")
            if not top_rural.empty:
                st.dataframe(
                    formato_tabla(top_rural.head(10)[['Marca', 'Modelo', 'Version', 'Anio', 'Rural', 'Metropolitana']].rename(columns={'Version':'Versión', 'Anio':'Año'}), ['Rural', 'Metropolitana']),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.write("No se encontraron oportunidades destacables.")

        # Oportunidades Metropolitanas
        top_metro = geo_pivot[geo_pivot['Metropolitana'] > 0].copy()
        top_metro['Indicador'] = (top_metro['Rural'] - top_metro['Metropolitana']) / top_metro['Metropolitana']
        top_metro = top_metro.replace([np.inf, -np.inf], np.nan).dropna(subset=['Indicador'])
        top_metro.sort_values(by='Indicador', ascending=False, inplace=True)
        top_metro = top_metro[(top_metro['Indicador'] > 0) & (top_metro['Indicador'] <= 0.3)]

        with col_m:
            st.info("**Mejores ofertas en zona Metropolitana (vs. Rural)**")
            if not top_metro.empty:
                st.dataframe(
                    formato_tabla(top_metro.head(10)[['Marca', 'Modelo', 'Version', 'Anio', 'Metropolitana', 'Rural']].rename(columns={'Version':'Versión', 'Anio':'Año'}), ['Metropolitana', 'Rural']),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.write("No se encontraron oportunidades destacables.")
    else:
        st.warning("No hay datos suficientes para buscar oportunidades cruzadas entre zonas en la seleccion actual.")


# ----------------------------------------------------------------------------------------
# ------------------------------- CONCLUSIONES RESUMEN -----------------------------------
# ----------------------------------------------------------------------------------------
st.markdown("---")
st.markdown("<div id='conclusiones-resumen'></div>", unsafe_allow_html=True)
st.markdown("## Conclusiones Resumen")

if not df_filtrado.empty:
    st.markdown(f"**Filtros de exploración aplicados:** `{filtro_str}`")
    
    # 1. Métricas Globales
    cantidad_total = df_filtrado.shape[0]
    precio_promedio_total = df_filtrado['Precio USD'].mean()
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric(label="Cantidad de Vehículos Analizados", value=f"{cantidad_total:,.0f} unidades")
    with col_c2:
        st.metric(label="Precio Promedio General", value=f"US$ {precio_promedio_total:,.2f}")

    st.markdown("### Insights Clave:")
    
    # 2. Variabilidad General
    std_global = df_filtrado['Precio USD'].std()
    cv_global = std_global / precio_promedio_total if precio_promedio_total > 0 else 0
    if cv_global > 0.6:
        var_comment = "Existe una **alta variabilidad** en los precios. Los montos fluctúan significativamente respecto al promedio general, indicando un mercado muy diverso en cuanto a condiciones de los vehículos, equipamiento, kilometraje o la mezcla de distintos sub-modelos."
    elif cv_global > 0.3:
        var_comment = "Se observa una **variabilidad moderada**. Hay diferencias razonables de precio justificadas por el estado general del vehículo y año de fabricación dentro de la muestra seleccionada."
    else:
        var_comment = "La muestra presenta **baja variabilidad**. Los precios tienden a estar concentrados muy cerca del promedio, sugiriendo un mercado altamente estandarizado para los filtros aplicados."
    
    st.markdown(f"- **Variabilidad General de los Precios:** {var_comment}")

    # 3 & 4. Dinámica de Oferta y Comparativa Geográfica (Imprimimos los generados arriba)
    st.markdown(f"- **Dinámica de Oferta y Precio:** {resumen_oferta_precio}")
    st.markdown(f"- **Comparativa Geográfica:** {resumen_geo}")

    # 5. Top Oportunidades (Re-impresión para el resumen)
    st.markdown("### Top Oportunidades Geograficas Resumidas")
    if 'Metropolitana' in geo_pivot.columns and 'Rural' in geo_pivot.columns:
        col_r_res, col_m_res = st.columns(2)
        with col_r_res:
            st.success("**Top Rural**")
            if not top_rural.empty:
                st.dataframe(
                    formato_tabla(top_rural.head(5)[['Marca', 'Modelo', 'Versión' if 'Versión' in top_rural.columns else 'Version', 'Año' if 'Año' in top_rural.columns else 'Anio', 'Rural', 'Metropolitana']], ['Rural', 'Metropolitana']),
                    width="stretch", hide_index=True
                )
            else:
                st.write("-")
        with col_m_res:
            st.info("**Top Metropolitano**")
            if not top_metro.empty:
                st.dataframe(
                    formato_tabla(top_metro.head(5)[['Marca', 'Modelo', 'Versión' if 'Versión' in top_metro.columns else 'Version', 'Año' if 'Año' in top_metro.columns else 'Anio', 'Metropolitana', 'Rural']], ['Metropolitana', 'Rural']),
                    width="stretch", hide_index=True
                )
            else:
                st.write("-")
    else:
        st.write("No hay datos para mostrar el top de oportunidades en el resumen.")
else:
    st.info("No hay datos suficientes para generar conclusiones sobre esta selección.")


#--------------------------------------------- Modelo estadístico -------------------------------------------------------------
st.markdown("---")
st.markdown("<div id='modelo-estadistico-de-validacion-de-precio'></div>", unsafe_allow_html=True)
st.markdown("## Modelo estadistico de validacion de precio")
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

marcas_modelo_est = sorted([str(m) for m in df_datos['Marca'].dropna().unique()])
if not marcas_modelo_est:
    st.warning("No hay marcas disponibles para ejecutar el modelo estadistico.")
    st.stop()

with col1:
    # Este modelo evalúa la base completa independientemente de los filtros globales de arriba
    marca_est = st.selectbox("Marca", marcas_modelo_est, key='marca_estadistico')
base_marca_est = df_datos[df_datos['Marca'].astype(str) == marca_est].copy()

modelos_modelo_est = sorted([str(x) for x in base_marca_est['Modelo'].dropna().unique()])
if not modelos_modelo_est:
    st.warning("No hay modelos disponibles para la marca seleccionada.")
    st.stop()

with col2:
    modelo_est = st.selectbox("Modelo", modelos_modelo_est, key='modelo_estadistico')
base_modelo_est = base_marca_est[base_marca_est['Modelo'].astype(str) == modelo_est].copy()

versiones_modelo_est = sorted([str(x) for x in base_modelo_est['Version'].dropna().unique()])
if not versiones_modelo_est:
    st.warning("No hay versiones disponibles para la combinacion seleccionada.")
    st.stop()

with col3:
    version_est = st.selectbox("Versión", versiones_modelo_est, key='version_estadistico')
base_version_est = base_modelo_est[base_modelo_est['Version'].astype(str) == version_est].copy()

anios_modelo_est = sorted([int(x) for x in pd.to_numeric(base_version_est['Anio'], errors='coerce').dropna().unique()])
if not anios_modelo_est:
    st.warning("No hay anos disponibles para la version seleccionada.")
    st.stop()

with col4:
    anio_est = st.selectbox(
        "Año",
        anios_modelo_est,
        key='anio_estadistico'
    )

with col5:
    precio_consulta = st.number_input("Precio a evaluar (US$)", min_value=0.0, step=1000.0, value=20000.0)

historico_precio = df_datos[
    (df_datos['Marca'].astype(str) == marca_est)
    & (df_datos['Modelo'].astype(str) == modelo_est)
    & (df_datos['Version'].astype(str) == version_est)
    & (pd.to_numeric(df_datos['Anio'], errors='coerce') == int(anio_est))
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
        width="stretch",
        hide_index=True
    )

    st.info(f"**Conclusion:** {comentario_percentil(percentile_precio)}")

    if percentile_precio >= 90:
        mejores_ofertas = historico_precio[historico_precio['Precio USD'] < precio_consulta].copy()
        mejores_ofertas = mejores_ofertas.sort_values(by='Precio USD', ascending=True)
        cantidad_mejores = mejores_ofertas.shape[0]

        st.warning(f"**Alerta de Precio:** Existen {cantidad_mejores} ofertas vehiculares publicadas con mejores precios para las mismas especificaciones.")

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
                width="stretch",
                hide_index=True
            )
        else:
            st.write("No fue posible listar ofertas con mejor precio para esta combinación.")
    else:
        st.success("El precio evaluado es competitivo (no cae en el rango percentil 90 o superior). No se listan ofertas comparativas mas baratas obligatorias.")
