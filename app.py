import streamlit as st
import pandas as pd
import pydeck as pdk

import matplotlib.pyplot as plt

import numpy as np

col1, col2, col3= st.columns([15, 60, 10])

v_max=100
cmap_type ="hot"


def get_color_function(v_max, cmap_type, v_min=1):
    """
    Devuelve una función que convierte un valor en un color según el cmap y la normalización.
    
    Parámetros:
    - v_max: valor máximo para normalización
    - cmap_type: nombre del colormap (default 'plasma')
    - v_min: valor mínimo para normalización (default 1)
    
    Retorna:
    - func_color(valor): función que recibe un valor y devuelve el color RGBA (0-1) y RGB255
    """
    norm = plt.Normalize(vmin=v_min, vmax=v_max)
    cmap = plt.get_cmap(cmap_type)
    
    def func_color(valor):
        color_rgba = cmap(norm(valor))  # color RGBA normalizado 0-1
        color_rgb255 = [int(255*c) for c in color_rgba[:3]]  # color RGB 0-255
        return color_rgb255
    
    return func_color

color_func = get_color_function(v_max=v_max, cmap_type=cmap_type)


# Simulación de tus datos de rutas
df = pd.DataFrame([
    {"from_lat": 40.4168, "from_lon": -3.7038, "to_lat": 48.8566, "to_lon": 2.3522, "width":30},  # Madrid → París
    {"from_lat": 51.5074, "from_lon": -0.1278, "to_lat": 40.7128, "to_lon": -74.0060, "width": 1}, # Londres → NYC
])
df["color"] = df["width"].apply(color_func)


# Capa de arcos
arc_layer = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position='[from_lon, from_lat]',
    get_target_position='[to_lon, to_lat]',
    get_source_color="color",
    get_target_color="color",
    pickable=True
)


# Mostrar en Streamlit
with col2:
    st.pydeck_chart(pdk.Deck(
        layers=[arc_layer],
        tooltip={"text": "Vuelo"},
        height=400
    ))



def mostrar_colorbar(vmin, vmax, cmap):
    fig, ax = plt.subplots(figsize=(0.10, 4))
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax)
    cb.set_label("Numero de vuelos")
    
    with col3:
        st.pyplot(fig, use_container_width=True)

# Llamar en Streamlit
mostrar_colorbar(vmin=0, vmax=v_max, cmap=cmap_type)


