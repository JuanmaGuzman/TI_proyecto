import requests

############################## LINKS #################################################
dev_link = "https://dev.api-bodega.2022-2.tallerdeintegracion.cl"
prod_link = "https://prod.api-bodega.2022-2.tallerdeintegracion.cl"
############################# ALMACENES ID ##########################################
dev_store = "633eee43ada98a78416b8924"
dev_buffer = "633eee43ada98a78416b8925"
prod_store = "634d4d0e3fde87291f8aafa1"
prod_buffer = "634d4d0e3fde87291f8aafa2"
################################ TOKEN ###############################################
dev_token = 'a9nbv7SkwFSgtWqQ6Qq4'
prod_token = "0;-Ab]4du6PNM&t9Wd6A}LW7S*pK(a" + "%" + "f"
################################ CREDENTIALS #########################################
prod_credentials = ("grupo12_produccion", "w7Pjkgy2oyMrSFI2wp")
dev_credentials = ("grupo12_desarrollo", "hYxJTi7kMj5J8iKfiF")
####################### USED LINKS #################################
used_credentials = prod_credentials
used_link = prod_link
used_store = prod_store
used_buffer = prod_buffer
used_token = prod_token


# Obtiene el token de autorizacion
def get_token():
    url_token = "{}/warehouse/auth".format(used_link)
    data_sent = {"group": 12, "secret": used_token}
    response = requests.post(url=url_token, json=data_sent)
    return response.json()["token"]


def get_token_oc():
    url_token = "{}/ordenes-compra/autenticar".format(used_link)
    data_sent = {"group": 12, "secret": used_token}
    response = requests.post(url=url_token, json=data_sent)
    return response.json()["token"]


# Hace una orden de producto sku=sku y cantidad=quantity
def make_order(bearer_token, sku, quantity):
    url_token = "{}/warehouse/products".format(used_link)
    data_sent = {"sku": sku, "quantity": quantity}
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.post(url=url_token, json=data_sent, headers=headers_)
    return response.json()


# Envía el producto de id=product_id al grupo numero group_number
def send_product(bearer_token, product_id, group_number):
    url_token = "{}/warehouse/products/{}/group".format(used_link, product_id)
    data_sent = {"group": group_number}
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.post(url=url_token, json=data_sent, headers=headers_)
    return response.json()


# Envía el producto de id=product_id a la bodega de id=bodega_destino
def move_product(bearer_token, product_id, bodega_destino):
    url_token = "{}/warehouse/products/{}".format(used_link, product_id)
    data_sent = {"store": bodega_destino}
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.patch(url=url_token, json=data_sent, headers=headers_)
    return response.json()


# muestra la info actual de los almacenes
def get_almacenes(bearer_token):
    url_almacenes = "{}/warehouse/stores".format(used_link)
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.get(url=url_almacenes, headers=headers_)
    return response.json()


# Muestra los productos de sku=sku en el almacen de id=id_almacen
def get_sku_en_almacen(bearer_token, id_almacen, sku):
    url_stock_sku = "{}/warehouse/stores/{}/products?sku={}&limit=199".format(
        used_link, id_almacen, sku)
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.get(url=url_stock_sku, headers=headers_)
    return response.json()

# Muestra aquellos skus que tienen stock en el almacen id=id_almacen
def get_sku_con_stock(bearer_token, id_almacen):
    url_stock_sku = "{}/warehouse/stores/{}/inventory".format(
        used_link, id_almacen)
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.get(url=url_stock_sku, headers=headers_)
    return response.json()


def get_external_stocks(url_grupo):
    url = "{}/stocks".format(url_grupo)
    response = requests.get(url=url)
    return response.json()


def create_external_order(bearer_token, cliente, proveedor, sku, cantidad, vencimiento):
    url = "{}/ordenes-compra/ordenes".format(used_link)
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    data_sent = {"cliente": cliente, "proveedor": proveedor,
                 "sku": sku, "cantidad": cantidad, "vencimiento": vencimiento}
    response = requests.post(url=url, json=data_sent,
                             headers=headers_, timeout=5)
    return response.json()


def get_estado_oc(bearer_token, id_orden):
    url = "{}/ordenes-compra/ordenes/{}".format(used_link, id_orden)
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.get(url=url, headers=headers_)
    return response.json()
    

def api_dispach(bearer_token, productId, orderId):
    url_token = "{}/warehouse/dispatch".format(used_link)
    data_sent = {"productId": productId, "orderId": orderId}
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.post(url=url_token, json=data_sent, headers=headers_)
    if response.status_code == 204:
        return {"message": "success"}
    return response.json()


def update_oc(bearer_token, id, status):
    url_order = "{}/ordenes-compra/ordenes/{}/{}".format(
        used_link, id, "estado")
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    data_sent = {"estado": status}
    response = requests.post(url=url_order, json=data_sent,
                             headers=headers_, timeout=5)
    if response.status_code == 204:
        return {"message": "success"}

    return response.json()


def notificate_other_group(url_group, order_id, status):
    data_sent = {"estado": status}
    if "/ordenes-compra/" in url_group:
        url_ = url_group
    else:
        url_ = url_group + "/ordenes-compra/" + order_id
    response = requests.patch(url=url_, json=data_sent)
    return response.json()


def create_other_group_order(bearer_token, url_group, order_id, sku, fecha_entrega, quantity):
    our_url = "http://clavo12.ing.puc.cl" + "/ordenes-compra/" + order_id
    headers_ = {"Authorization": "Bearer {}".format(bearer_token)}
    data_sent = {"cliente": "12", "sku": sku, "fechaEntrega": str(fecha_entrega),
                 "cantidad": quantity, "urlNotificacion": our_url}
    url_ = url_group + "/ordenes-compra/" + order_id
    response = requests.post(url=url_, json=data_sent, headers=headers_)
    try:
        return response.json()
    except:
        pass

# print(get_almacenes(get_token()))