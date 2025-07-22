import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import numpy as np
import itertools
import gzip
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        html, body, [data-testid="stApp"] {
            height: 100vh;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            height: 100vh;
        }

        .main {
            height: 100%;
        }

        /* Opcional: elimina el espacio de header/footer */
        header, footer, #MainMenu {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """
    Carga los datos públicos

    Returns:
    -------
    - df con los datos
    """
    df = pd.read_csv("df.csv")
    df_continents = pd.read_csv("df_continents.csv")
    return df, df_continents


def two_columns_sidebar(elem1, elem2):
    with st.sidebar:
        with st.container():
            col1_sidebar, col2_sidebar = st.columns(2)

            with col1_sidebar:
                res1 = elem1()
            
            with col2_sidebar:
                res2 = elem2()

    return res1, res2

def n_columns_sidebar(n_elems, list_elems):
    """
    Crea un número especificado de columnas en la barra lateral de Streamlit y coloca elementos en ellas.

    Parameters:
    - n_elems (int): El número de columnas a crear en la barra lateral.
    - list_elems (list): Una lista de funciones que generan los elementos a colocar en cada columna. Cada función debe ser llamada sin argumentos.

    Returns:
    - list: Una lista de los resultados de las funciones en `list_elems`.
    """
    res = list()
    with st.sidebar:
        with st.container():
            col_sidebar = st.columns(n_elems)

            for index, col in enumerate(col_sidebar):
                with col:
                    res.append(list_elems[index]())


    return res

def count_flights_per_day(df):
    """
    Cuenta el número de vuelos por día a partir de un DataFrame.

    Parameters:
    - df (DataFrame): Un DataFrame de pandas que debe contener una columna llamada "day" con los días de los vuelos.

    Returns:
    - DataFrame: Un nuevo DataFrame que contiene dos columnas: "num_flights" (número de vuelos) y "day" (días).
    """
    df_count = pd.DataFrame()
    df_count["num_flights"] = df["day"].value_counts().sort_index()
    df_count["day"] = df_count.index

    return df_count

def count_flights_by_country_origin(df, df_continents):
    """
    Cuenta la cantidad total de vuelos por país de origen, 
    asociando cada código ICAO con su país correspondiente.

    Parameters
    df : pandas.DataFrame
        DataFrame que contiene datos de vuelos, con al menos una columna llamada 'origin' 
        que representa el código ICAO del aeropuerto de origen de cada vuelo.
    
    df_continents : pandas.DataFrame
        DataFrame con información sobre aeropuertos, que incluye al menos las columnas:
        - 'icao_code': código ICAO del aeropuerto
        - 'country_name': nombre del país correspondiente

    Returns
        Un DataFrame con dos columnas:
        - 'country_name': nombre del país
        - 'num_flights': número total de vuelos originados en aeropuertos de ese país
    """

    df_count = df["origin"].value_counts().reset_index()
    df_count.columns = ["origin", "num_flights"]
    df_merge = pd.merge(df_count, df_continents, left_on="origin", right_on="icao_code", how="left")
    df_sum = df_merge.groupby("country_name")["num_flights"].sum().reset_index()

    return df_sum



def filter_df_continent(df_continents, col, elem):
    """
    Filtra un DataFrame de continentes basado en un valor específico de una columna.

    Parameters:
    - df_continents (DataFrame): Un DataFrame de pandas que contiene información sobre continentes.
    - col (str): El nombre de la columna en la que se desea aplicar el filtro.
    - elem (str): El valor que se utilizará para filtrar la columna especificada.

    Returns:
    - DataFrame: Un nuevo DataFrame que contiene solo las filas donde el valor de `col` es igual a `elem`.
    """
    df_continents_filt =  df_continents[df_continents[col]==elem]
    return df_continents_filt

def filter_df(df, df_continents_filt):
    """
    Filtra un DataFrame basado en los códigos ICAO de un DataFrame de continentes filtrados.

    Parameters:
    - df (DataFrame): Un DataFrame de pandas que contiene información sobre vuelos, incluyendo columnas "origin" y "destination".
    - df_continents_filt (DataFrame): Un DataFrame de pandas que contiene una columna "icao_code" con los códigos ICAO de los continentes filtrados.

    Returns:
    - DataFrame: Un nuevo DataFrame que contiene solo las filas donde el "origin" o "destination" están en la lista de códigos ICAO del DataFrame de continentes filtrados.
    """
    df_filt = df[df["origin"].isin(df_continents_filt["icao_code"]) | df["destination"].isin(df_continents_filt["icao_code"])]
    return df_filt

def do_filter(col, elem, df_filtered, df_continents_filtered):
    """
    Aplica un filtro a un DataFrame de continentes y luego filtra otro DataFrame basado en el resultado.

    Paramters:
    - col (str): El nombre de la columna en el DataFrame de continentes que se utilizará para aplicar el filtro.
    - elem (str): El valor que se utilizará para filtrar la columna especificada en el DataFrame de continentes.
    - df_filtered (DataFrame): Un DataFrame de pandas que contiene información que se filtrará en función de los continentes.
    - df_continents_filtered (DataFrame): Un DataFrame de pandas que contiene información sobre continentes, que será filtrado.

    Returns
    - tuple: Una tupla que contiene dos elementos:
        - DataFrame: El DataFrame filtrado basado en los continentes.
        - DataFrame: El DataFrame de continentes filtrados después de aplicar el filtro.
    """
    df_continents_filtered = filter_df_continent(df_continents_filtered, col, elem)
    df_filt = filter_df(df_filtered, df_continents_filtered)
    return df_filt, df_continents_filtered
   
def filter_day(df, type_filter, day):
    """
    Filtra un DataFrame basado en el valor de la columna "day" según el tipo de filtro especificado.

    Parameters
    - df (DataFrame): Un DataFrame de pandas que contiene una columna llamada "day".
    - type_filter (str): El tipo de filtro a aplicar. Puede ser "=", "<", o ">".
    - day (str o int): El valor que se utilizará para filtrar la columna "day". El tipo debe coincidir con el tipo de datos en la columna.

    Returns
    - DataFrame: Un nuevo DataFrame que contiene solo las filas que cumplen con la condición del filtro.
    """
    if type_filter == "=":
        df = df[df["day"]==day]

    elif type_filter == "<":
        df = df[df["day"]<day]

    elif type_filter == ">":
        df = df[df["day"]>day]

    return df


def graph_df_total_line(df):
    """
    Genera un gráfico de líneas que muestra el total de vuelos por día a partir de un DataFrame.

    Parameters:
    - df (DataFrame): Un DataFrame de pandas que contiene información sobre vuelos, incluyendo una columna "day".

    Returns:
    - Figure: Un objeto de figura de Plotly que representa el gráfico de total de vuelos por día.
    """
    df_total_count = count_flights_per_day(df)
    fig = go.Figure()

    fig.add_trace(
    go.Scatter(
        x=df_total_count["day"],
        y=df_total_count["num_flights"],
        mode="lines+markers",
        hovertemplate=("day: %{x}<br> num_flights: %{y}<br>"),
        name="Total"
        )
    )
   
    return fig

def graph_add_line(df_add, fig, name):
    """
    Agrega una línea adicional a un gráfico existente que muestra el número de vuelos por día.

    Parameters:
    - df_add (DataFrame): Un DataFrame de pandas que contiene información sobre vuelos, incluyendo una columna "day" y "num_flights".
    - fig (Figure): Un objeto de figura de Plotly al que se le agregará la línea.
    - name (str): El nombre de la línea que se mostrará en la leyenda del gráfico.

    Returns:
    - None: La función modifica el objeto de figura existente en lugar de devolver uno nuevo.
    """
    fig.add_trace(
        go.Scatter(
            x=df_add["day"],
            y=df_add["num_flights"],
            mode="lines+markers",
            hovertemplate=("day: %{x}<br> num_flights: %{y}<br>"),
            name=name
        )
    )


@st.cache_data
def graph_line(df):
    """
    Crea una gráfica de líneas que muestra la evolución diaria del número de vuelos,
    desglosada por continente de origen o destino.

    Parameters
    - df : DataFrame con la información de vuelos. Debe contener una columna que identifique 
         la fecha (por ejemplo 'day') y una columna que identifique el aeropuerto de origen o destino.

    Returns
    - Gráfico de líneas interactivo con la serie temporal total de vuelos y las líneas por continente.

    Notas
    -----
    Esta función:
    - Utiliza `count_flights_per_day(df)` para contar vuelos por día.
    - Usa `graph_df_total_line(df)` para crear la figura base.
    - Filtra los datos por continente usando `do_filter("continent", ...)`.
    - Agrega las líneas individuales por continente mediante `graph_add_line(...)`.
    """

    df_count = count_flights_per_day(df)
    fig_scatter = graph_df_total_line(df)

    for continent in df_continents["continent"].unique():
        df_filtered, _ = do_filter("continent", continent, df, df_continents)
        df_count = count_flights_per_day(df_filtered)
        graph_add_line(df_count, fig_scatter, continent)

    # Una funcion adicional que me ha salido al usar un elemento "or" a la hora de filtrar, es que te muestra 
    # tanto los vuelos de ida o vuelata del contiente filtrada como los vuelos de ida/vuelta hacia ese contienente

    return fig_scatter

@st.cache_data
def mapmundi(df, df_continents):
    """
    Genera un mapa coroplético (choropleth map) que muestra el número total de vuelos 
    originados por país en el mundo.

    Parameters
    ----------
    - df : DataFrame con datos de vuelos. Debe contener una columna 'origin' con los códigos ICAO 
           de los aeropuertos de origen de cada vuelo.

    - df_continents : DataFrame con información geográfica de los aeropuertos

    Returns
    plotly.graph_objects.Figure
        Figura interactiva de Plotly que representa un mapa mundial con intensidad de color 
        proporcional al número de vuelos originados por país.

    """
    df = count_flights_by_country_origin(df, df_continents)
    fig = px.choropleth(
    df,
    locations="country_name",
    locationmode="country names",  
    color="num_flights",   
    hover_data={"num_flights": True} , 
    color_continuous_scale="Blues")

    return fig

#---------------------------------------------------------------------------------------
# Realización de calculos iniciales:
# Cargamos los df originales
df, df_continents = load_data()


# ---------------------------------------------------------------------------
# Sidebar

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 400px;
            width: 400px;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("Dataframes a mostrar en la pantalla")

# Checkboxes para saber que dataframes mostrar abajo
list_df = [ "df", "df_continents"]
checkbox = dict()
for name in list_df:
    checkbox[name] = st.sidebar.checkbox(name)


    
st.sidebar.title("Filtrado")

# Inicializamos lista de filtros si no existe
if "filtros" not in st.session_state:
    st.session_state.filtros = []



button_add_filter, button_filter, button_delete_filter = n_columns_sidebar(n_elems=3, 
    list_elems=[lambda: st.button("Añadir filtro"),
                lambda: st.button("Realizar filtro"),
                lambda: st.button("Borrar filtros")]
)

# Si el botón "Añadir filtro" fue presionado, activa el filtro
if button_add_filter:
    # Añadir un filtro vacío (puedes personalizar valores por defecto)
    st.session_state.filtros.append({"columna": None, "comparacion": None, "valor": None})

if button_delete_filter:
    st.session_state.filtros = []


st.sidebar.markdown("--------------------")


col_filtrado = [""] + ["Continente", "Pais", "Día"]
continent_filtrado = [""] + df_continents["continent"].unique()
country_filtrado = df_continents["country_name"].unique()
day_filtrado = df["day"].unique()

select_col = {"Continente": continent_filtrado,
              "Pais": country_filtrado,
              "Día": day_filtrado}



for i, diccionary in enumerate(st.session_state.filtros):
    columna_key = f"columna_{i}"
    comparacion_key = f"comparacion_{i}"
    elemento_key = f"elemento_{i}"

    

    diccionary["columna"] = st.sidebar.selectbox("Elige una columna", col_filtrado, key=columna_key)

    if not st.session_state.get(columna_key):
        break
    # Solo mostramos el tipo de comparación si se eligió una columna
    elif st.session_state.get(columna_key) == "Día":
        diccionary["comparacion"] = st.sidebar.selectbox("Elige un tipo de comparación", ["", "=", "<", ">"], key=comparacion_key)


        if not st.session_state.get(comparacion_key):
            break
        # Solo mostramos el valor si se eligió la comparación
        elif st.session_state.get(comparacion_key):
            col_seleccionada = st.session_state.get(columna_key)
            opciones = select_col.get(col_seleccionada, [])
            diccionary["valor"] = st.sidebar.selectbox("Elige un valor", opciones, key=elemento_key)

    else: 
        comparacion_key=None
        col_seleccionada = st.session_state.get(columna_key)
        opciones = select_col.get(col_seleccionada, [])
        diccionary["valor"] = st.sidebar.selectbox("Elige un valor", opciones, key=elemento_key)

    st.sidebar.markdown("--------------------")

if button_filter:

    for i, elem in enumerate(st.session_state.filtros):
        if elem["columna"] == "Día":
            df = filter_day(df, elem["comparacion"], elem["valor"])
        
        elif elem["columna"] == "Pais":
            df, df_continents = do_filter("country_name", elem["valor"], df, df_continents)

        elif elem["columna"] == "Continente":
            df, df_continents = do_filter("continent", elem["valor"], df, df_continents)
        
    

#-----------------------------------------------------------------------------------------
# Pagina principal
if "intro" not in st.session_state:
    st.session_state.intro = False

# Parte introductoria del trabajo
if not st.session_state.intro:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## ✈️ Visualización de Vuelos")
    with col2:
        st.write("")
        siguiente = st.button("Siguiente", type="primary", key="1")

    
    st.markdown("""
        Esta aplicación ha sido desarrollada con el objetivo de representar, a través de varias gráficas, la cantidad de vuelos registrados a nivel mundial durante un período específico, permitiendo además aplicar filtros personalizados e iterativos según los intereses del usuario.

        ###  Fuentes de datos

        Los datos principales utilizados provienen del conjunto público relacionado con el descenso de vuelos durante la pandemia de COVID-19 en 2020. En concreto, se ha utilizado el dataset:

        - [flightlist_20200301_20200331.csv.gz](https://zenodo.org/records/7923702) — descargado desde Zenodo.

        Para enriquecer y contextualizar los datos, se han empleado también los siguientes conjuntos de apoyo:

        - [airport-codes.csv](https://datahub.io/core/airport-codes/r/airport-codes.csv): contiene información de aeropuertos a nivel global.
        - [country-list.csv](https://datahub.io/core/country-list/r/data.csv): utilizado para normalizar los nombres de los países en inglés.

        ---

        ##  Funcionalidades principales

        ###  Sistema de filtrado interactivo

        Se ha implementado un sistema de filtrado altamente flexible que permite:

        - Añadir filtros de forma manual y personalizada.
        - Eliminar todos los filtros aplicados sin necesidad de recargar la aplicación.
        - Ejecutar el filtrado de datos únicamente cuando el usuario lo indique.
        - Visualizar y configurar progresivamente cada filtro en función de las opciones seleccionadas previamente.

        ---

        ###  Gráfico de líneas con marcadores

        Se incluye una visualización lineal con marcadores que, aunque no es interactiva, permite observar de manera clara la evolución del número total de vuelos con origen o destino en cada continente. Cada punto del gráfico incluye información detallada al pasar el cursor sobre él.

        ---

        ##  Mapa coroplético

        El mapa coroplético permite visualizar la distribución geográfica de los vuelos a nivel país, coloreando cada territorio en función del número de vuelos que han llegado o partido desde él. Esta visualización facilita una interpretación clara del impacto del tráfico aéreo por región.
        """)

    siguiente2 = st.button("Siguiente", type="primary", key="2")

    if siguiente or siguiente2:
        st.session_state.intro = True



# Pestaña del trabajo
elif st.session_state.intro:
    if "help" not in st.session_state:
        st.session_state.help = [False, False]

    col1_fil1, col2_fil1 = st.columns([90, 17])
    with col1_fil1:
        graphic_lines = graph_line(df)
        st.plotly_chart(graphic_lines, use_container_width=True)

    with col2_fil1:
        st.markdown("<h2 style='margin-top: 4rem; font-size: 32px;'>Evolución de vuelos</h2>", unsafe_allow_html=True)
        help_evolution = st.button("ℹ️", help="Este gráfico muestra el número de vuelos por continente.")
        if help_evolution:
            st.session_state.help[0] = not st.session_state.help[0]
        
        if st.session_state.help[0]:
            st.write("Muestra el sumatorio de de los vuelos que han tenido como origen un determinado continente, más los vuelos que han tenido como destino un determinado continente")


    col1_fil2, col2_fil2 = st.columns([17, 90])
    with col1_fil2:
        st.markdown("<h2 style='margin-top: 4rem; font-size: 32px;'>Cantidad de vuelos</h2>", unsafe_allow_html=True)
        help_cantidad = st.button("ℹ️", help="Este gráfico muestra el número de vuelos por país.")
        if help_cantidad:
            st.session_state.help[1] = not st.session_state.help[1]

        if st.session_state.help[1]:
            st.write("Muestra el sumatorio de de los vuelos que han tenido como origen un determinado país, más los vuelos que han tenido como destino un determinado país")

    with col2_fil2:
        graphic_map = mapmundi(df, df_continents)
        st.plotly_chart(graphic_map)


    dictionary_dataframes = {"df": df, "df_continents": df_continents}
    for names in list_df:
        if checkbox[names]:
            st.dataframe(dictionary_dataframes[names])

