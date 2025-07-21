import pandas as pd
import gzip

# Datos de vuelos
file = "flightlist_20200301_20200331.csv.gz"

with gzip.open(file, 'rt') as f:
    df = pd.read_csv(f)

# Guardo el dataset de los continentes y paises
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

# Tambien voy a cambiar la forma en que se muestra la latitud y longitud
df_continents["latitud"] = df_continents["coordinates"].apply(lambda x: float(x.split(",")[0]))
df_continents["longitud"] = df_continents["coordinates"].apply(lambda x: float(x.split(",")[1]))

# Elimino la columna de coordenadas
df_continents.drop(["coordinates"], axis=1, inplace=True)

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


# Como sabemos que es de un mes y solo son dias, voy a quitar toda la informacion irrelevante
df["day"] = df["day"].apply(lambda x: int(x.split()[0].split("-")[2]))

# Da distintos valores de latitud y longitud para los mismos aeropuertos, quitare todas estas posiciones
# y usare las posiciones que hay en df_continentes

# Además eliminare los elemntos que no sean necesarios

df.drop(["callsign", "number", "icao24", "registration", "typecode", "firstseen", "lastseen",
         "latitude_1", "longitude_1", "altitude_1", "latitude_2", "longitude_2", "altitude_2"], axis=1, inplace=True)

def save_dfs(df, df_continents):
    df.to_csv("df.csv", index=False)
    df_continents.to_csv("df_continents.csv", index=False)
       
save_dfs(df, df_continents)