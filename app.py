import streamlit as st
import pandas as pd
import pydeck as pdk

import matplotlib.pyplot as plt

import numpy as np
import io

# Normalizador entre 0 y 10000
norm = plt.Normalize(vmin=0, vmax=100)

# Colormap (ej: viridis, plasma, inferno, etc.)
cmap = plt.cm.plasma

# Ejemplo: convertir un valor a color RGB
valor = 60
color = cmap(norm(valor))  # Devuelve una tupla (r, g, b, a)

def mostrar_colorbar(vmin, vmax, cmap):
    fig, ax = plt.subplots(figsize=(1, 5))
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax)
    cb.set_label("Numero de vuelos")
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', transparent=True)
    buf.seek(0)
    st.image(buf, caption="Escala de colores", use_column_width=False)

# Llamar en Streamlit
mostrar_colorbar(vmin=0, vmax=100, cmap=plt.cm.plasma)

def color_normalizado(v_max):
    norm = plt.Normalize(v_min=1, vmax=v_max)
    cmap = plt.cm.plasma    


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
    pickable=True
)


# Mostrar en Streamlit
st.pydeck_chart(pdk.Deck(
    layers=[arc_layer],
    tooltip={"text": "Vuelo"}
))




