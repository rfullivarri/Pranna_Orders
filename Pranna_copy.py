import os
from streamlit_extras.metric_cards import style_metric_cards
import numpy as np
import pandas as pd
import streamlit as st
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import zipfile
from io import BytesIO
from etiquetas import etiquetas


SCOPE=['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID= '1jUkNcmwj0P4v8h-xclnkPklKm9eyD4AosgOaCuY7BZI'

def get_google_sheets_data():
    credentials= None
    if os.path.exists('token.json'):
        credentials= Credentials.from_authorized_user_file("token.json",SCOPE)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow= InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPE)
            credentials= flow.run_local_server(port=0)
        with open("token.json","w") as token:
            token.write(credentials.to_json())    

    try:
        service = build("sheets", "v4", credentials= credentials)
        sheets= service.spreadsheets()
        result= sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="Ordenes!A:AF").execute()
        values=result.get("values",[])
        return values
    except HttpError as error:
        print(error)

def update_status(target_ids):
    values = get_google_sheets_data()
    credentials= None
    if os.path.exists('token.json'):
        credentials= Credentials.from_authorized_user_file("token.json",SCOPE)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow= InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPE)
            credentials= flow.run_local_server(port=0)
        with open("token.json","w") as token:
            token.write(credentials.to_json())

    if values is not None:
        for row in values:
            if row[0] in target_ids:
                row_index = values.index(row)
                # Actualizar el valor de la columna "Status" en la fila encontrada
                service = build("sheets", "v4", credentials= credentials)
                sheets= service.spreadsheets()
                sheets.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f'Ordenes!C{row_index + 1}',  # Reemplaza 'C' con la columna que corresponde a 'Status'
                    valueInputOption='RAW',
                    body={'values': [['completed']]}
                ).execute()
                # print(f'Status actualizado a "{new_status}" para el ID {row[0]}')



if __name__=="__main__":
    sheet_data = get_google_sheets_data()
    if sheet_data:
        df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])  # Use the first row as column headers
        #print(df,"\n","\n","\n")


#Set up web
st.set_page_config(page_title="PRANNA ORDERS",
                        page_icon="🌱",
                        layout="wide")

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


#DATOS DEL CLIENTE
client_columns= ['id','status','shipping.first_name','shipping.address_1','shipping.address_2','delivery_date',
                'delivery_time_frame','total']
df_client= df[client_columns]

df_client_u=df_client.drop_duplicates(subset='id')
client_col_name={'shipping.first_name':'Nombre',
                 'Teléfono (facturación)':'Teléfono',
                 'shipping.address_1':'Dirección1',
                 'shipping.address_2':'Dirección2',
                 'delivery_date': 'Dia',
                 'delivery_time_frame': 'Hora',
                 'total':'Importe',
                 'status': 'Status'}

df_client_u.columns = [client_col_name.get(col, col) for col in df_client_u.columns]

#df_client_u.rename(columns=client_col_name,inplace=True)
#print(df_client_u.columns,"\n","\n","\n")


#DATOS DEL PEDIDO
col_name= { 'id':'id',
            'PRAN01':'Alubias',
            'PRAN02':'Espinaca',
            'PRAN03':'Garbanzos', 
            'PRAN04': 'Lentejas',
            'PRAN05':'Remolacha SG',
            'PRAN06': 'Setas',
            'PRAN08': 'Sueca',
            'PRAN07': 'Shitake SG',
            'PRAN09': 'Frankfurt'}

#Crea un DataFrame con todas las columnas de 'col_name' y valores iniciales en 0
default_values = {col: 0 for col in col_name.keys()}
df_defaults = pd.DataFrame([default_values])
#Concatena 'df_defaults' con tu DataFrame original 'df'
#df_filtrado= df[df['status']=='processing']
df = pd.concat([df, df_defaults], axis=0, ignore_index=True)
#Pivota la tabla para obtener una columna para cada producto y un solo "id"
df_orders = df.pivot(index='id', columns='sku', values='quantity').fillna(0).astype(int)
#Restablece el índice
df_orders.reset_index(inplace=True)
df_orders = df_orders.reindex(columns=col_name.keys(), fill_value=0)
#Renombra las columnas para eliminar el nombre de la columna de valores
df_orders.columns.name = None
df_orders.rename(columns=col_name,inplace=True)
df_orders.fillna(0, inplace=True)
#print(df_orders.columns)
df_orders["Total"]= df_orders["Garbanzos"]+df_orders["Lentejas"]+df_orders["Espinaca"]+df_orders["Setas"]+df_orders["Alubias"]+df_orders["Frankfurt"]+df_orders["Sueca"]+df_orders["Remolacha SG"]+df_orders["Shitake SG"]
df_orders["cant_eti"]= df_orders["Total"].astype(float)-df_orders["Remolacha SG"].astype(float)-df_orders["Shitake SG"].astype(float)
df_orders["Etiquetas"]= np.ceil(df_orders["cant_eti"]/6).astype(int)
df_orders=df_orders[["id", "Total","Etiquetas", "Alubias" , "Espinaca" , "Garbanzos" , "Sueca" , "Lentejas" , "Setas" ,"Frankfurt" ,"Remolacha SG" , "Shitake SG" ]]



df_app= pd.merge(df_client_u, df_orders, on='id')
df_app1= df_app[df_app['Status']=='completed']
df_app= df_app[df_app['Status']=='processing']

df_app= df_app[['id','Nombre', 'Dirección1', 'Dirección2', 'Dia', 'Hora',
       'Importe', 'Total', 'Etiquetas', 'Alubias', 'Espinaca', 'Garbanzos',
       'Sueca', 'Lentejas', 'Setas', 'Frankfurt', 'Remolacha SG',
       'Shitake SG']]

# def etiqueta():
#     return df_app.to_csv('df_app.csv',index=False)
# etiqueta()

preparado = pd.DataFrame({"A_Preparar":[False]})
multiple = pd.DataFrame({"Estado":[""]})
df_app.insert(0, 'A_Preparar', preparado["A_Preparar"])
df_app.insert(1, 'Estado', multiple["Estado"])



#FILTRO
selected_dates = st.multiselect("Filtrar por Días de Entrega",list(df_app['Dia'].unique()))
if selected_dates:
    filtered_df = df_app[df_app['Dia'].isin(selected_dates)]
else:
    filtered_df = df_app


#TABLA DE DATOS FINAL
df_entrega=st.data_editor(
                        filtered_df,
                        column_config={"A_Preparar": st.column_config.CheckboxColumn(
                        "A_Preparar",
                        help="Que pedidos vas a preparar?",
                        default=False),
                        "Estado": st.column_config.SelectboxColumn(
                        "Estado del pedido",
                        help="Seleccionar Estado del pedido",
                        width="medium",
                        options=[" ",
                                 "🔝 Pedido Preparado",
                                 "🟨 Entregado sin pagar",
                                 "✅ Entregado y pagado"],
                        required=False)},
                        disabled=['id',"Nombre","Dia","Hora",
                                    'Dirección1',
                                    'Dirección2',
                                    'Importe',
                                    "Total","Etiquetas",
                                    "Frankfurt" , "Alubias" ,
                                    "Espinaca" , "Garbanzos", 
                                    "Sueca" , "Lentejas" , "Setas" ,
                                    "Remolacha SG" , "Shitake SG" ],
                        hide_index=True)

# Obtener solo las filas con el CheckboxColumn como True
pedidos_preparados = df_entrega[df_entrega["A_Preparar"] == True]

# Calcular el total de las columnas específicas
total_alubias = pedidos_preparados['Alubias'].sum()
total_espinaca = pedidos_preparados['Espinaca'].sum()
total_garbanzos = pedidos_preparados['Garbanzos'].sum()
total_sueca = pedidos_preparados['Sueca'].sum()
total_lentejas = pedidos_preparados['Lentejas'].sum()
total_setas = pedidos_preparados['Setas'].sum()
total_remola = pedidos_preparados['Remolacha SG'].sum()
total_shitake = pedidos_preparados['Shitake SG'].sum()
total_frankfurt = pedidos_preparados['Frankfurt'].sum()
total_tarjetas = pedidos_preparados['Etiquetas'].sum()
 

totales= st.container()
st.write("---")
button1,button2= st.columns((4,1))
button1.empty()
#button1.markdown(f"<h1 style='text-align: center; font-size: 40px; display: flex; justify-content: center; align-items: center;'>ETIQUETAS: {total_tarjetas}</h1>",unsafe_allow_html=True,)
with button2:
    # Llama a la función etiquetas y obtiene las imágenes generadas
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


st.header("Total a preparar")
empty1,etiqueta1,column_1,column_2,column_3,column_4,empty2=st.columns(7)
etiqueta1.metric("Etiquetas", total_tarjetas)
style_metric_cards( background_color = "#F2D17B",
                    border_size_px = 0,
                    border_color= "#CCC",
                    border_radius_px= 9,
                    border_left_color= "#FDF8E0",
                    box_shadow = False)
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


if st.button("Confirmar Preparacion"):
    for index, row in df_entrega.iterrows():
        if row["Estado"] == "🔝 Pedido Preparado":
            target_id = row["id"]
            update_status([target_id])
    get_google_sheets_data()

st.write("---")
st.write("##")
   
st.header("Filtros")



# Crear un filtro para el rango de fechas y nombres
df_app1['Dia'] = pd.to_datetime(df_app1['Dia'], errors='coerce')
#df_app1['Dia'] = df_app1['Dia'].dt.strftime('%d/%m/%Y')

columna1, columna2 = st.columns(2)
with columna1:
    start_date = pd.to_datetime(st.date_input("Fecha de inicio", pd.to_datetime(df_app1['Dia'].min(), errors='coerce')))
with columna2:
    end_date = pd.to_datetime(st.date_input("Fecha de fin", pd.to_datetime(df_app1['Dia'].max(), errors='coerce')))

selected_client = st.multiselect("Filtrar por Cliente",list(df_app1['Nombre'].unique()))
    
if not selected_client:
    # Si no se selecciona ningún nombre, mostrar todos los datos dentro del rango de fechas
    filtered_df = df_app1[(~df_app1['Dia'].isna()) & (df_app1['Dia'] >= start_date) & (df_app1['Dia'] <= end_date)]
else:
    # Si se selecciona al menos un nombre, aplicar el filtro por nombre y por fecha
    filtered_df = df_app1[(df_app1['Nombre'].isin(selected_client)) & (~df_app1['Dia'].isna()) & (df_app1['Dia'] >= start_date) & (df_app1['Dia'] <= end_date)]


if df_app1 is not None:
    cant_pedidos= len(filtered_df)
    filtered_df['Importe']=filtered_df['Importe'].str.replace('€', '').astype(float).round()
    
    if selected_client:
        monto_pedido= filtered_df[filtered_df["Nombre"].isin(selected_client)]["Importe"].sum()
    else:
        monto_pedido= filtered_df["Importe"].sum()
        

    total_alubias1 = filtered_df['Alubias'].sum()
    total_espinaca1 = filtered_df['Espinaca'].sum()
    total_garbanzos1 = filtered_df['Garbanzos'].sum()
    total_sueca1 = filtered_df['Sueca'].sum()
    total_lentejas1 = filtered_df['Lentejas'].sum()
    total_setas1 = filtered_df['Setas'].sum()
    total_remola1 = filtered_df['Remolacha SG'].sum()
    total_shitake1 = filtered_df['Shitake SG'].sum()
    total_tarjetas1 = filtered_df['Etiquetas'].sum()

    st.header("Informacion")
    vacio1,importe11,pedidos22,vacio2= st.columns((1,2,2,1))
    st.write("##")
    style_metric_cards( background_color = "#F2D17B",
                    border_size_px = 0,
                    border_color= "#CCC",
                    border_radius_px= 9,
                    border_left_color= "#FDF8E0",
                    box_shadow = False)
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

st.dataframe(filtered_df,use_container_width=True)

















