import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import numpy as np
import itertools
import gzip


@st.cache_data
def load_data():
    """
    Carga los datos públicos

    Returns:
    -------
    - df con los datos
    """

    # Usaré los datos del mes de marzo de 2020
    file = "flightlist_20200301_20200331.csv.gz"

    with gzip.open(file, 'rt') as f:
        df = pd.read_csv(f)

    # Voy a necesitar cambiar algunos valores para poder filtrar facilmente, uno de ellos será el nombre de los paises y 
    # clasificarlos por contientes

    # Guardo el dataset de los continentes
    url_continents = "https://datahub.io/core/airport-codes/r/airport-codes.csv"
    df_continents = pd.read_csv(url_continents)


    # Elimino las columnas que no son necesarias
    df_continents.drop(["ident", "name", "elevation_ft", "iso_region", "municipality", "gps_code", "local_code"], axis=1, inplace=True)

    # Parece ser que donde pone NaN en verdad es NA
    df_continents["continent"] = df_continents["continent"].fillna("NA")

    # Elimino las filas que no tienen codigo ICAO
    df_continents = df_continents[df_continents["icao_code"].notna()]

    # Elimino las filas que no tienen codigo IATA
    df_continents = df_continents[df_continents["iata_code"].notna()]

    # Elimino aquellos que no sean aeropuertos
    df_continents = df_continents[~df_continents["type"].isin(["heliport", "seaplane_base"])]

    # Para renombrar los paises usare un dataframe de soporte
    url_iso = "https://datahub.io/core/country-list/r/data.csv"
    df_iso = pd.read_csv(url_iso)  

    df_continents = df_continents.merge(df_iso, left_on='iso_country', right_on='Code', how='left')
    df_continents = df_continents.rename(columns={'Name': 'country_name'}).drop(columns=['Code'])

    # Tambien voy a renombrar los continentes para que sean mas amigables
    continent_names = {
        'AF': 'Africa',
        'AN': 'Antarctica',
        'AS': 'Asia',
        'EU': 'Europe',
        'NA': 'North America',
        'OC': 'Oceania',
        'SA': 'South America'
    }
    df_continents['continent'] = df_continents['continent'].replace(continent_names)



    return df



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

@st.cache_data
def count_flights_per_day(df):
    df["day"] = df["day"].apply(lambda x: x.split()[0].split("-")[2])
    serie_count = df["day"].value_counts().sort_index()
    return serie_count

#---------------------------------------------------------------------------------------
# Realización de calculos iniciales:
# Cargamos los df originales
df = load_data()
serie_per_day = count_flights_per_day(df)
fig, ax = plt.subplots()
ax.plot(serie_per_day.index, serie_per_day.values, marker='o', linestyle="-", color='blue')
ax.set_ylabel('Cantidad')
ax.set_xlabel('Día')
ax.set_title('Conteo de vuelos por día')
plt.xticks(rotation=90 )


st.pyplot(fig)







# ---------------------------------------------------------------------------
# Sidebar
st.sidebar.title("Dataframes a mostrar en la pantalla")

# Checkboxes para saber que dataframes mostrar abajo
list_df = [(df, "df")]
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





for df in list_df:
    if checkbox[df[1]]:
        st.dataframe(df[0].head(20))

