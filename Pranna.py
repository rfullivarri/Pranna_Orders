import requests
import os
import datetime
import locale
import numpy as np
import pandas as pd
import streamlit as st
from  streamlit_lottie import  st_lottie
from streamlit_option_menu import option_menu
from  PIL import  Image as Pillow
import plotly.express as px

#Set up web
st.set_page_config(page_title="PRANNA ORDERS",
                        page_icon="🌱",
                        layout="wide")

#CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/main.css")

#df= pd.read_excel(r"orders-2023-09-22-18-40-41.xlsx")


imagen_space,imagen_emprty=st.columns((1,3))
with imagen_space:
    st.image(r"image/pranna logo ajustado.png",use_column_width=True)
with imagen_emprty:
    st.empty()    
st.markdown("<h1 style='text-align: center; font-size: 70px;'>ORDERS</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload an article", type=("csv", "xlsx"))



if uploaded_file is not None:
    df= pd.read_excel(uploaded_file)

    #formateamos hora de entrega
    df["Hora de entrega"]= [(str(i[26:]).replace('";s:7:"','').replace('time_to";s:5:"',' - ').replace('";}','')) for i in df["Hora de entrega"]]

    #formateamos dia de entrega
    def combinar_dia_fecha(row):
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        nombre_dia = row.strftime("%A")
        fecha_formateada = row.strftime("%d-%m-%Y")
        locale.setlocale(locale.LC_TIME, '')
        return f"{nombre_dia} {fecha_formateada}"

    df["Fecha de entrega"] = df["Fecha de entrega"].apply(combinar_dia_fecha)


    used_columns1= ['Nombre (envío)','Fecha de entrega','Hora de entrega','Teléfono (facturación)','Dirección lineas 1 y 2 (envío)',
                    'Importe total del pedido']
    df_client= df[used_columns1]
    df_client_unique=df_client.drop_duplicates(subset='Nombre (envío)')
    col_name_client={'Nombre (envío)':'Nombre',
                     'Hora de entrega': 'Hora',
                     'Teléfono (facturación)':'Teléfono',
                     'Dirección lineas 1 y 2 (envío)':'Dirección',
                     'Importe total del pedido':'Importe'}
    df_client_unique.rename(columns=col_name_client,inplace=True)
    
    col_name= { 'Nombre (envío)':'Nombre',
                'Hamburguesa Garbanzos':'Garbanzos', 
                'Hamburguesa Lentejas': 'Lentejas',
                'Hamburguesa Remolacha - Sin Gluten':'Remolacha SG',
                'Hamburguesa Espinaca':'Espinaca',
                'Hamburguesa Setas y Cebolla': 'Setas',
                'Hamburguesa La Sueca': 'Sueca',
                'Hamburguesa Shitake - Sin Gluten': 'Shitake SG',
                'Hamburguesa Alubias':'Alubias',
                'Frankfurt Vegano - Sin Gluten': 'Frankfurt'}
    
    # Pivota la tabla para obtener una columna para cada producto y un solo "Nombre (envío)"
    df_orders = df.pivot(index='Nombre (envío)', columns='Nombre del artículo', values='Cantidad (- reembolso)').fillna(0).astype(int)
    # Restablece el índice para que 'Nombre (envío)' sea una columna en lugar de un índice
    df_orders.reset_index(inplace=True)
    # Renombra las columnas para eliminar el nombre de la columna de valores
    df_orders.columns.name = None
    df_orders.rename(columns=col_name,inplace=True)
    df_orders["Total"]= df_orders["Garbanzos"]+df_orders["Lentejas"]+df_orders["Espinaca"]+df_orders["Setas"]+df_orders["Alubias"]+df_orders["Frankfurt"]+df_orders["Sueca"]+df_orders["Remolacha SG"]+df_orders["Shitake SG"]

    df_orders["cant_eti"]= df_orders["Total"].astype(float)-df_orders["Remolacha SG"].astype(float)-df_orders["Shitake SG"].astype(float)
    df_orders["Cant_Etiquetas"]= np.ceil(df_orders["cant_eti"]/6).astype(int)

    df_orders=df_orders[["Nombre", "Total","Cant_Etiquetas","Frankfurt" , "Alubias" , "Espinaca" , "Garbanzos" , "Sueca" , "Lentejas" , "Setas" ,"Remolacha SG" , "Shitake SG" ]]

    df_app= pd.merge(df_client_unique, df_orders, on='Nombre')

    preparado = pd.DataFrame({"Preparado":[False]})
    multiple = pd.DataFrame({"Estado":[""]})
    df_app.insert(0, 'Preparado', preparado["Preparado"])
    df_app.insert(1, 'Estado', multiple["Estado"])

    if not os.path.isfile("historial.csv"):
        with open("historial.csv", "w") as file:
            file.write(",".join(df_app.columns) + "\n")

    #FILTRO
    selected_dates = st.multiselect("Filtrar por Días de Entrega",list(df_app['Fecha de entrega'].unique()))

    if selected_dates:
        filtered_df = df_app[df_app['Fecha de entrega'].isin(selected_dates)]
    else:
        filtered_df = df_app


    # selected_date = st.selectbox("Filtrar por Día de Entrega", [None] + list(df_app['Fecha de entrega'].unique()))

    # if selected_date is not None: 
    #     filtered_df = df_app[df_app['Fecha de entrega'] == selected_date]
    # else:
    #     filtered_df = df_app

    #TABLA DE DATOS FINAL
    df_entrega=st.data_editor(
                            filtered_df,
                            column_config={ "Preparado": st.column_config.CheckboxColumn(
                            "Preparado?",
                            help="El pedido esta preparado?",
                            default=False),
                            "Estado": st.column_config.SelectboxColumn(
                            "Estado del pedido",
                            help="Seleccionar Estado del pedido",
                            width="medium",
                            options=[" ",
                                     "✅ Entregado y pagado",
                                     "🟨 Entregado sin pagar",
                                     "🔝 Pedido Preparado"],
                            required=False)},
                            disabled=["Nombre","Fecha de entrega","Hora",'Teléfono',
                                        'Dirección',
                                        'Importe',
                                        "Total","Cant_Etiquetas",
                                        "Frankfurt" , "Alubias" ,
                                        "Espinaca" , "Garbanzos", 
                                        "Sueca" , "Lentejas" , "Setas" ,
                                        "Remolacha SG" , "Shitake SG" ],
                            hide_index=True)
    
    # Obtener solo las filas con el CheckboxColumn como True
    pedidos_preparados = df_entrega[df_entrega["Preparado"] == True]

    # Calcular el total de las columnas específicas
    total_alubias = pedidos_preparados['Alubias'].sum()
    total_espinaca = pedidos_preparados['Espinaca'].sum()
    total_garbanzos = pedidos_preparados['Garbanzos'].sum()
    total_sueca = pedidos_preparados['Sueca'].sum()
    total_lentejas = pedidos_preparados['Lentejas'].sum()
    total_setas = pedidos_preparados['Setas'].sum()
    total_remola = pedidos_preparados['Remolacha SG'].sum()
    total_shitake = pedidos_preparados['Shitake SG'].sum()
    total_tarjetas = pedidos_preparados['Cant_Etiquetas'].sum()

    totales= st.container()
    st.write("---")
    column_t, emptyt2 =st.columns(2)
    with  column_t:  
        st.markdown("<h1 style='text-align: right; font-size: 40px'>ETIQUETAS:</h1>",unsafe_allow_html=True)
    with emptyt2:
        st.metric("", total_tarjetas)

    st.header("Total a preparar 🛠")

    empty1,column_1,column_2,column_3,column_4,empty2=st.columns(6)
    with  empty1:
        st.empty()
    with  column_1:   
        st.metric("Alubias", total_alubias)
    with  column_2:    
        st.metric("Espinaca", total_espinaca)
    with  column_3:
        st.metric("Garbanzos", total_garbanzos)
    with  column_4:
        st.metric("Sueca", total_sueca)
    with  empty2:
        st.empty()
    st.write("##")        
    empty3,column_5,column_6,column_7,column_8,empty4=st.columns(6)
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
    with  empty4:
        st.empty()

    st.write("##")
    st.write("---")
    st.write("##")



    #GUARDADO
    if st.button("Guardar en el Historial"):
        # Abre el archivo CSV en modo de escritura para agregar datos al final
        with open("historial.csv", "a") as file:
            # Escribe los datos de df_app en el archivo CSV
            df_app.to_csv(file, header=False, index=False)
        st.success("Los datos han sido guardados en el historial.")

    historial_df = pd.read_csv(r"historial.csv").drop_duplicates()
    st.dataframe(historial_df,use_container_width=True)













