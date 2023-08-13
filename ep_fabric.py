import pandas as pd
from api_calls import used_store, used_buffer, get_external_stocks, get_token, get_sku_en_almacen, create_external_order, get_token_oc, get_estado_oc, create_other_group_order
import random
import re
from datetime import timezone, timedelta
import datetime
import requests
import ast
from bdd_manage import add_external_oc, remove_from_db_oc, update_to_accepted_oc, see_created_oc, see_accepted_oc

# external_products = ['CLJETA1', 'USJETA1', 'CHJETA1', 'CLCREW', 'USCREW',
#                      'CHCREW', 'CLBOE737', 'CLAB320', 'CLAB330', 'CLAB340',
#                      'CLBOE747', 'CLNOV', 'CLINT', 'CLEXP', 'CLOFC', 'CLCPT',
#                      'CLCMD', 'USBOE737', 'USAB320', 'USAB330', 'USAB340', 'USBOE747',
#                      'USNOV', 'USINT', 'USEXP', 'USOFC', 'USCPT', 'USCMD', 'CHBOE737',
#                      'CHAB320', 'CHAB330', 'CHAB340', 'CHBOE747', 'CHNOV', 'CHINT',
#                      'CHEXP', 'CHOFC', 'CHCPT', 'CHCMD']

# Para hacer dict de sku y productores
# def read_csv():
#     products_dict = {}
#     df_productos = pd.read_csv("Static_Data/productos.csv", delimiter=",")
#     df_productos.rename(columns = {'Grupos Productores': 'Productores', 'Producción': 'Produccion'}, inplace = True)
#     product_list = df_productos.SKU.values.tolist()
#     # lote_list = df_productos.Lote.values.tolist()
#     groups_list = df_productos.Productores.values.tolist()
#     tipo_prod = df_productos.Produccion.values.tolist()
#     lista_sku = []
#     for x in range(0, len(product_list)):
#         if tipo_prod[x] == "producto final":
#             if '12' not in groups_list[x]:
#                 lista_sku.append(product_list[x])
#     print(len(lista_sku))
#     return lista_sku

# print(read_csv())

# i = groups_list[x].replace("'", "")
# res = i.strip('][').split(', ')
# res1 = list(map(int, res))
# products_dict[product_list[x]] = res1

# Lista con TODOS los vuelos directos y los vuelos con escala que no producimos
external_products = ['SCLIAD', 'IADCDG', 'IADMEL', 'IADPEK', 
                    'IADFEZ', 'SCLCDG', 'CDGIAD', 'CDGMEL', 
                    'CDGPEK', 'CDGFEZ', 'SCLMEL', 'MELIAD', 'MELCDG', 
                    'MELPEK', 'MELFEZ', 'SCLPEK', 'PEKIAD', 'PEKCDG', 
                    'PEKMEL', 'PEKFEZ', 'SCLFEZ', 'FEZIAD', 'FEZCDG', 
                    'FEZMEL', 'FEZPEK', 'IADSCL', 'CDGSCL', 'MELSCL', 
                    'PEKSCL', 'FEZSCL',
                    'SCLCDGMEL', 'SCLCDGPEK', 'SCLMELCDG', 'SCLMELPEK', 
                    'SCLPEKCDG', 'SCLPEKMEL', 'IADSCLCDG', 'IADSCLMEL', 
                    'IADSCLPEK', 'IADCDGSCL', 'IADCDGMEL', 'IADCDGPEK', 
                    'IADMELSCL', 'IADMELCDG', 'IADMELPEK', 'IADPEKSCL', 
                    'IADPEKCDG', 'IADPEKMEL', 'CDGSCLMEL', 'CDGSCLPEK', 
                    'CDGMELSCL', 'CDGMELPEK', 'CDGPEKSCL', 'CDGPEKMEL', 
                    'MELSCLCDG', 'MELSCLPEK', 'MELCDGSCL', 'MELCDGPEK', 
                    'MELPEKSCL', 'MELPEKCDG', 'PEKSCLCDG', 'PEKSCLMEL', 
                    'PEKCDGSCL', 'PEKCDGMEL', 'PEKMELSCL', 'PEKMELCDG', 
                    'FEZSCLCDG', 'FEZSCLMEL', 'FEZSCLPEK', 'FEZCDGSCL', 
                    'FEZCDGMEL', 'FEZCDGPEK', 'FEZMELSCL', 'FEZMELCDG', 
                    'FEZMELPEK', 'FEZPEKSCL', 'FEZPEKCDG', 'FEZPEKMEL']

vuelos_escala_que_no_producimos = ['SCLCDGMEL', 'SCLCDGPEK', 'SCLMELCDG', 'SCLMELPEK', 
                                    'SCLPEKCDG', 'SCLPEKMEL', 'IADSCLCDG', 'IADSCLMEL', 
                                    'IADSCLPEK', 'IADCDGSCL', 'IADCDGMEL', 'IADCDGPEK', 
                                    'IADMELSCL', 'IADMELCDG', 'IADMELPEK', 'IADPEKSCL', 
                                    'IADPEKCDG', 'IADPEKMEL', 'CDGSCLMEL', 'CDGSCLPEK', 
                                    'CDGMELSCL', 'CDGMELPEK', 'CDGPEKSCL', 'CDGPEKMEL', 
                                    'MELSCLCDG', 'MELSCLPEK', 'MELCDGSCL', 'MELCDGPEK', 
                                    'MELPEKSCL', 'MELPEKCDG', 'PEKSCLCDG', 'PEKSCLMEL', 
                                    'PEKCDGSCL', 'PEKCDGMEL', 'PEKMELSCL', 'PEKMELCDG', 
                                    'FEZSCLCDG', 'FEZSCLMEL', 'FEZSCLPEK', 'FEZCDGSCL', 
                                    'FEZCDGMEL', 'FEZCDGPEK', 'FEZMELSCL', 'FEZMELCDG', 
                                    'FEZMELPEK', 'FEZPEKSCL', 'FEZPEKCDG', 'FEZPEKMEL']

all_lotes = {'CLJETA1': 2, 'USJETA1': 2, 'FRJETA1': 2, 'AUJETA1': 2, 'CHJETA1': 2,
             'CLCREW': 4, 'USCREW': 4, 'FRCREW': 4, 'AUCREW': 4, 'CHCREW': 4, 'CLBOE737': 1,
             'CLAB320': 1, 'CLAB330': 1, 'CLAB340': 1, 'CLBOE747': 1, 'CLNOV': 2, 'CLINT': 2,
             'CLEXP': 2, 'CLOFC': 2, 'CLCPT': 2, 'CLCMD': 2, 'USBOE737': 1, 'USAB320': 1,
             'USAB330': 1, 'USAB340': 1, 'USBOE747': 1, 'USNOV': 2, 'USINT': 2, 'USEXP': 2,
             'USOFC': 2, 'USCPT': 2, 'USCMD': 2, 'FRBOE737': 1, 'FRAB320': 1, 'FRAB330': 1,
             'FRAB340': 1, 'FRBOE747': 1, 'FRNOV': 2, 'FRINT': 2, 'FREXP': 2, 'FROFC': 2,
             'FRCPT': 2, 'FRCMD': 2, 'AUBOE737': 1, 'AUAB320': 1, 'AUAB330': 1, 'AUAB340': 1,
             'AUBOE747': 1, 'AUNOV': 2, 'AUINT': 2, 'AUEXP': 2, 'AUOFC': 2, 'AUCPT': 2, 'AUCMD': 2,
             'CHBOE737': 1, 'CHAB320': 1, 'CHAB330': 1, 'CHAB340': 1, 'CHBOE747': 1, 'CHNOV': 2,
             'CHINT': 2, 'CHEXP': 2, 'CHOFC': 2, 'CHCPT': 2, 'CHCMD': 2, 'SCLIAD': 1, 'IADCDG': 1,
             'IADMEL': 1, 'IADPEK': 1, 'SCLCDG': 1, 'CDGIAD': 1, 'CDGMEL': 1, 'CDGPEK': 1, 'SCLMEL': 1,
             'MELIAD': 1, 'MELCDG': 1, 'MELPEK': 1, 'SCLPEK': 1, 'PEKIAD': 1, 'PEKCDG': 1, 'PEKMEL': 1,
             'IADSCL': 1, 'CDGSCL': 1, 'MELSCL': 1, 'PEKSCL': 1, 'SCLIADCDG': 1, 'SCLIADMEL': 1,
             'SCLIADPEK': 1, 'SCLCDGIAD': 1, 'SCLCDGMEL': 1, 'SCLCDGPEK': 1, 'SCLMELIAD': 1, 'SCLMELCDG': 1,
             'SCLMELPEK': 1, 'SCLPEKIAD': 1, 'SCLPEKCDG': 1, 'SCLPEKMEL': 1, 'IADSCLCDG': 1,
             'IADSCLMEL': 1, 'IADSCLPEK': 1, 'IADCDGSCL': 1, 'IADCDGMEL': 1, 'IADCDGPEK': 1,
             'IADMELSCL': 1, 'IADMELCDG': 1, 'IADMELPEK': 1, 'IADPEKSCL': 1, 'IADPEKCDG': 1,
             'IADPEKMEL': 1, 'CDGSCLIAD': 1, 'CDGSCLMEL': 1, 'CDGSCLPEK': 1, 'CDGIADSCL': 1,
             'CDGIADMEL': 1, 'CDGIADPEK': 1, 'CDGMELSCL': 1, 'CDGMELIAD': 1, 'CDGMELPEK': 1,
             'CDGPEKSCL': 1, 'CDGPEKIAD': 1, 'CDGPEKMEL': 1, 'MELSCLIAD': 1, 'MELSCLCDG': 1,
             'MELSCLPEK': 1, 'MELIADSCL': 1, 'MELIADCDG': 1, 'MELIADPEK': 1, 'MELCDGSCL': 1,
             'MELCDGIAD': 1, 'MELCDGPEK': 1, 'MELPEKSCL': 1, 'MELPEKIAD': 1, 'MELPEKCDG': 1,
             'PEKSCLIAD': 1, 'PEKSCLCDG': 1, 'PEKSCLMEL': 1, 'PEKIADSCL': 1, 'PEKIADCDG': 1,
             'PEKIADMEL': 1, 'PEKCDGSCL': 1, 'PEKCDGIAD': 1, 'PEKCDGMEL': 1, 'PEKMELSCL': 1,
             'PEKMELIAD': 1, 'PEKMELCDG': 1}

# Se sacó al grupo 14 de la lista porque tienen la página caída y eso retrasa la función http://clavo14.ing.puc.cl
url_grupos = ["http://clavo1.ing.puc.cl", "http://clavo2.ing.puc.cl",
              "http://clavo3.ing.puc.cl", "http://clavo4.ing.puc.cl",
              "http://clavo5.ing.puc.cl", "http://clavo6.ing.puc.cl",
              "http://clavo7.ing.puc.cl", "http://clavo8.ing.puc.cl",
              "http://clavo9.ing.puc.cl", "http://clavo10.ing.puc.cl",
              "http://clavo11.ing.puc.cl", "http://clavo13.ing.puc.cl",
              "http://clavo15.ing.puc.cl", "http://clavo19.ing.puc.cl",
              "http://clavo17.ing.puc.cl", "http://clavo18.ing.puc.cl"]

productors_groups = {'CLJETA1': [13, 14, 15, 16, 17, 18, 19], 'USJETA1': [2, 4, 6, 8, 10, 12], 
                    'FRJETA1': [1, 3, 5, 7, 9, 11], 'AUJETA1': [13, 14, 15, 16, 17, 18, 19], 
                    'CHJETA1': [1, 3, 5, 7, 9, 11], 'MRJETA1': [2, 4, 6, 8, 10, 12], 'CLCREW': [13, 14, 15, 16, 17, 18, 19], 
                    'USCREW': [2, 4, 6, 8, 10, 12], 'FRCREW': [1, 3, 5, 7, 9, 11], 'AUCREW': [13, 14, 15, 16, 17, 18, 19], 
                    'CHCREW': [1, 3, 5, 7, 9, 11], 'MRCREW': [2, 4, 6, 8, 10, 12], 'CLBOE737': [13, 14, 15, 16, 17, 18, 19], 
                    'CLAB320': [13, 14, 15, 16, 17, 18, 19], 'CLAB330': [13, 14, 15, 16, 17, 18, 19], 'CLAB340': [13, 14, 15, 16, 17, 18, 19], 
                    'CLBOE747': [13, 14, 15, 16, 17, 18, 19], 'CLNOV': [13, 14, 15, 16, 17, 18, 19], 'CLINT': [13, 14, 15, 16, 17, 18, 19], 
                    'CLEXP': [13, 14, 15, 16, 17, 18, 19], 'CLOFC': [13, 14, 15, 16, 17, 18, 19], 'CLCPT': [13, 14, 15, 16, 17, 18, 19], 
                    'CLCMD': [13, 14, 15, 16, 17, 18, 19], 'USBOE737': [2, 4, 6, 8, 10, 12], 'USAB320': [2, 4, 6, 8, 10, 12], 
                    'USAB330': [2, 4, 6, 8, 10, 12], 'USAB340': [2, 4, 6, 8, 10, 12], 'USBOE747': [2, 4, 6, 8, 10, 12], 
                    'USNOV': [2, 4, 6, 8, 10, 12], 'USINT': [2, 4, 6, 8, 10, 12], 'USEXP': [2, 4, 6, 8, 10, 12], 'USOFC': [2, 4, 6, 8, 10, 12], 
                    'USCPT': [2, 4, 6, 8, 10, 12], 'USCMD': [2, 4, 6, 8, 10, 12], 'FRBOE737': [1, 3, 5, 7, 9, 11], 'FRAB320': [1, 3, 5, 7, 9, 11], 
                    'FRAB330': [1, 3, 5, 7, 9, 11], 'FRAB340': [1, 3, 5, 7, 9, 11], 'FRBOE747': [1, 3, 5, 7, 9, 11], 'FRNOV': [1, 3, 5, 7, 9, 11], 
                    'FRINT': [1, 3, 5, 7, 9, 11], 'FREXP': [1, 3, 5, 7, 9, 11], 'FROFC': [1, 3, 5, 7, 9, 11], 'FRCPT': [1, 3, 5, 7, 9, 11], 
                    'FRCMD': [1, 3, 5, 7, 9, 11], 'AUBOE737': [13, 14, 15, 16, 17, 18, 19], 'AUAB320': [13, 14, 15, 16, 17, 18, 19], 
                    'AUAB330': [13, 14, 15, 16, 17, 18, 19], 'AUAB340': [13, 14, 15, 16, 17, 18, 19], 'AUBOE747': [13, 14, 15, 16, 17, 18, 19], 
                    'AUNOV': [13, 14, 15, 16, 17, 18, 19], 'AUINT': [13, 14, 15, 16, 17, 18, 19], 'AUEXP': [13, 14, 15, 16, 17, 18, 19], 
                    'AUOFC': [13, 14, 15, 16, 17, 18, 19], 'AUCPT': [13, 14, 15, 16, 17, 18, 19], 'AUCMD': [13, 14, 15, 16, 17, 18, 19], 
                    'CHBOE737': [1, 3, 5, 7, 9, 11], 'CHAB320': [1, 3, 5, 7, 9, 11], 'CHAB330': [1, 3, 5, 7, 9, 11], 'CHAB340': [1, 3, 5, 7, 9, 11], 
                    'CHBOE747': [1, 3, 5, 7, 9, 11], 'CHNOV': [1, 3, 5, 7, 9, 11], 'CHINT': [1, 3, 5, 7, 9, 11], 'CHEXP': [1, 3, 5, 7, 9, 11], 
                    'CHOFC': [1, 3, 5, 7, 9, 11], 'CHCPT': [1, 3, 5, 7, 9, 11], 'CHCMD': [1, 3, 5, 7, 9, 11], 'MRBOE737': [2, 4, 6, 8, 10, 12], 
                    'MRAB320': [2, 4, 6, 8, 10, 12], 'MRAB330': [2, 4, 6, 8, 10, 12], 'MRAB340': [2, 4, 6, 8, 10, 12], 
                    'MRBOE747': [2, 4, 6, 8, 10, 12], 'MRNOV': [2, 4, 6, 8, 10, 12], 'MRINT': [2, 4, 6, 8, 10, 12], 'MREXP': [2, 4, 6, 8, 10, 12], 
                    'MROFC': [2, 4, 6, 8, 10, 12], 'MRCPT': [2, 4, 6, 8, 10, 12], 'MRCMD': [2, 4, 6, 8, 10, 12], 'SCLIAD': [2, 4, 6, 8, 10, 12], 
                    'IADCDG': [1, 3, 5, 7, 9, 11], 'IADMEL': [13, 14, 15, 16, 17, 18, 19], 'IADPEK': [1, 3, 5, 7, 9, 11], 
                    'IADFEZ': [2, 4, 6, 8, 10, 12], 'SCLCDG': [1, 3, 5, 7, 9, 11], 'CDGIAD': [2, 4, 6, 8, 10, 12], 
                    'CDGMEL': [13, 14, 15, 16, 17, 18, 19], 'CDGPEK': [1, 3, 5, 7, 9, 11], 'CDGFEZ': [2, 4, 6, 8, 10, 12], 
                    'SCLMEL': [13, 14, 15, 16, 17, 18, 19], 'MELIAD': [2, 4, 6, 8, 10, 12], 'MELCDG': [1, 3, 5, 7, 9, 11], 
                    'MELPEK': [1, 3, 5, 7, 9, 11], 'MELFEZ': [2, 4, 6, 8, 10, 12], 'SCLPEK': [1, 3, 5, 7, 9, 11], 'PEKIAD': [2, 4, 6, 8, 10, 12], 
                    'PEKCDG': [1, 3, 5, 7, 9, 11], 'PEKMEL': [13, 14, 15, 16, 17, 18, 19], 'PEKFEZ': [2, 4, 6, 8, 10, 12], 
                    'SCLFEZ': [2, 4, 6, 8, 10, 12], 'FEZIAD': [2, 4, 6, 8, 10, 12], 'FEZCDG': [1, 3, 5, 7, 9, 11], 
                    'FEZMEL': [13, 14, 15, 16, 17, 18, 19], 'FEZPEK': [1, 3, 5, 7, 9, 11], 'IADSCL': [13, 14, 15, 16, 17, 18, 19], 
                    'CDGSCL': [13, 14, 15, 16, 17, 18, 19], 'MELSCL': [13, 14, 15, 16, 17, 18, 19], 'PEKSCL': [13, 14, 15, 16, 17, 18, 19], 
                    'FEZSCL': [13, 14, 15, 16, 17, 18, 19], 'SCLIADCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 
                    'SCLIADMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 'SCLIADPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 
                    'SCLIADFEZ': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 'SCLCDGIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 
                    'SCLCDGMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 'SCLCDGPEK': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 
                    'SCLCDGFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'SCLMELIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 
                    'SCLMELCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'SCLMELPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'SCLMELFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'SCLPEKIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 
                    'SCLPEKCDG': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 'SCLPEKMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'SCLPEKFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'SCLFEZIAD': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 
                    'SCLFEZCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'SCLFEZMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'SCLFEZPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'IADSCLCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'IADSCLMEL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'IADSCLPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'IADSCLFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 
                    'IADCDGSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 'IADCDGMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'IADCDGPEK': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 'IADCDGFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 
                    'IADMELSCL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'IADMELCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'IADMELPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'IADMELFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'IADPEKSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'IADPEKCDG': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 'IADPEKMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'IADPEKFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'IADFEZSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'IADFEZCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'IADFEZMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'IADFEZPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'CDGSCLIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 
                    'CDGSCLMEL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'CDGSCLPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'CDGSCLFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 
                    'CDGIADSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 'CDGIADMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'CDGIADPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'CDGIADFEZ': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 
                    'CDGMELSCL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'CDGMELIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'CDGMELPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'CDGMELFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'CDGPEKSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'CDGPEKIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'CDGPEKMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'CDGPEKFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'CDGFEZSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'CDGFEZIAD': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 'CDGFEZMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'CDGFEZPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'MELSCLIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 
                    'MELSCLCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'MELSCLPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'MELSCLFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'MELIADSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'MELIADCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'MELIADPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 
                    'MELIADFEZ': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 'MELCDGSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'MELCDGIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'MELCDGPEK': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 
                    'MELCDGFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'MELPEKSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'MELPEKIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'MELPEKCDG': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 
                    'MELPEKFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'MELFEZSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'MELFEZIAD': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 'MELFEZCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 
                    'MELFEZPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'PEKSCLIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 
                    'PEKSCLCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'PEKSCLMEL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'PEKSCLFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'PEKIADSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'PEKIADCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'PEKIADMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'PEKIADFEZ': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 'PEKCDGSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'PEKCDGIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'PEKCDGMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'PEKCDGFEZ': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'PEKMELSCL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'PEKMELIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'PEKMELCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'PEKMELFEZ': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'PEKFEZSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'PEKFEZIAD': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8, 10, 12], 'PEKFEZCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 
                    'PEKFEZMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 'FEZSCLIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 
                    'FEZSCLCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'FEZSCLMEL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'FEZSCLPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'FEZIADSCL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'FEZIADCDG': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'FEZIADMEL': [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19], 
                    'FEZIADPEK': [2, 4, 6, 8, 10, 12, 1, 3, 5, 7, 9, 11], 'FEZCDGSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'FEZCDGIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'FEZCDGMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'FEZCDGPEK': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 'FEZMELSCL': [13, 14, 15, 16, 17, 18, 19, 13, 14, 15, 16, 17, 18, 19], 
                    'FEZMELIAD': [13, 14, 15, 16, 17, 18, 19, 2, 4, 6, 8, 10, 12], 'FEZMELCDG': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 
                    'FEZMELPEK': [13, 14, 15, 16, 17, 18, 19, 1, 3, 5, 7, 9, 11], 'FEZPEKSCL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19], 
                    'FEZPEKIAD': [1, 3, 5, 7, 9, 11, 2, 4, 6, 8, 10, 12], 'FEZPEKCDG': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7, 9, 11], 
                    'FEZPEKMEL': [1, 3, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19]}

## BDD Manage ##

# Primero revisamos las OC en estado ACEPTADAS


def check_oc_accepted():
    en_proceso = []
    token = get_token_oc()
    # Obtenemos los id de todas las oc de nuestra base de datos con estado "aceptadas"
    id_oc_list = see_accepted_oc()
    # Consultamos el estado de cada una
    for id_ in id_oc_list:
        estado = get_estado_oc(token, id_)
        estado_final = estado['estado']
        # Si esta finalizada, se debe elminiar de la BDD
        if estado_final == 'finalizada':
            remove_from_db_oc(id_)
            print(f"FINALIZADA {id_}")
        # Si sigue aceptada, es porque se está haciendo y no hay que pedirla denuevo
        elif estado_final == 'aceptada':
            en_proceso.append(estado['sku'])
            print(f"ACEPTADA {id_}")
        # Si está vencida se elimina de la base de datos
        elif estado_final == 'vencida':
            remove_from_db_oc(id_)
            print(f"VENCIDA {id_}")
        elif estado_final == 'cumplida':
            remove_from_db_oc(id_)
            print(f"CUMPLIDA {id_}")

    return en_proceso

# check_oc_accepted()
# Segundo revisamos las OC en estado CREADAS


def check_oc_created():
    en_proceso2 = []
    token = get_token_oc()
    # Obtenemos los id de todas las oc de nuestra base de datos con estado "creadas"
    id_oc_list = see_created_oc()
    # Consultamos el estado de cada una
    for id_ in id_oc_list:
        estado = get_estado_oc(token, id_)
        print(estado)
        estado_final = estado['estado']
        # Si es "ACEPTADA" se actualiza el estado de la BDD a "aceptada"
        if estado_final == "aceptada":
            update_to_accepted_oc(id_)
            en_proceso2.append(estado['sku'])
            print(f"ACEPTADA {id_}")
        # Si fue RECHAZADA se elimina de la base de datos
        elif estado_final == "rechazada":
            remove_from_db_oc(id_)
            print(f"RECHAZADA {id_}")
        # Si aún no fue aceptada, se deja igual
        elif estado_final == 'creada':
            en_proceso2.append(estado['sku'])
            print(f"CREADA {id_}")
        # Si está vencida se elimina de la base de datos
        elif estado_final == 'vencida':
            remove_from_db_oc(id_)
            print(f"VENCIDA {id_}")
        elif estado_final == 'cumplida':
            remove_from_db_oc(id_)
            print(f"CUMPLIDA {id_}")


    return en_proceso2

# check_oc_created()
####### Mantener stock materias primas externas ########

# Función que retorna un diccionario con las cantidades de materias primas que no producimos que mantenemos en inventario (store o buffer).


def check_external_products_store():
    bearer_token = get_token()
    external_products_stored = {}
    for product in external_products:
        external_products_stored[product] = 0

    for sku in external_products_stored.keys():
        buffer = get_sku_en_almacen(bearer_token, used_buffer, sku)
        store = get_sku_en_almacen(bearer_token, used_store, sku)
        result = buffer + store
        external_products_stored[sku] += len(result)

    return external_products_stored


def main(en_proceso_final, groups_and_stock):
    bearer_token = get_token_oc()
    token_oficial = get_token()
    external_products_stored = check_external_products_store()
    inventario_minimo = 3
    for product in external_products:
        # ¿Debo pedir de ese producto?
        if external_products_stored[product] < inventario_minimo and product not in en_proceso_final:
            # ¿Cuanto debo pedir?
            total_amount = inventario_minimo - \
                external_products_stored[product]
            # Agregado de si es vuelo con escala, entonces total_amount será 1
            if product in vuelos_escala_que_no_producimos:
                total_amount = 1
            list_groups_with_stock = whom_should_i_ask(
                product, total_amount, groups_and_stock)
            # Si ningún grupo tiene en stock del sku en cuestión, debemos elejir al azar a cualquiera de los productores de ese sku y pedir
            fecha_vencimiento_utc = get_fecha_vencimiento_UTC()
            fecha_vencimiento_timestamp = get_fecha_vencimiento_timestamp()
            if len(list_groups_with_stock) == 0:
                print(f"Ningún grupo tiene stock de {product}")
                productors = productors_groups[product]
                grupo_proveedor = random.choice(productors)

                while grupo_proveedor == 12:
                    grupo_proveedor = random.choice(productors)
                    if grupo_proveedor != 12:
                        break

                url = "http://clavo{}.ing.puc.cl".format(grupo_proveedor)

                print(f"Pediremos aleatoriamente al grupo {grupo_proveedor}")
                # Crea la orden de compra en la API
                try:
                    order = create_external_order(bearer_token=bearer_token, cliente="12", proveedor=str(
                        grupo_proveedor), sku=product, cantidad=total_amount, vencimiento=fecha_vencimiento_utc)
                    # Hacemos post al grupo que estamos pidiendo
                    print(order)
                    og_order = create_other_group_order(token_oficial,
                                                        url, order['id'], order['sku'], fecha_vencimiento_timestamp, order['cantidad'])
                    print(og_order)
                    # Agregamos la orden a la BDD External_OC
                    add_external_oc(id_oc_=order['id'], cliente_=order['cliente'], proveedor_=order['proveedor'], sku_=order['sku'], cantidad_=order['cantidad'], despachado_=order['despachado'],
                                    estado_=order['estado'], historial_=str(order['historial']), creada_=order['creada'], actualizada_=order['actualizada'], vencimiento_=order['vencimiento'])
            # Si uno o varios grupos tienen stock de ese sku, entonces se elejirá al azar cualquiera de estos
                except:
                    print("Me vine al PRIMER EXCEPT")
                    pass

            else:
                grupo_proveedor = random.choice(list_groups_with_stock)
                print(f"De los grupos que tienen stock elegimos aleatoriamente al grupo {grupo_proveedor}")
                num_grupo = re.findall(r'\d+', grupo_proveedor)

                while int(num_grupo[0]) == 12:
                    grupo_proveedor = random.choice(list_groups_with_stock)
                    num_grupo = re.findall(r'\d+', grupo_proveedor)
                    if int(num_grupo[0]) != 12:
                        break
                # Creamos orden de compra API
                try:
                    # Hacemos post al grupo que estamos pidiendo
                    order = create_external_order(bearer_token=bearer_token, cliente="12", proveedor=str(
                        num_grupo[0]), sku=product, cantidad=total_amount, vencimiento=fecha_vencimiento_utc)
                    print(order)
                    og_order = create_other_group_order(token_oficial,
                                                        grupo_proveedor, order['id'], order['sku'], fecha_vencimiento_timestamp, order['cantidad'])
                    print(og_order)
                    # Agregamos la orden a la BDD External_OC
                    add_external_oc(id_oc_=order['id'], cliente_=order['cliente'], proveedor_=order['proveedor'], sku_=order['sku'], cantidad_=order['cantidad'], despachado_=order['despachado'],
                                    estado_=order['estado'], historial_=str(order['historial']), creada_=order['creada'], actualizada_=order['actualizada'], vencimiento_=order['vencimiento'])
                except:
                    print("Me vine al SEGUNDO EXCEPT")
                    pass


def get_fecha_vencimiento_UTC():
    # Sacamos el tiempo de ahora en UTC
    time_now = datetime.datetime.now(timezone.utc)
    # Definimos un delta
    delta = datetime.timedelta(hours=10)
    # Le sumamos delta a time_now
    time_plus_delta = time_now + delta
    # Dejamos la fecha en formato UTC con ISO (Con la Z alfinal)
    fecha_vencimiento = time_plus_delta.isoformat().replace("+00:00", "Z")

    return fecha_vencimiento


def get_fecha_vencimiento_timestamp():
    time = datetime.datetime.now() + datetime.timedelta(hours=10)
    new_time = time.timestamp()

    return new_time

# print(get_fecha_vencimiento_timestamp())
# Funcion que retora una lista con grupos que producen el sku actual, y que tienen en su inventario actual un número >= de lo que necesitamos.


def whom_should_i_ask(sku, amount, groups_and_stock):
    possible_groups = []
    for grupo in url_grupos:
        # Verificar que el grupo lo produce
        num_grupo = re.findall(r'\d+', grupo)
        productors = productors_groups[sku]
        if int(num_grupo[0]) in productors:
            # print(f"El grupo {int(num_grupo[0])} si produce el sku {sku}")
            stock_grupo_actual = groups_and_stock[num_grupo[0]]
            for product in stock_grupo_actual:
                if "quantity" in product.keys():
                    if product["sku"] == sku and product["quantity"] >= amount:
                        possible_groups.append(grupo)
                else:
                    if product["sku"] == sku and product["total"] >= amount:
                        possible_groups.append(grupo)
                    # print(f"he agregado al grupo {grupo} para el sku {sku}")
        else:
            # print(f"El grupo {int(num_grupo[0])} NO produce del sku {sku}")
            pass

    return possible_groups

# Funcion que recibe un sku y una cantidad a pedir. Devuelve el la cantidad "loteada" que se debe pedir.


def check_lote(sku, number):
    lote = all_lotes[sku]
    if lote == 2:
        if number % 2 != 0 or number == 1:
            number += 1
        return number
    elif lote == 4:
        return 4
    elif lote == 1:
        return number

# Funcion que "saca una foto" del inventario actual de los grupos y retorna un dicc con llave -> num de grupo y valor -> lista de diccionarios con sku y total
# IMPORTANTE: SE DEMORA, POR LO TANTO LA IDEA ES LLAMARLA UNA VEZ Y DEJAR UNA VARIABLE EXTERNA FIJADA


def groups_actual_stock():
    groups_and_stock = {}
    for grupo in url_grupos:
        lista_vacia = []
        num_grupo = re.findall(r'\d+', grupo)
        try:
            # print(f"Viendo grupo {num_grupo}")
            external_stock_products = get_external_stocks(grupo)
            if isinstance(external_stock_products, list):
                # print("your object is a list !")
                groups_and_stock[num_grupo[0]] = external_stock_products
            else:
                groups_and_stock[num_grupo[0]] = lista_vacia
        except:
            # print(f"Viendo grupo vacio {num_grupo}")
            groups_and_stock[num_grupo[0]] = lista_vacia

    return groups_and_stock


# FLUJO #
def start_ep():
    groups_and_stock = groups_actual_stock()
    en_proceso = check_oc_accepted()
    en_proceso2 = check_oc_created()
    en_proceso_final = en_proceso + en_proceso2
    main(en_proceso_final, groups_and_stock)




# start_ep()
######## Pedir a otros grupos #########

# bearer_token_oc = get_token_oc()
# bearer_token = get_token()

# fecha_utc = get_fecha_vencimiento_UTC()
# fecha_time = get_fecha_vencimiento_timestamp()

# order = create_external_order(bearer_token=bearer_token_oc, cliente="12",
#                               proveedor="7", sku="FRCREW", cantidad=1, vencimiento=fecha_utc)

# print(order)

# og_order = create_other_group_order(
#     bearer_token, "http://clavo10.ing.puc.cl", order['id'], 'FRCREW', fecha_time, 1)

# print(og_order)
######## Enviar a otros grupos #########


