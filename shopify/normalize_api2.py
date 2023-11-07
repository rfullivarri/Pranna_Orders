import pandas as pd
from shop_api import all_data

import pandas as pd


#NORMALIZACION
def normalize_data_1(all_data):
    #NORMALIZACION NIVEL1
    df_order = pd.json_normalize(all_data, meta=["id"], sep="_", record_prefix="level_1")

    #NORMALIZACION NIVEL2
    level_2_columns=[]
    for columna in df_order.columns:
        primer_valor = df_order[columna][0]
        if str(primer_valor).startswith("[{"):
            level_2_columns.append(columna)
    print(level_2_columns)    

    # level_2= {}
    # df_order2= df_order[level_2_columns]
    # for l in range(len(df_order2)+1):
    #     variable_name = f"{level_2_columns[l]}_{l}"
    #     value = pd.json_normalize(all_data, record_path=[str(level_2_columns[l])], errors='ignore', meta=["id"], sep="_", record_prefix=f"level_2_{l}_")
    #     level_2[variable_name] = value 

    #print(df_order.columns)
    print("\n")
    df_order2= df_order[level_2_columns]
    for l in range(len(df_order2)+1):
        value = pd.json_normalize(all_data, record_path=[str(level_2_columns[l])], errors='ignore', meta=["id"], sep="_", record_prefix=f"level_2_{l}_")
        df_final = pd.merge(df_order, value, on="id", how="left")
        df_order = df_final

    df_final = df_final.drop(columns=level_2_columns)
    df_final = df_final.drop(columns='level_2_1_tax_lines')
    return df_final

#print(len(normalize_data_1(all_data).columns))
# dd= normalize_data_1(all_data)

# for columna in dd.columns:
#     primer_valor = dd[columna][0]
#     print(f"{columna} = {primer_valor}") # // {df_final.dtypes}")

# for key, value in level_2.items():
#     print(f"{key}: {value} \n")



#NORMALIZACION NIVEL3
# # level_3_columns=[]
# # for key, value in level_2.items():
# #     for k,val in value.items():
# #         for v in val:
# #           if str(v).startswith("[{"):
# #           level_3_columns.append(k)
# #             print(f"{key} -- {k} - {v} \n")


# level_3= {}
# df_order= df_order[level_3_columns]
# for l in range(len(df_order)+1):
#     variable_name = f"{level_2_columns[l]}_{l}"
#     value =pd.json_normalize(all_data, record_path=[str(level_2_columns[l])], errors='ignore', meta=["id"], sep="_", record_prefix=f"level_2{l}")
#     level_2[variable_name] = value 

# for key, value in level_2.items():
#     print(f"{key}: {value} \n")

    #df_items = pd.json_normalize(df_order[l], record_path=[str(level_2_columns[l])], errors='ignore', meta=["id"], sep="_", record_prefix="level_2")




# df_order = df_order.drop(columns=["line_items","meta_data",'coupon_lines','shipping_lines'])

# # Normalizar los datos de los elementos de la línea con prefijo "items_"
# df_items = pd.json_normalize(all_data, record_path=['line_items'], errors='ignore', meta=["id"], sep="items_", record_prefix="items")

# #LISTA DE DICCIONARIOS
# meta_data_list = []
# for record in all_data:
#     meta_data = record.get("meta_data", [])
#     meta_data_dict = {}
#     for entry in meta_data:
#         if entry["key"] == "_delivery_date":
#             meta_data_dict["_delivery_date"] = entry["value"]
#         elif entry["key"] == "_delivery_time_frame":
#             meta_data_dict["_delivery_time_frame"] = entry["value"]
#     meta_data_dict["id"] = record["id"]        
#     meta_data_list.append(meta_data_dict)
# df_meta_data = pd.json_normalize(meta_data_list,errors='ignore', meta=["id"], sep="meta_data_", record_prefix="meta_data")


# # Combinar los DataFrames usando una combinación "left" en función de la columna "order_id"
# df_final = pd.merge(df_order, df_items, on="id", how="left")
# df_final = pd.merge(df_final, df_meta_data, on="id", how="left")


# columns_to_exclude = ['itemsmeta_data','version', 'itemstaxes', '_links_collection', '_links_self', 'refunds','fee_lines','tax_lines']
# df_final = df_final[[col for col in df_final.columns if col not in columns_to_exclude]]
# # Importa la biblioteca datetime

# # Convierte la columna '_delivery_time_framemeta_data_time_from' a un formato válido
# df_final['_delivery_time_framemeta_data_time_from'] = df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_from']
# df_final['_delivery_time_framemeta_data_time_to'] = df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_to']
# # Convierte la cadena en objetos de fecha y hora
# df_final['_delivery_time_framemeta_data_time_from'] = pd.to_datetime(df_final['_delivery_time_framemeta_data_time_from'])
# df_final['_delivery_time_framemeta_data_time_to'] = pd.to_datetime(df_final['_delivery_time_framemeta_data_time_to'])

# # #print(df_final.columns)

# # # for columna in df_final.columns:
# # #     primer_valor = df_final[columna][0]
# # #     print(f"{columna} -- {primer_valor}")










# def normalize_data(all_data):
#     # Normalizar los datos de pedidos con prefijo "order_"
#     df_order = pd.json_normalize(all_data, meta=["id"], sep="_", record_prefix="order")
#     df_order = df_order.drop(columns=["line_items", "meta_data", 'coupon_lines', 'shipping_lines'])

#     # Normalizar los datos de los elementos de la línea con prefijo "items_"
#     df_items = pd.json_normalize(all_data, record_path=['line_items'], errors='ignore', meta=["id"], sep="items_", record_prefix="items")

#     # Lista de diccionarios
#     meta_data_list = []
#     for record in all_data:
#         meta_data = record.get("meta_data", [])
#         meta_data_dict = {}
#         for entry in meta_data:
#             if entry["key"] == "_delivery_date":
#                 meta_data_dict["_delivery_date"] = entry["value"]
#             elif entry["key"] == "_delivery_time_frame":
#                 meta_data_dict["_delivery_time_frame"] = entry["value"]
#         meta_data_dict["id"] = record["id"]
#         meta_data_list.append(meta_data_dict)
#     df_meta_data = pd.json_normalize(meta_data_list, errors='ignore', meta=["id"], sep="meta_data_", record_prefix="meta_data")

#     # Combinar los DataFrames usando una combinación "left" en función de la columna "id"
#     df_final = pd.merge(df_order, df_items, on="id", how="left")
#     df_final = pd.merge(df_final, df_meta_data, on="id", how="left")

#     columns_to_exclude = ['itemsmeta_data', 'version', 'itemstaxes', '_links_collection', '_links_self', 'refunds', 'fee_lines', 'tax_lines']
#     df_final = df_final[[col for col in df_final.columns if col not in columns_to_exclude]]

#     # Convierte las columnas de fecha y hora a objetos de fecha y hora
#     df_final['_delivery_time_framemeta_data_time_from'] = pd.to_datetime(df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_from'])
#     df_final['_delivery_time_framemeta_data_time_to'] = pd.to_datetime(df_final['_delivery_date'] + ' ' + df_final['_delivery_time_framemeta_data_time_to'])

#     return df_final
