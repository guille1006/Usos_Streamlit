import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import numpy as np
import itertools
import gzip
import plotly.express as px
import plotly.graph_objects as go


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
    res = list()
    with st.sidebar:
        with st.container():
            col_sidebar = st.columns(n_elems)

            for index, col in enumerate(col_sidebar):
                with col:
                    res.append(list_elems[index]())


    return res

def count_flights_per_day(df):
    df_count = pd.DataFrame()
    df_count["num_flights"] = df["day"].value_counts().sort_index()
    df_count["day"] = df_count.index

    return df_count

def count_flights_by_country_origin(df):
    df_count = pd.DataFrame()
    df_count["num_flights"] = df["origin"].value_counts().reset_index()
    df_count.columns = ["origin", "num_flights"]
    df_merge = pd.merge(df_count, df_continent, left_on="origin", right_on="icao_code", how="left")


def filter_df_continent(df_continents, col, elem):
    df_continents_filt =  df_continents[df_continents[col]==elem]
    return df_continents_filt

def filter_df(df, df_continents_filt):
    df_filt = df[df["origin"].isin(df_continents_filt["icao_code"]) | df["destination"].isin(df_continents_filt["icao_code"])]
    return df_filt

def do_filter(col, elem, df_filtered, df_continents_filtered):
    df_continents_filtered = filter_df_continent(df_continents_filtered, col, elem)
    df_filt = filter_df(df_filtered, df_continents_filtered)
    return df_filt, df_continents_filtered
   
def filter_day(df, type_filter, day):
    if type_filter == "=":
        df = df[df["day"]==day]

    elif type_filter == "<":
        df = df[df["day"]<day]

    elif type_filter == ">":
        df = df[df["day"]>day]

    return df


def graph_df_total_line(df):
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
    fig.add_trace(
        go.Scatter(
            x=df_add["day"],
            y=df_add["num_flights"],
            mode="lines+markers",
            hovertemplate=("day: %{x}<br> num_flights: %{y}<br>"),
            name=name
        )
    )



def graph_line(df):
    df_count = count_flights_per_day(df)
    fig_scatter = graph_df_total_line(df)

    for continent in df_continents["continent"].unique():
        df_filtered, _ = do_filter("continent", continent, df, df_continents)
        df_count = count_flights_per_day(df_filtered)
        graph_add_line(df_count, fig_scatter, continent)

    # Una funcion adicional que me ha salido al usar un elemento "or" a la hora de filtrar, es que te muestra 
    # tanto los vuelos de ida o vuelata del contiente filtrada como los vuelos de ida/vuelta hacia ese contienente

    return fig_scatter


def mapmundi(df):
    fig = px.choropleth(
    df,
    locations="country_name",
    locationmode="country_names",  
    color="color",
    hover_name="country_name",   
    hover_data={"color": True} , 
    color_continuous_scale="Blues")

    fig.show()

#---------------------------------------------------------------------------------------
# Realización de calculos iniciales:
# Cargamos los df originales
df, df_continents = load_data()


# ---------------------------------------------------------------------------
# Sidebar

# Cambiar el ancho de la sidebar usando CSS
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
list_df = [(df, "df"), (df_continents, "df_continents")]
checkbox = dict()
for dataframe in list_df:
    checkbox[dataframe[1]] = st.sidebar.checkbox(dataframe[1])


    
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
            df, df_continent = do_filter("country_name", elem["valor"], df, df_continents)

        elif elem["columna"] == "Continente":
            df, df_continent = do_filter("continent", elem["valor"], df, df_continents)

#-----------------------------------------------------------------------------------------
# Pagina principal

# Dividimos la página principal en 3 columnas
col1, col2, col3= st.columns([15, 60, 10])

with col2:
    graphic = graph_line(df)
    st.plotly_chart(graphic)




for df in list_df:
    if checkbox[df[1]]:
        st.dataframe(df[0])

