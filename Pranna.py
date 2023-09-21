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

imagen_space,imagen_emprty=st.columns((1,3))
with imagen_space:
    st.image(r"image/pranna . LOGO PRINCIPAL.png",use_column_width=True)
with imagen_emprty:
    st.empty()    
st.markdown("<h1 style='text-align: center; font-size: 70px;'>ORDERS</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload an article", type=("csv", "xlsx"))

if uploaded_file is not None:
    df= pd.read_excel(uploaded_file)
    #df= pd.read_excel(r"orders.xlsx")
    used_columns1= ['Nombre (envío)','Fecha del pedido','Teléfono (facturación)','Dirección lineas 1 y 2 (envío)',
                    'Importe total del pedido']
    df_client= df[used_columns1]
    df_client_unique=df_client.drop_duplicates(subset='Nombre (envío)')
    col_name= {'Hamburguesa Garbanzos':'Garbanzos', 
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

    df_orders=df_orders[["Nombre (envío)", "Total","Cant_Etiquetas","Frankfurt" , "Alubias" , "Espinaca" , "Garbanzos" , "Sueca" , "Lentejas" , "Setas" ,"Remolacha SG" , "Shitake SG" ]]

    df_app= pd.merge(df_client_unique, df_orders, on='Nombre (envío)')
    
    # Muestra el DataFrame con la columna "Opción"
    st.dataframe(df_app, width=800, height=400, use_container_width=True)













    # float_int_columns = [col for col in df_app.columns if df_app[col].dtype in (float, int)]
    # df_app= df_app.set_flags(subset=float_int_columns, **{'text-align': 'center'})


    # Define the CSS styles
    # st.markdown(
    #     f"""
    #     <style>
    #         .column-specific-style {{
    #             background-color: #96B0C8; /* Background color for specified columns */
    #         }}
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )

    # #Define a function to style specific columns with a different background color
    # def style_specific_columns(s, columns):
    #     return [f'background-color: #96B0C8' if col in columns else '' for col in s.index]

    # # Apply the styling function to the specified columns
    # df_app_style = df_app.style.apply(style_specific_columns, columns=["Remolacha SG", "Shitake SG"], axis=1)

    # # Define alternating row colors for all other rows
    # def alternate_row_colors(s):
    #     return [f'background-color: #97C0AC' if i % 2 == 0 else f'background-color: #15322C' for i in range(len(s))]

    # # Apply alternating row colors
    # df_app_style = df_app.style.apply(alternate_row_colors, axis=0)

    # # Center align float and int columns
    
    # st.data_editor(df_app_style,use_container_width=True,width=900,column_config=)

  








