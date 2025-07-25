import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import numpy as np
import itertools


@st.cache_data
def load_data():
    """
    Carga los datos públicos de la base de datos OpenFlights directamente desde GitHub

    Returns:
    -------
    - Tres objetos de tipo pandas.Dataframe:
        df_airports, df_airlines, df_routes
    """
    # Leer los datos directamente desde GitHub
    url_airports = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    url_airlines = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"
    url_routes = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

    # Columnas para cada archivo (documentadas en OpenFlights)
    columns_airports = [
        "Airport ID", "Name", "City", "Country", "IATA", "ICAO",
        "Latitude", "Longitude", "Altitude", "Timezone", "DST",
        "Tz database time zone", "Type", "Source"
    ]

    columns_airlines = [
        "Airline ID", "Name", "Alias", "IATA", "ICAO", "Callsign",
        "Country", "Active"
    ]

    columns_routes = [
        "Airline", "Airline ID", "Source airport", "Source airport ID",
        "Destination airport", "Destination airport ID",
        "Codeshare", "Stops", "Equipment"
    ]

    # Cargar los DataFrames
    df_airports = pd.read_csv(url_airports, header=None, names=columns_airports)
    df_airlines = pd.read_csv(url_airlines, header=None, names=columns_airlines)
    df_routes = pd.read_csv(url_routes, header=None, names=columns_routes)

    return df_airports, df_airlines, df_routes


def unir_pos_geografica(df, columns=["Source airport", "Destination airport"]):
    combinaciones = list(itertools.product(["Latitude", "Longitude"], columns))
    for eje, posicion in combinaciones:
        df = df.merge(
            df_airports[["IATA", eje]],
            left_on=posicion,
            right_on="IATA",
            how="left"
        )

        df.rename(columns={eje: f"{posicion.split()[0]} {eje}"}, inplace=True)
        df.drop(columns=["IATA"], inplace=True)
    return df 


def num_vuelos_ida_vuelta(df):
    contador_viajes = dict()

    for elem in df["Journeys"]:
        if elem in contador_viajes:
            contador_viajes[elem]+=1

        else:
            elem_split = elem.split("-")
            elem_reverse = elem_split[1]+"-"+elem_split[0]

            if elem_reverse in contador_viajes:
                contador_viajes[elem_reverse]+=1

            else:
                contador_viajes[elem]=1

    df_result = pd.DataFrame([{"Journeys": k, "Num vuelos": v} for k, v in contador_viajes.items()])
    df_result = pd.merge(df_result, df[["Journeys", "Source airport", "Destination airport"]], on="Journeys", how="left")
    return df_result



def get_color_function(v_max, cmap_type, v_min=1):
    """
    Devuelve una función que convierte un valor en un color según el cmap y la normalización.
    
    Parameters:
    ----------
    - v_max: valor máximo para normalización
    - cmap_type: nombre del colormap
    - v_min: valor mínimo para normalización (default 1)
    
    Returns:
    -------
    - func_color(valor): función que recibe un valor y devuelve el color RGB255
    """
    norm = plt.Normalize(vmin=v_min, vmax=v_max)
    cmap = plt.get_cmap(cmap_type)
    
    def func_color(valor):
        color_rgba = cmap(norm(int(valor)))  # color RGBA normalizado 0-1
        color_rgb255 = [int(255*c) for c in color_rgba[:3]]  # color RGB 0-255
        return color_rgb255
    
    return func_color


def mostrar_colorbar(vmax, cmap, vmin=1):
    """
    Muestra una barra de color vertical en una aplicación Streamlit.

    Parameters
    ----------
    - vmax : Valor máximo de la escala de colores
    - cmap : Colormap a utilizar
    - vmin : Valor mínimo de la escala de colores. Por defecto es 1

    Returns
    -------
    None
    """

    fig, ax = plt.subplots(figsize=(0.10, 4))
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax)
    cb.set_label("Numero de vuelos")
    
    with col3:
        st.pyplot(fig, use_container_width=True)



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


#---------------------------------------------------------------------------------------
# Realización de calculos iniciales:
# Cargamos los df originales
df_airports, df_airlines, df_routes = load_data()

combinaciones = list(itertools.product(["Latitude", "Longitude"], ["Source", "Destination"]))

df_trips = df_routes.groupby(["Source airport", "Destination airport"]).size().reset_index(name="vuelos")
df_trips["Journeys"] = df_trips["Source airport"] + "-" + df_trips["Destination airport"]


df_ida_vuelta = num_vuelos_ida_vuelta(df_trips)
df_ida_vuelta = unir_pos_geografica(df_ida_vuelta)


# Establecemos los colores que usaremos para los arcos y dibujamos la colorbar
v_max=df_ida_vuelta["Num vuelos"].max()
cmap_type ="hot"
color_func = get_color_function(v_max=v_max, cmap_type=cmap_type)


df_ida_vuelta["color"] = df_ida_vuelta["Num vuelos"].apply(color_func)


# Capa de arcos
arc_layer = pdk.Layer(
    "ArcLayer",
    data=df_ida_vuelta,
    get_source_position=["Source Longitude", "Source Latitude"],
    get_target_position=["Destination Longitude", "Destination Latitude"],
    get_source_color="color",
    get_target_color="color",
    pickable=True
)



# ---------------------------------------------------------------------------
# Sidebar
st.sidebar.title("Dataframes a mostrar en la pantalla")

# Checkboxes para saber que dataframes mostrar abajo
list_df = [(df_airports, "df_airports"), (df_airlines, "df_airlines"), (df_routes, "df_routes"), (df_ida_vuelta, "df_ida_vuelta")]
checkbox = dict()
for df in list_df:
    checkbox[df[1]] = st.sidebar.checkbox(df[1])

    
st.sidebar.title("Filtrado")

# Inicializamos lista de filtros si no existe
if "filtros" not in st.session_state:
    st.session_state.filtros = []



button_add_filter, button_filter = n_columns_sidebar(n_elems=2, 
    list_elems=[lambda: st.button("Añadir filtro"),
                lambda: st.button("Realizar filtro")]
)

# Si el botón "Añadir filtro" fue presionado, activa el filtro
if button_add_filter:
    # Añadir un filtro vacío (puedes personalizar valores por defecto)
    st.session_state.filtros.append({"columna": None, "elemento": None})



for i, filtro in enumerate(st.session_state.filtros):
    col1, col2 = two_columns_sidebar(
        elem1=lambda key=f"columna_{i}": st.selectbox(
            "Elige una columna", ["1", "2", "3"], key=key
        ),
        elem2=lambda key=f"elemento_{i}": st.selectbox(
            "Elige un elemento", ["A", "B", "C"], key=key
        )
    )




#-----------------------------------------------------------------------------------------
# Pagina principal

# Dividimos la página principal en 3 columnas
col1, col2, col3= st.columns([15, 60, 10])

mostrar_colorbar(v_max, cmap_type)

# Mostrar en Streamlit
initial_view_state = pdk.ViewState(
    latitude=df_ida_vuelta["Source Latitude"].mean(),
    longitude=df_ida_vuelta["Source Longitude"].mean(),
    zoom=2
)

with col2:
    st.pydeck_chart(pdk.Deck(
        layers=[arc_layer],
        tooltip={"text": "Journeys"},
        initial_view_state=initial_view_state,
        height=400
    ))



for df in list_df:
    if checkbox[df[1]]:
        st.dataframe(df[0].head(20))

st.write(v_max)