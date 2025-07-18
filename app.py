import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk

st.title("Primeras pruebas")
st.sidebar.title("Un sidebar")

st.markdown("vamos a empezar con el madown")
st.sidebar.markdown("seguimos escribiendo en markdown")

# Datos de ejemplo: origen y destino con lat/lon
data = pd.DataFrame([
    {"from_lat": 40.4168, "from_lon": -3.7038,   # Madrid
     "to_lat": 48.8566, "to_lon": 2.3522},       # París
    {"from_lat": 51.5074, "from_lon": -0.1278,   # Londres
     "to_lat": 40.7128, "to_lon": -74.0060},     # Nueva York
])

# Crear capa de arcos
arc_layer = pdk.Layer(
    "ArcLayer",
    data=data,
    get_source_position='[from_lon, from_lat]',
    get_target_position='[to_lon, to_lat]',
    get_source_color=[0, 128, 255],
    get_target_color=[255, 0, 0],
    auto_highlight=True,
    width_scale=0.0001,
    get_width=5,
    pickable=True,
)

# Vista inicial del mapa (centrado en Europa)
view_state = pdk.ViewState(latitude=45, longitude=0, zoom=1.5)

# Mostrar en Streamlit
st.pydeck_chart(pdk.Deck(
    layers=[arc_layer],
    initial_view_state=view_state,
    tooltip={"text": "Ruta entre puntos"},
))