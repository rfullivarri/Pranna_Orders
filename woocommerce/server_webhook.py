from flask import Flask, request, jsonify
import psycopg2
import pandas as pd
import configparser
from woocommerce.normalize_api import normalize_data

app = Flask(__name__)

sql_table= 'pranna_orders_180'

config = configparser.ConfigParser()
config.read('config.ini')

conn = psycopg2.connect(
    dbname=config['SQL']['dbname'], # Nombre de la base de datos
    user=config['SQL']['user'], # Nombre de usuario de PostgreSQL
    password=config['SQL']['password'], # Contraseña de PostgreSQL
    host=config['SQL']['host']  # Dirección del servidor (en este caso, localhost)
)

# ...

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            data = request.json  # Obtener los datos del pedido en formato JSON

            # Verificar si el pedido contiene un ID válido
            order_id = data.get("id")
            if order_id:
                # Consultar la base de datos para obtener todas las filas con el mismo order_id
                existing_orders = get_orders_from_db(order_id)

                if not existing_orders:
                    # No existen filas para este order_id, insertar todas las filas
                    insert_orders_into_db(data)
                else:
                    print(f"Las filas para el order_id {order_id} ya existen en la base de datos. No se insertarán duplicados.")
            else:
                print("El pedido no contiene un ID válido.")
            return jsonify({'message': 'Solicitud recibida correctamente'}), 200
        else:
            return jsonify({'error': 'Solicitud incorrecta'}), 400
    else:
        return jsonify({'error': 'Método no permitido'}), 405

def get_orders_from_db(order_id):
    # Realiza una consulta en la base de datos para obtener todas las filas con el mismo order_id
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM {sql_table} WHERE id = %s', (order_id,))
    existing_orders = cur.fetchall()
    cur.close()
    return existing_orders

def insert_orders_into_db(order_id):
    normalize= normalize_data(order_id)
    data_to_insert = normalize.values.tolist()

    # Construye la consulta de inserción
    insert_query = f"INSERT INTO {sql_table} VALUES ({', '.join(['%s' for _ in range(len(normalize.columns))])})"

    # Inserta los datos en la tabla
    cur = conn.cursor()
    cur.executemany(insert_query, data_to_insert)
    conn.commit()
    # Procesa y realiza la inserción de todas las filas de la orden en la base de datos
    # Puedes adaptar el código para insertar órdenes aquí
    pass

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")

