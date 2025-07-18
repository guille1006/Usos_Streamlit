import streamlit as st
import pandas as pd
import pydeck as pdk

import matplotlib.pyplot as plt

# Normalizador entre 0 y 10000
norm = plt.Normalize(vmin=0, vmax=100)

# Colormap (ej: viridis, plasma, inferno, etc.)
cmap = plt.cm.plasma

# Ejemplo: convertir un valor a color RGB
valor = 60
color = cmap(norm(valor))  # Devuelve una tupla (r, g, b, a)

def color_normalizado(v_max, )


# Simulación de tus datos de rutas
df = pd.DataFrame([
    {"from_lat": 40.4168, "from_lon": -3.7038, "to_lat": 48.8566, "to_lon": 2.3522, "width":30},  # Madrid → París
    {"from_lat": 51.5074, "from_lon": -0.1278, "to_lat": 40.7128, "to_lon": -74.0060, "width": 1}, # Londres → NYC
])
df["color"] = df["width"].apply(lambda x: [int(c*255) for c in cmap(norm(x))[:3]])


# Capa de arcos
arc_layer = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position='[from_lon, from_lat]',
    get_target_position='[to_lon, to_lat]',
    get_source_color="color",
    get_target_color="color",
    get_width="width",
    pickable=True
)

# Vista del mapa
view_state = pdk.ViewState(
    latitude=df["from_lat"].mean(),
    longitude=df["from_lon"].mean(),
    zoom=1.5,
    pitch=0
)

# Mostrar en Streamlit
st.pydeck_chart(pdk.Deck(
    layers=[arc_layer],
    initial_view_state=view_state,
    tooltip={"text": "Vuelo"}
))




