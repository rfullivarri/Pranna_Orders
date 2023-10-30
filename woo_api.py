import configparser
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1Session
from datetime import datetime, timedelta


#OBTENER DATOS DE API
# Crear un objeto de configuración
config = configparser.ConfigParser()
config.read('config.ini')

# URL de la API que deseas acceder
url = "https://pranna.es/wp-json/wc/v3/orders"

# Credenciales de OAuth
consumer_key = config['API']['consumer_key']
consumer_secret = config['API']['consumer_secret']

# URL de solicitud de token
#request_token_url = 'https://pranna.es/wc-auth/v1/authorize'

# Crear una sesión OAuth
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)


# Calcular la fecha actual y la fecha 
end_date = datetime.now()
start_date = end_date - timedelta(days=10)  


all_data = []
page = 1
while True:
    # Parámetros para filtrar por rango de fechas y página
    params = {
        'after': start_date.isoformat(),
        'before': end_date.isoformat(),
        'page': page}
    # Realizar la solicitud a la API
    response = oauth.get(url, params=params)
    data = response.json()

    if not data:
        break
    all_data.extend(data)
    page += 1

print(f"Número de registros obtenidos: {len(all_data)} \n")