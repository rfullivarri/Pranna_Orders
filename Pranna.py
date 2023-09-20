import requests
import pandas as pd
import streamlit as st
from  streamlit_lottie import  st_lottie
from streamlit_option_menu import option_menu
from  PIL import  Image as Pillow
import plotly.express as px

df= pd.read_excel(r"Pranna/orders.xlsx")

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

used_columns= ['Teléfono (facturación)',
                'Nombre (envío)', 'Dirección lineas 1 y 2 (envío)',
                'Importe total del pedido',
                'SKU', 'Artículo #', 'Nombre del artículo', 'Cantidad (- reembolso)',
                'Coste de artículo']

dfp= df[used_columns]

# Pivota la tabla para obtener una columna para cada producto y un solo "Nombre (envío)"
df_orders = dfp.pivot(index='Nombre (envío)', columns='Nombre del artículo', values='Cantidad (- reembolso)').fillna('')

# Restablece el índice para que 'Nombre (envío)' sea una columna en lugar de un índice
df_orders.reset_index(inplace=True)

# Renombra las columnas para eliminar el nombre de la columna de valores
df_orders.columns.name = None
df_orders.rename(columns=col_name,inplace=True)

# Ahora, 'df_orders' contendrá la tabla pivotada con una columna para cada producto
#print(df_client_unique,"\n",df_orders)

df_app= pd.merge(df_client_unique, df_orders, on='Nombre (envío)')

st.dataframe(df_app, use_container_width=True)









# print(df[used_columns2].head(9))
# # pedido=[df['Nombre (envío)'].unique().T]

# # persona=[]
# # direccion=[]
# # for i in range(len(df)):
# #     persona= df['Nombre (envío)'][i]
# #     direccion= df['Dirección lineas 1 y 2 (envío)'][i]
# #     articulo= df['Nombre del artículo'][i]
# #     cantidad= df['Cantidad (- reembolso)'][i]

# #     print(persona," ",direccion," ",articulo[12:]," ",cantidad,"\n")
    

# # if i in

# # sku =[]
# # producto=[]

# # # for k, v in dict(zip(df['SKU'],df['Nombre del artículo'])):
# # #     if k not in sku:
# # #         sku.append(k)
# # #     v12= str(v).split()
# # #     palabra= v12[1:]
# # #     palabra=''.join(palabra)
# # #     if palabra not in producto:
# # #         producto.append(palabra) 

# # # productos= zip(sku,producto)   




# # for k in df['SKU']:
# #     if k not in sku:
# #         sku.append(k)
# # for v in df['Nombre del artículo']:
# #     v12= str(v).split()
# #     palabra= v12[1:]
# #     palabra=''.join(palabra)
# #     if palabra not in producto:
# #         producto.append(palabra)

# # # producto =[set(producto)]

# # # productos= zip(sku,producto)

# # print(sku,"\n",producto)#,"\n",productos)

# # dfp= pd.DataFrame()


