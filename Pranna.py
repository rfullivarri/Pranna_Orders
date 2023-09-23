import requests
import os
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

#df= pd.read_excel(r"orders-2023-09-22-18-40-41.xlsx")


imagen_space,imagen_emprty=st.columns((1,3))
with imagen_space:
    st.image(r"image/pranna . LOGO PRINCIPAL.png",use_column_width=True)
with imagen_emprty:
    st.empty()    
st.markdown("<h1 style='text-align: center; font-size: 70px;'>ORDERS</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload an article", type=("csv", "xlsx"))



if uploaded_file is not None:
    df= pd.read_excel(uploaded_file)
    df["Hora de entrega"]= [(str(i[26:]).replace('";s:7:"','').replace('time_to";s:5:"',' - ').replace('";}','')) for i in df["Hora de entrega"]]
    df["Fecha de entrega"]=df["Fecha de entrega"].astype(str)
    df["Entrega"]=df["Fecha de entrega"] + "\n" + df["Hora de entrega"]
    used_columns1= ['Nombre (envío)','Entrega','Teléfono (facturación)','Dirección lineas 1 y 2 (envío)',
                    'Importe total del pedido']
    df_client= df[used_columns1]
    df_client_unique=df_client.drop_duplicates(subset='Nombre (envío)')
    col_name_client={'Nombre (envío)':'Nombre',
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

    #df_app=df_app.style.set_properties(**{'text-align': 'center'}, subset=pd.IndexSlice[:, :])

    df_entrega=st.data_editor(
                            df_app,
                            column_config={ "Preparado": st.column_config.CheckboxColumn(
                            "Preparado?",
                            help="El pedido esta preparado?",
                            default=False),
                            "Estado": st.column_config.SelectboxColumn(
                            "Estado del pedido",
                            help="Seleccionar Estado del pedido",
                            width="medium",
                            options=[" ",
                                     "📊 Entregado y pagado",
                                     "📈 Entregado sin pagar",
                                     "🤖 Pedido Preparado"],
                            required=False)},
                            disabled=["Nombre","Entrega",'Teléfono',
                                        'Dirección',
                                        'Importe',
                                        "Total","Cant_Etiquetas",
                                        "Frankfurt" , "Alubias" ,
                                        "Espinaca" , "Garbanzos", 
                                        "Sueca" , "Lentejas" , "Setas" ,
                                        "Remolacha SG" , "Shitake SG" ],
                            hide_index=True)


    if st.button("Guardar en el Historial"):
        # Abre el archivo CSV en modo de escritura para agregar datos al final
        with open("historial.csv", "a") as file:
            # Escribe los datos de df_app en el archivo CSV
            df_app.to_csv(file, header=False, index=False)
        st.success("Los datos han sido guardados en el historial.")

    historial_df = pd.read_csv(r"historial.csv")
    st.dataframe(historial_df,use_container_width=True)













