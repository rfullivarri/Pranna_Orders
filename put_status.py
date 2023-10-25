import requests
import configparser

# Crear un objeto de configuración
config = configparser.ConfigParser()
config.read('config.ini')
consumer_key = config['API']['consumer_key']
consumer_secret = config['API']['consumer_secret']


def update_order_status(target_id, consumer_key, consumer_secret):
    # URL para actualizar el estado de la orden
    update_url = f"https://pranna.es/wp-json/wc/v3/orders/{target_id}"

    # Datos para la solicitud PUT
    data = {'status': "completed"}

    # Realizar la solicitud PUT con las credenciales
    response = requests.put(update_url, auth=(consumer_key, consumer_secret), json=data)
    return response





    # # Verificar la respuesta
    # if response.status_code == 200:
    #     return f"Estado de la orden {target_id} actualizado con éxito."
    # else:
    #     return f"Error al actualizar el estado de la orden {target_id}: {response.text}"








# Ejemplo

#target_id = 123
#new_status = "completed"

# result = update_order_status(target_id, consumer_key, consumer_secret)
# print(result)
