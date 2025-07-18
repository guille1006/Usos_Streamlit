import pandas as pd

# Leer los datos directamente desde GitHub (o local si lo prefieres)
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

# Ejemplo: ver los primeros 5 aeropuertos
print(df_airports.head())
