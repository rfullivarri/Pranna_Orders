import numpy as np
import pandas as pd
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import zipfile
from io import BytesIO
from etiquetas import etiquetas
import configparser
from put_status import update_order_status
import configparser
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1Session
from datetime import datetime, timedelta


#-----------------------------------------------------------------------------------------------------------------------------------
#SET UP WEB

st.set_page_config(page_title="PRANNA ORDERS",
                        page_icon="🌱",
                        layout="wide")


#-----------------------------------------------------------------------------------------------------------------------------------
#CSS

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/main.css")

imagen_space,imagen_emprty=st.columns((1,3))
with imagen_space:
    st.image(r"image/pranna logo ajustado.png",use_column_width=True)
with imagen_emprty:
    st.empty()    
st.markdown("<h1 style='text-align: center; font-size: 70px;'>ORDERS</h1>", unsafe_allow_html=True)


#-----------------------------------------------------------------------------------------------------------------------------------
#OBTENER DATOS DE API

config = configparser.ConfigParser() # Crear un objeto de configuración
config.read('config.ini')

# URL de la API que deseas acceder
url = "https://pranna.es/wp-json/wc/v3/orders"

# Credenciales de OAuth
consumer_key = config['API']['consumer_key']
consumer_secret = config['API']['consumer_secret']

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
    #print(json.dumps(response.json(), indent=2),"\n")
    #print(response.text)
    if response.text.strip() == "[]":
        break

    data = response.json()

    if not data:
        break
    all_data.extend(data)
    page += 1


#-----------------------------------------------------------------------------------------------------------------------------------
#NORMALIZAR DE DATOS API

def normalize_data(all_data):
    # Normalizar los datos de pedidos con prefijo "order_"
    df_order = pd.json_normalize(all_data, meta=["id"], sep="_", record_prefix="order")
    df_order = df_order.drop(columns=["line_items", "meta_data", 'coupon_lines', 'shipping_lines'])

    # Normalizar los datos de los elementos de la línea con prefijo "items_"
    df_items = pd.json_normalize(all_data, record_path=['line_items'], errors='ignore', meta=["id"], sep="items_", record_prefix="items")

    # Lista de diccionarios
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
    df_meta_data = pd.json_normalize(meta_data_list, errors='ignore', meta=["id"], sep="meta_data_", record_prefix="meta_data")

    # Combinar los DataFrames usando una combinación "left" en función de la columna "id"
    df_final = pd.merge(df_order, df_items, on="id", how="left")
    df_final = pd.merge(df_final, df_meta_data, on="id", how="left")

    columns_to_exclude = ['itemsmeta_data', 'version', 'itemstaxes', '_links_collection', '_links_self', 'refunds', 'fee_lines', 'tax_lines']
    df_final = df_final[[col for col in df_final.columns if col not in columns_to_exclude]]

    # Convierte las columnas de fecha y hora a objetos de fecha y hora
    df_final['_delivery_time_framemeta_data_time_from'] = pd.to_datetime(df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_from'])
    df_final['_delivery_time_framemeta_data_time_to'] = pd.to_datetime(df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_to'])
    df_final['delivery_time_frame'] = df_final['_delivery_time_framemeta_data_time_from'].dt.strftime('%H:%M') + ' - ' + df_final['_delivery_time_framemeta_data_time_to'].dt.strftime('%H:%M')
    return df_final


#-----------------------------------------------------------------------------------------------------------------------------------
# #DATOS DEL CLIENTE

client_columns= ['id','status','shipping_first_name','shipping_address_1','shipping_address_2','_delivery_date',
                'delivery_time_frame','total']
df= normalize_data(all_data)
df_client= df[client_columns]

df_client_u=df_client.drop_duplicates(subset='id')
client_col_name={'shipping_first_name':'Nombre',
                 'Teléfono (facturación)':'Teléfono',
                 'shipping_address_1':'Dirección1',
                 'shipping_address_2':'Dirección2',
                 '_delivery_date': 'Dia',
                 'delivery_time_frame': 'Hora',
                 'total':'Importe',
                 'status': 'Status'}

df_client_u.columns = [client_col_name.get(col, col) for col in df_client_u.columns]
#print(df_client_u.head(5))


#-----------------------------------------------------------------------------------------------------------------------------------
#DATOS DEL PEDIDO

col_name= { 'id':'id',
            'PRAN01':'Alubias',
            'PRAN02':'Espinaca',
            'PRAN03':'Garbanzos', 
            'PRAN04':'Lentejas',
            'PRAN05':'Remolacha SG',
            'PRAN05-1':'Remolacha 180',
            'PRAN06':'Setas',
            'PRAN08':'Sueca',
            'PRAN07':'Shitake SG',
            'PRAN09':'Frankfurt'}

#Crea un DataFrame con todas las columnas de 'col_name' y valores iniciales en 0
default_values = {col: 0 for col in col_name.keys()}
df_defaults = pd.DataFrame([default_values])
#Concatena 'df_defaults' con tu DataFrame original 'df'
df = pd.concat([df, df_defaults], axis=0, ignore_index=True)
#Pivota la tabla para obtener una columna para cada producto y un solo "id"
df_orders = df.pivot(index='id', columns='itemssku', values='itemsquantity').fillna(0).astype(int)
#Restablece el índice
df_orders.reset_index(inplace=True)
df_orders = df_orders.reindex(columns=col_name.keys(), fill_value=0)
#Renombra las columnas para eliminar el nombre de la columna de valores
df_orders.columns.name = None
df_orders.rename(columns=col_name,inplace=True)
df_orders.fillna(0, inplace=True)
#print(df_orders.columns)
df_orders["Total"]= df_orders["Garbanzos"]+df_orders["Lentejas"]+df_orders["Espinaca"]+df_orders["Setas"]+df_orders["Alubias"]+df_orders["Frankfurt"]+df_orders["Sueca"]+df_orders["Remolacha SG"]+df_orders["Shitake SG"]+df_orders["Remolacha 180"]
df_orders["cant_eti"]= df_orders["Total"].astype(float)-df_orders["Remolacha SG"].astype(float)-df_orders["Shitake SG"].astype(float)
df_orders["Etiquetas"]= np.ceil(df_orders["cant_eti"]/6).astype(int)
df_orders=df_orders[["id", "Total","Etiquetas", "Alubias" , "Espinaca" , "Garbanzos" , "Sueca" , "Lentejas" , "Setas" ,"Frankfurt" ,"Remolacha 180","Remolacha SG" , "Shitake SG" ]]


#-----------------------------------------------------------------------------------------------------------------------------------
#UNIFICACION DE DF'S

df_app= pd.merge(df_client_u, df_orders, on='id')
df_app1= df_app[df_app['Status']=='completed']
df_app= df_app[df_app['Status']=='processing']

df_app= df_app[['id','Nombre', 'Dirección1', 'Dirección2', 'Dia', 'Hora',
       'Importe', 'Total', 'Etiquetas', 'Alubias', 'Espinaca', 'Garbanzos',
       'Sueca', 'Lentejas', 'Setas', 'Frankfurt', 'Remolacha 180','Remolacha SG',
       'Shitake SG']]

preparado = pd.DataFrame({"A_Preparar":[False]})
multiple = pd.DataFrame({"Estado":[""]})
df_app.insert(0, 'A_Preparar', preparado["A_Preparar"])
df_app.insert(1, 'Estado', multiple["Estado"])


#-----------------------------------------------------------------------------------------------------------------------------------
#FILTRO

selected_dates = st.multiselect("Filtrar por Días de Entrega",list(df_app['Dia'].unique()))
if selected_dates:
    filtered_df = df_app[df_app['Dia'].isin(selected_dates)]
else:
    filtered_df = df_app


#-----------------------------------------------------------------------------------------------------------------------------------
#TABLA DE DATOS FINAL

df_entrega=st.data_editor(filtered_df,
                        column_config={
                            "A_Preparar":st.column_config.CheckboxColumn(
                                            "A_Preparar",
                                            help="Que pedidos vas a preparar?",
                                            default=False),
                            "Estado":st.column_config.SelectboxColumn(
                                            "Estado del pedido",
                                            help="Seleccionar Estado del pedido",
                                            width="medium",
                                            options=[" ",
                                                     "🔝 Pedido Preparado",
                                                     "🟨 Entregado sin pagar",
                                                     "✅ Entregado y pagado"],
                                            required=False)},
                        disabled=['id',"Nombre","Dia","Hora",
                                    'Dirección1','Dirección2',
                                    'Importe',"Total","Etiquetas",
                                    "Frankfurt" , "Alubias" ,"Espinaca" , "Garbanzos", 
                                    "Sueca" , "Lentejas" , "Setas" ,"Remolacha 180",
                                    "Remolacha SG" , "Shitake SG" ],
                        hide_index=True)

#Obtener solo las filas con el CheckboxColumn como True
pedidos_preparados = df_entrega[df_entrega["A_Preparar"] == True]

# Calcular el total de las columnas específicas
total_alubias = pedidos_preparados['Alubias'].sum()
total_espinaca = pedidos_preparados['Espinaca'].sum()
total_garbanzos = pedidos_preparados['Garbanzos'].sum()
total_sueca = pedidos_preparados['Sueca'].sum()
total_lentejas = pedidos_preparados['Lentejas'].sum()
total_setas = pedidos_preparados['Setas'].sum()
total_remola = pedidos_preparados['Remolacha SG'].sum()
total_remola180 = pedidos_preparados['Remolacha 180'].sum()
total_shitake = pedidos_preparados['Shitake SG'].sum()
total_frankfurt = pedidos_preparados['Frankfurt'].sum()
total_tarjetas = pedidos_preparados['Etiquetas'].sum()


#-----------------------------------------------------------------------------------------------------------------------------------
#BOTON DE DESCARGA DE ETIQUETAS

totales= st.container()
st.write("---")
button1,button2= st.columns((4,1))
button1.empty()
with button2:
    etiquetas_images = etiquetas(df_app)
    # Crea un archivo ZIP y agrega las imágenes a él
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for i, img_bytes in enumerate(etiquetas_images):
            zipf.writestr(f"etiqueta_{i}.png", img_bytes)

    # Descarga el archivo ZIP como un solo botón
    st.download_button(
        label="Descargar Todas las Etiquetas",
        data=zip_buffer.getvalue(),
        key="etiquetas.zip",
        file_name="etiquetas.zip",)
    

#-----------------------------------------------------------------------------------------------------------------------------------
#WINDOW DE PRODUCTOS/PEDIDOS

st.header("Total a preparar")
empty1,etiqueta1,column_1,column_2,column_3,column_4,empty2=st.columns(7)
etiqueta1.metric("Etiquetas", total_tarjetas)
# style_metric_cards( background_color = "#F2D17B",
#                     border_size_px = 0,
#                     border_color= "#CCC",
#                     border_radius_px= 9,
#                     border_left_color= "#FDF8E0",
#                     box_shadow = False)
with  empty1:
    st.empty()
column_1.metric("Alubias", total_alubias,)
with  column_2:    
    st.metric("Espinaca", total_espinaca)
with  column_3:
    st.metric("Garbanzos", total_garbanzos)
with  column_4:
    st.metric("Sueca", total_sueca)
with  empty2:
    st.empty()
st.write("##")        
empty3,column_5,column_6,column_7,column_8,column_9,empty4=st.columns(7)
st.write("##")
with  empty1:
    st.empty() 
with  column_5:  
    st.metric("Lentejas", total_lentejas)
with  column_6:
    st.metric("Setas", total_setas)
with  column_7:
    st.metric("Shitake", total_shitake)
with  column_8:
    st.metric("Remolacha", total_remola)
with  column_9:
    st.metric("Frankfurt", total_frankfurt)
with  empty4:
    st.empty()
st.write("##")


#-----------------------------------------------------------------------------------------------------------------------------------
#CONFIRMAR PREPARACION DE PEDIDOS

if st.button("Confirmar Preparacion"):
    for index, row in df_entrega.iterrows():
        if row["Estado"] == "✅ Entregado y pagado":
            target_id = row["id"]
            update_order_status(target_id, consumer_key, consumer_secret)


#-----------------------------------------------------------------------------------------------------------------------------------
#HISTORIAL + FILTROS

st.write("---")
st.write("##")

st.header("Filtros")

# Crear un filtro para el rango de fechas y nombres
df_app1['Dia'] = pd.to_datetime(df_app1['Dia'], errors='coerce')

# Filtrar fechas no nulas
valid_dates = df_app1['Dia'].dropna()

columna1, columna2 = st.columns(2)
with columna1:
    #start_date = st.date_input("Fecha de inicio", pd.to_datetime(df_app1['Dia'].min(), errors='coerce'))
    start_date = st.date_input("Fecha de inicio", valid_dates.min() if not valid_dates.empty else pd.to_datetime("today"), key="start_date")
    start_date = pd.to_datetime(start_date)  # Convierte a datetime64[ns]
with columna2:
    #end_date = st.date_input("Fecha de fin", pd.to_datetime(df_app1['Dia'].max(), errors='coerce'))
    end_date = st.date_input("Fecha de fin", valid_dates.max() if not valid_dates.empty else pd.to_datetime("today"), key="end_date")
    end_date = pd.to_datetime(end_date)  # Convierte a datetime64[ns]


# Aplicar filtros por fecha
if start_date is not None and end_date is not None:
    filtered_df1 = df_app1[(df_app1['Dia'] >= start_date) & (df_app1['Dia'] <= end_date)]
else:
    filtered_df1 = df_app1


# Aplicar filtro por cliente
selected_client = st.multiselect("Filtrar por Cliente", list(df_app1['Nombre'].unique()))
if selected_client:
    filtered_df1 = filtered_df1[filtered_df1['Nombre'].isin(selected_client)]
else:
    filtered_df1 = df_app1

# Mostrar información solo si hay datos después de aplicar los filtros
if not filtered_df1.empty:
    cant_pedidos = len(filtered_df1)
    filtered_df1.loc[:, 'Importe'] = filtered_df1['Importe'].str.replace('€', '').astype(float).round()
    monto_pedido = filtered_df1["Importe"].sum()

    total_alubias1 = filtered_df1['Alubias'].sum()
    total_espinaca1 = filtered_df1['Espinaca'].sum()
    total_garbanzos1 = filtered_df1['Garbanzos'].sum()
    total_sueca1 = filtered_df1['Sueca'].sum()
    total_lentejas1 = filtered_df1['Lentejas'].sum()
    total_setas1 = filtered_df1['Setas'].sum()
    total_remola1 = filtered_df1['Remolacha SG'].sum()
    total_shitake1 = filtered_df1['Shitake SG'].sum()
    total_tarjetas1 = filtered_df1['Etiquetas'].sum()

    st.header("Informacion")
    vacio1,importe11,pedidos22,vacio2= st.columns((1,2,2,1))
    st.write("##")
    
    vacio1.empty()
    importe11.metric("Importe",f'€{monto_pedido}')
    pedidos22.metric("Pedidos", cant_pedidos)
    vacio2.empty()

    empty111,column_11,column_22,column_33,column_44,empty22=st.columns(6)
    st.write("##")
    empty111.empty()
    column_11.metric("Alubias", total_alubias1)
    column_22.metric("Espinaca", total_espinaca1)
    column_33.metric("Garbanzos", total_garbanzos1)
    column_44.metric("Sueca", total_sueca1)
    empty22.empty() 

    empty333,column_55,column_66,column_77,column_88,empty444=st.columns(6)
    st.write("##")
    empty333.empty()
    column_55.metric("Lentejas", total_lentejas1)
    column_66.metric("Setas", total_setas1)
    column_77.metric("Shitake", total_shitake1)
    column_88.metric("Remolacha", total_remola1)
    empty444.empty()
    # style_metric_cards( background_color = "#F2D17B",
    #                 border_size_px = 0,
    #                 border_color= "#CCC",
    #                 border_radius_px= 9,
    #                 border_left_color= "#FDF8E0",
    #                 box_shadow = False)
    
st.dataframe(filtered_df1,use_container_width=True)












# selected_client = st.multiselect("Filtrar por Cliente", list(df_app1['Nombre'].unique()))


# if not selected_client:
#     # Si no se selecciona ningún nombre, mostrar todos los datos dentro del rango de fechas
#     filtered_df = df_app1[(~df_app1['Dia'].isna()) & (df_app1['Dia'] >= start_date) & (df_app1['Dia'] <= end_date)]
# else:
#     # Si se selecciona al menos un nombre, aplicar el filtro por nombre y por fecha
#     filtered_df = df_app1[(df_app1['Nombre'].isin(selected_client)) & (~df_app1['Dia'].isna()) & (df_app1['Dia'] >= start_date) & (df_app1['Dia'] <= end_date)]



# if not filtered_df.empty:
#     # Actualizar las métricas y visualizaciones aquí
#     cant_pedidos = len(filtered_df)
#     monto_pedido = filtered_df['Importe'].sum()

#     total_alubias1 = filtered_df['Alubias'].sum()
#     total_espinaca1 = filtered_df['Espinaca'].sum()
#     total_garbanzos1 = filtered_df['Garbanzos'].sum()
#     total_sueca1 = filtered_df['Sueca'].sum()
#     total_lentejas1 = filtered_df['Lentejas'].sum()
#     total_setas1 = filtered_df['Setas'].sum()
#     total_remola1 = filtered_df['Remolacha SG'].sum()
#     total_shitake1 = filtered_df['Shitake SG'].sum()
#     total_tarjetas1 = filtered_df['Etiquetas'].sum()

#     # Mostrar las métricas
#     st.header("Informacion")
#     st.metric("Importe", f'€{monto_pedido}', delta=cant_pedidos)
#     st.metric("Pedidos", cant_pedidos)

#     # Mostrar los totales
#     st.header("Totales")
#     st.metric("Alubias", total_alubias1)
#     st.metric("Espinaca", total_espinaca1)
#     st.metric("Garbanzos", total_garbanzos1)
#     st.metric("Sueca", total_sueca1)
#     st.metric("Lentejas", total_lentejas1)
#     st.metric("Setas", total_setas1)
#     st.metric("Shitake", total_shitake1)
#     st.metric("Remolacha", total_remola1)
#     st.metric("Tarjetas", total_tarjetas1)

#     # Mostrar la tabla final
#     st.dataframe(filtered_df, use_container_width=True)
# else:
#     st.warning("No hay datos disponibles para los filtros seleccionados.")











# st.header("Filtros")

# # Crear un filtro para el rango de fechas y nombres
# df_app1['Dia'] = pd.to_datetime(df_app1['Dia'], errors='coerce')

# # Filtrar fechas no nulas
# valid_dates = df_app1['Dia'].dropna()

# columna1, columna2 = st.columns(2)
# with columna1:
#     start_date = st.date_input("Fecha de inicio", pd.to_datetime(df_app1['Dia'].min(), errors='coerce'))
#     #start_date = st.date_input("Fecha de inicio", valid_dates.min() if not valid_dates.empty else pd.to_datetime("today"), key="start_date")
#     start_date = pd.to_datetime(start_date)  # Convierte a datetime64[ns]
# with columna2:
#     end_date = st.date_input("Fecha de fin", pd.to_datetime(df_app1['Dia'].max(), errors='coerce'))
#     #end_date = st.date_input("Fecha de fin", valid_dates.max() if not valid_dates.empty else pd.to_datetime("today"), key="end_date")
#     end_date = pd.to_datetime(end_date)  # Convierte a datetime64[ns]

    
# selected_client = st.multiselect("Filtrar por Cliente", list(df_app1['Nombre'].unique()))
# # valid_dates_filtered = valid_dates.dropna()

# # # Filtrar fechas no nulas antes de aplicar los filtros
# # if not selected_client:
# #     # Si no se selecciona ningún nombre, mostrar todos los datos dentro del rango de fechas
# #     filtered_df = df_app1[(df_app1['Dia'].isin(valid_dates_filtered)) & (df_app1['Dia'] >= np.datetime64(start_date)) & (df_app1['Dia'] <= np.datetime64(end_date))]
# # else:
# #     # Si se selecciona al menos un nombre, aplicar el filtro por nombre y por fecha
# #     filtered_df = df_app1[(df_app1['Nombre'].isin(selected_client)) & (df_app1['Dia'].isin(valid_dates_filtered)) & (df_app1['Dia'] >= np.datetime64(start_date)) & (df_app1['Dia'] <= np.datetime64(end_date))]














# # st.header("Filtros")

# # # Crear un filtro para el rango de fechas y nombres
# # #min_date = df_app1['Dia'].dropna().min()
# # df_app1['Dia'] = pd.to_datetime(df_app1['Dia'], errors='coerce')
# # #df_app1['Dia'] = df_app1['Dia'].dt.strftime('%d/%m/%Y')

# # columna1, columna2 = st.columns(2)
# # with columna1:
# #     #start_date = pd.to_datetime(st.date_input("Fecha de inicio", min_date, errors='coerce'))
# #     start_date = pd.to_datetime(st.date_input("Fecha de inicio", pd.to_datetime(df_app1['Dia'].min(), errors='coerce')))
# # with columna2:
# #     end_date = pd.to_datetime(st.date_input("Fecha de fin", pd.to_datetime(df_app1['Dia'].max(), errors='coerce')))

# # selected_client = st.multiselect("Filtrar por Cliente",list(df_app1['Nombre'].unique()))
    
# if not selected_client:
#     # Si no se selecciona ningún nombre, mostrar todos los datos dentro del rango de fechas
#     filtered_df = df_app1[(~df_app1['Dia'].isna()) & (df_app1['Dia'] >= start_date) & (df_app1['Dia'] <= end_date)]
# else:
#     # Si se selecciona al menos un nombre, aplicar el filtro por nombre y por fecha
#     filtered_df = df_app1[(df_app1['Nombre'].isin(selected_client)) & (~df_app1['Dia'].isna()) & (df_app1['Dia'] >= start_date) & (df_app1['Dia'] <= end_date)]


# if df_app1 is not None:
#     cant_pedidos= len(filtered_df)
#     filtered_df['Importe']=filtered_df['Importe'].str.replace('€', '').astype(float).round()
    
#     if selected_client:
#         monto_pedido= filtered_df[filtered_df["Nombre"].isin(selected_client)]["Importe"].sum()
#     else:
#         monto_pedido= filtered_df["Importe"].sum()
        

#     total_alubias1 = filtered_df['Alubias'].sum()
#     total_espinaca1 = filtered_df['Espinaca'].sum()
#     total_garbanzos1 = filtered_df['Garbanzos'].sum()
#     total_sueca1 = filtered_df['Sueca'].sum()
#     total_lentejas1 = filtered_df['Lentejas'].sum()
#     total_setas1 = filtered_df['Setas'].sum()
#     total_remola1 = filtered_df['Remolacha SG'].sum()
#     total_shitake1 = filtered_df['Shitake SG'].sum()
#     total_tarjetas1 = filtered_df['Etiquetas'].sum()

#     st.header("Informacion")
#     vacio1,importe11,pedidos22,vacio2= st.columns((1,2,2,1))
#     st.write("##")
#     style_metric_cards( background_color = "#F2D17B",
#                     border_size_px = 0,
#                     border_color= "#CCC",
#                     border_radius_px= 9,
#                     border_left_color= "#FDF8E0",
#                     box_shadow = False)
#     vacio1.empty()
#     importe11.metric("Importe",f'€{monto_pedido}')
#     pedidos22.metric("Pedidos", cant_pedidos)
#     vacio2.empty()

#     empty111,column_11,column_22,column_33,column_44,empty22=st.columns(6)
#     st.write("##")
#     empty111.empty()
#     column_11.metric("Alubias", total_alubias1)
#     column_22.metric("Espinaca", total_espinaca1)
#     column_33.metric("Garbanzos", total_garbanzos1)
#     column_44.metric("Sueca", total_sueca1)
#     empty22.empty() 

#     empty333,column_55,column_66,column_77,column_88,empty444=st.columns(6)
#     st.write("##")
#     empty333.empty()
#     column_55.metric("Lentejas", total_lentejas1)
#     column_66.metric("Setas", total_setas1)
#     column_77.metric("Shitake", total_shitake1)
#     column_88.metric("Remolacha", total_remola1)
#     empty444.empty()

# st.dataframe(filtered_df,use_container_width=True)
