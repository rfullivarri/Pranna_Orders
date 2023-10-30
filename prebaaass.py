import os
import psycopg2
import numpy as np
import pandas as pd
from pandas import json_normalize
import streamlit as st
from etiquetas import etiquetas
import requests
from requests_oauthlib import OAuth1Session
from datetime import datetime, timedelta
import configparser
import json


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
request_token_url = 'https://pranna.es/wc-auth/v1/authorize'

# Crear una sesión OAuth
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)


# Calcular la fecha actual y la fecha 
end_date = datetime.now()
start_date = end_date - timedelta(days=180)  


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




#NORMALIZACION
# Normalizar los datos de pedidos con prefijo "order_"
df_order = pd.json_normalize(all_data, meta=["id"], sep="_", record_prefix="order")
df_order = df_order.drop(columns=["line_items","meta_data",'coupon_lines','shipping_lines'])

# Normalizar los datos de los elementos de la línea con prefijo "items_"
df_items = pd.json_normalize(all_data, record_path=['line_items'], errors='ignore', meta=["id"], sep="items_", record_prefix="items")

#LISTA DE DICCIONARIOS
meta_data_list = []
for record in all_data:
    meta_data = record.get("meta_data", [])
    meta_data_dict = {}
    for entry in meta_data:
        if entry["key"] == "_delivery_date":
            meta_data_dict["_delivery_date"] = entry["value"]
        elif entry["key"] == "_delivery_time_frame":
            meta_data_dict["_delivery_time_frame"] = entry["value"]
    meta_data_dict["id"] = record["id"]        
    meta_data_list.append(meta_data_dict)
df_meta_data = pd.json_normalize(meta_data_list,errors='ignore', meta=["id"], sep="meta_data_", record_prefix="meta_data")


# Combinar los DataFrames usando una combinación "left" en función de la columna "order_id"
df_final = pd.merge(df_order, df_items, on="id", how="left")
df_final = pd.merge(df_final, df_meta_data, on="id", how="left")


columns_to_exclude = ['itemsmeta_data','version', 'itemstaxes', '_links_collection', '_links_self', 'refunds','fee_lines','tax_lines']
df_final = df_final[[col for col in df_final.columns if col not in columns_to_exclude]]
# Importa la biblioteca datetime

# Convierte la columna '_delivery_time_framemeta_data_time_from' a un formato válido
df_final['_delivery_time_framemeta_data_time_from'] = df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_from']
df_final['_delivery_time_framemeta_data_time_to'] = df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_to']
# Convierte la cadena en objetos de fecha y hora
df_final['_delivery_time_framemeta_data_time_from'] = pd.to_datetime(df_final['_delivery_time_framemeta_data_time_from'])
df_final['_delivery_time_framemeta_data_time_to'] = pd.to_datetime(df_final['_delivery_time_framemeta_data_time_to'])

# #print(df_final.columns)

# # for columna in df_final.columns:
# #     primer_valor = df_final[columna][0]
# #     print(f"{columna} -- {primer_valor}")







#CARGA EN POSTGRE SQL
# Conéctate a la base de datos PostgreSQL local
conn = psycopg2.connect(
    dbname='pranna_orders',  # Nombre de la base de datos
    user='ramirofernandezdeullivarri',       # Nombre de usuario de PostgreSQL
    password='prannaorders', # Contraseña de PostgreSQL
    host='localhost'         # Dirección del servidor (en este caso, localhost)
)

#CREAR TABLA EN POSTGRE
table_name = 'pranna_orders_180'

create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INT,
    parent_id INT,
    status TEXT,
    currency TEXT,
    prices_include_tax BOOLEAN,
    date_created TIMESTAMP,
    date_modified TIMESTAMP,
    discount_total NUMERIC,
    discount_tax NUMERIC,
    shipping_total NUMERIC,
    shipping_tax NUMERIC,
    cart_tax NUMERIC,
    total NUMERIC,
    total_tax NUMERIC,
    customer_id INT,
    order_key TEXT,
    payment_method TEXT,
    payment_method_title TEXT,
    transaction_id TEXT,
    customer_ip_address TEXT,
    customer_user_agent TEXT,
    created_via TEXT,
    customer_note TEXT,
    date_completed TIMESTAMP,
    date_paid TIMESTAMP,
    cart_hash TEXT,
    number INT,
    payment_url TEXT,
    is_editable BOOLEAN,
    needs_payment BOOLEAN,
    needs_processing BOOLEAN,
    date_created_gmt TIMESTAMP,
    date_modified_gmt TIMESTAMP,
    date_completed_gmt TIMESTAMP,
    date_paid_gmt TIMESTAMP,
    currency_symbol TEXT,
    billing_first_name TEXT,
    billing_last_name TEXT,
    billing_company TEXT,
    billing_address_1 TEXT,
    billing_address_2 TEXT,
    billing_city TEXT,
    billing_state TEXT,
    billing_postcode TEXT,
    billing_country TEXT,
    billing_email TEXT,
    billing_phone TEXT,
    shipping_first_name TEXT,
    shipping_last_name TEXT,
    shipping_company TEXT,
    shipping_address_1 TEXT,
    shipping_address_2 TEXT,
    shipping_city TEXT,
    shipping_state TEXT,
    shipping_postcode TEXT,
    shipping_country TEXT,
    shipping_phone TEXT,
    itemsid INT,
    itemsname TEXT,
    itemsproduct_id INT,
    itemsvariation_id INT,
    itemsquantity INT,
    itemstax_class TEXT,
    itemssubtotal NUMERIC,
    itemssubtotal_tax NUMERIC,
    itemstotal NUMERIC,
    itemstotal_tax NUMERIC,
    itemssku TEXT,
    itemsprice NUMERIC,
    itemsparent_name TEXT,
    itemsimageitems_id INT,
    itemsimageitems_src TEXT,
    _delivery_date DATE,
    _delivery_time_framemeta_data_time_from TIMESTAMP,
    _delivery_time_framemeta_data_time_to TIMESTAMP
);
"""

cur = conn.cursor()
cur.execute(create_table_query)
conn.commit()


# Convierte el DataFrame en una lista de tuplas para insertar en la base de datos
data_to_insert = df_final.values.tolist()

# Construye la consulta de inserción
insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s' for _ in range(len(df_final.columns))])})"

# Inserta los datos en la tabla
cur.executemany(insert_query, data_to_insert)
conn.commit()

# Cierra la conexión a la base de datos
conn.close()

