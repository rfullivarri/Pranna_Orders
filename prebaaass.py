import os
import numpy as np
import pandas as pd
from pandas import json_normalize
import streamlit as st
from etiquetas import etiquetas
import requests
from requests_oauthlib import OAuth1Session
from datetime import datetime, timedelta
import configparser

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
start_date = end_date - timedelta(days=30)  


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

#df_meta_data = pd.json_normalize(data, record_path=['meta_data'], errors='ignore', meta=["id"], sep="meta_data_", record_prefix="meta_data")


# Combinar los DataFrames usando una combinación "left" en función de la columna "order_id"
df_final = pd.merge(df_order, df_items, on="id", how="left")
df_final = pd.merge(df_final, df_meta_data, on="id", how="left")

#print(df_final)

for columna in df_final.columns:
    primer_valor = df_final[columna][0]
    print(f"{columna} -- {primer_valor}")

