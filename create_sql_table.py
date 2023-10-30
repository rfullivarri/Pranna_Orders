import psycopg2
import configparser
from woo_api import all_data
from normalize_api import normalize_data


#CARGA EN POSTGRE SQL
# Conéctate a la base de datos PostgreSQL local
config = configparser.ConfigParser()
config.read('config.ini')

conn = psycopg2.connect(
    dbname=config['SQL']['dbname'], # Nombre de la base de datos
    user=config['SQL']['user'], # Nombre de usuario de PostgreSQL
    password=config['SQL']['password'], # Contraseña de PostgreSQL
    host=config['SQL']['host']  # Dirección del servidor (en este caso, localhost)
)


#CREAR TABLA EN POSTGRE
table_name = 'pranna_orders_10'

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
normalize= normalize_data(all_data)
data_to_insert = normalize.values.tolist()

# Construye la consulta de inserción
insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s' for _ in range(len(normalize.columns))])})"

# Inserta los datos en la tabla
cur.executemany(insert_query, data_to_insert)
conn.commit()

# Cierra la conexión a la base de datos
conn.close()

