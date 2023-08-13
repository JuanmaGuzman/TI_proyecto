from api_calls import (
    get_sku_con_stock,
    get_sku_en_almacen,
    get_token,
    used_store,
    get_token_oc,
    update_oc,
    notificate_other_group,
    api_dispach,
    make_order,
    get_estado_oc,
    used_link,
    used_credentials
)

from ftp_oc import get_ftp
from bdd_manage import (
    oc_reception_add,
    current_orders,
    orders_by_sku,
    to_notificate,
    oc_delete,
    update_status,
    bd_delete_expired_orders
)

import datetime

from zeep import Client
from zeep.wsse.username import UsernameToken

url = used_link + '/soap/billing?wsdl'
wsse_auth = UsernameToken(used_credentials[0], used_credentials[1])
client = Client(url, wsse=wsse_auth)

our_mps_lotes = {"MRBOE737":1,"MRAB320":1, "MRAB330":1, "MRAB340":1,
 "MRBOE747":1, "MRNOV":2, "MRINT":2, "MREXP":2, "MROFC":2, "MRCPT":2, "MRCMD":2,
 "USBOE737":1, "USAB320":1, "USAB330":1, "USAB340":1, "USBOE747":1, "USNOV":2,
 "USINT":2, "USEXP":2, "USOFC":2, "USCPT":2, "USCMD":2, "MRCREW":12, "USCREW":12,
 "MRJETA1":6, "USJETA1":8}


def cantidad_a_pedir(lote, cantidad_stockeada, stock_minimo):
    falta = stock_minimo - cantidad_stockeada
    pedir = 0
    if lote > falta:
        pedir = lote
    else:
        while pedir < falta:
            pedir += lote
    return pedir
        

def refill_our_mp(our_mps_lotes):
    token = get_token()
    current_stocks = [(x["sku"], x["quantity"]) for x in get_sku_con_stock(token, used_store)]
    dict_stocks = {}
    for stocked_mp in current_stocks:
        dict_stocks[stocked_mp[0]] = stocked_mp[1]
    
    for mp in our_mps_lotes.keys():
        if mp not in dict_stocks.keys():
            ### Pedir 4 o mas segun el lote
            print(f"{mp} is empty")
            cantidad_pedido = cantidad_a_pedir(our_mps_lotes[mp], 0, 4)
            make_order(token, mp, cantidad_pedido)
        elif mp in dict_stocks.keys() and dict_stocks[mp] < 4:
            ### pedir para llega a 4 o mas segun el lote
            print(f"{mp} is understocked")
            cantidad_pedido = cantidad_a_pedir(our_mps_lotes[mp], dict_stocks[mp], 4)
            make_order(token, mp, cantidad_pedido)
            pass
        elif mp in dict_stocks.keys() and dict_stocks[mp] >=4:
            print(f"{mp} already stocked")
            pass


def check_current_asks(sku):
    query_searched = orders_by_sku(sku)
    sku_count = 0
    for item in query_searched:
        sku_count += item.quantity
    return sku_count


def add_b2b(id_, json_):
    time_now = datetime.datetime.now(datetime.timezone.utc)
    time_now2 = time_now.isoformat().replace("+00:00", "Z")
    token = get_token()
    store = get_sku_con_stock(token, used_store)
    store_skus = {}
    for item in store:
        sku = item["sku"]
        store_skus[sku] = item["quantity"]

    if json_["sku"] in store_skus.keys():
        sku = json_["sku"]
        if json_["cantidad"] <= store_skus[json_["sku"]]:
            try:
                # Aceptamos una Orden
                received = oc_reception_add(id_, json_["sku"], json_["cliente"], json_["fechaEntrega"], json_[
                                            "cantidad"], json_["urlNotificacion"], "Notificar Aceptada", time_now2)
                if received[0]:
                    return (True, {"id": id_, "sku": json_["sku"], "cliente": json_["cliente"],
                                   "fechaEntrega": json_["fechaEntrega"], "cantidad": json_["cantidad"], "urlNotificacion": json_["urlNotificacion"], "estado": "recibida"})
                return (False, {"error":"Duplicated Order"})

            except:
                # Parametros invalidos
                return (False, {"error":"Wrong values"})

        else:
            # No tenemos suficiente, rechazamos
            received = oc_reception_add(id_, json_["sku"], json_["cliente"], json_["fechaEntrega"], json_[
                                        "cantidad"], json_["urlNotificacion"], "Notificar Rechazo", time_now2)
            return (True, {"id": id_, "sku": json_["sku"], "cliente": json_["cliente"], "fechaEntrega": json_["fechaEntrega"], 
            "cantidad": json_["cantidad"], "urlNotificacion": json_["urlNotificacion"], "estado": "recibida"})

    else:
        try:
            # No tenemos ese sku, rechazamos
            received = oc_reception_add(id_, json_["sku"], json_["cliente"], json_["fechaEntrega"], json_[
                                        "cantidad"], json_["urlNotificacion"], "Notificar Rechazo", time_now2)
            return (True, {"id": id_, "sku": json_["sku"], "cliente": json_["cliente"], "fechaEntrega": json_["fechaEntrega"], 
            "cantidad": json_["cantidad"], "urlNotificacion": json_["urlNotificacion"], "estado": "recibida"})
        except:
                # Parametros invalidos
                return (False, {"error":"Wrong values"})


def notificar_aceptadas():
    # Revisar en la BDD los que estan en estado Notificar Aceptada
    for order in to_notificate(0):
        try:
            print(order)
            # Enviar llamado a la api de aceptar la orden
            print(get_estado_oc(get_token_oc(), order.id_oc))
            print(update_oc(get_token_oc(), order.id_oc, "aceptada"))
            # Enviar Patch al otro grupo de que la orden fue Aceptada
            notificate_other_group(order.notification_url, order.id_oc, "aceptada")
            # Cambiar el estado a aceptada
            update_status(order.id_oc, "Aceptada")
        except:
            print("problema con la orden")


def notificar_rechazos():
    # Revisar en la BDD los que estan en estado Notificar Rechazo
        for order in to_notificate(1):
            try:
                # Enviar llamado a la api de rechazar la orden
                print(update_oc(get_token_oc(), order.id_oc, "rechazada"))
                # Enviar patch al otro grupo de que la orden fue Rechazada
                print(notificate_other_group(order.notification_url,
                                    order.id_oc, "rechazada"))
                # Eliminar la orden de la BDD
                oc_delete(order.id_oc)
            except:
                print("problema con la orden")


def add_ftps():
    ftps = get_ftp()
    received_ftps = [y for y in ftps if y["cantidad"] < 4]
    for ftp_ in received_ftps:
        time_now = datetime.datetime.now(datetime.timezone.utc)
        time_now2 = time_now.isoformat().replace("+00:00", "Z")
        # Si tenemos menos de 3 de ese vuelo pendiente aceptamos la orden
        if check_current_asks(ftp_["sku"]) < 4:
            reception_status = oc_reception_add(ftp_["id"], ftp_["sku"], ftp_["cliente"], ftp_[
                                                "vencimiento"], ftp_["cantidad"], "-", "Aceptada", time_now2)
            if reception_status[0]:
                update_oc(get_token_oc(), ftp_["id"], "aceptada")


def review_orders():
    token = get_token()
    for order in current_orders():
        try:
            print(order.sku, order.quantity)
            skus_en_stock = get_sku_en_almacen(get_token(), used_store, order.sku)
            if len(skus_en_stock) >= order.quantity:
                for x in range(order.quantity):
                    # despachamos.
                    dispatch_response = api_dispach(token, skus_en_stock[x]["_id"], order.id_oc)
                    print(f"dispatch response: {dispatch_response}")
                    # creamos factura.
                    einvoice_response = client.service.emitInvoice(order_id=order.id_oc)
                    print(f"emitInvoice response: {einvoice_response}")
                oc_delete(order.id_oc)

            elif len(skus_en_stock) < order.quantity and len(order.sku) > 7 and order.status == "Aceptada":
                skus_direct_flight1 = get_sku_en_almacen(
                    get_token(), used_store, order.sku[0:6])
                skus_direct_flight2 = get_sku_en_almacen(
                    get_token(), used_store, order.sku[3:9])
                if len(skus_direct_flight1) >= int(order.quantity) and len(skus_direct_flight2) >= int(order.quantity):
                    # print("---------- HACIENDO ORDEN -----------")
                    make_order(token, order.sku, order.quantity)
                    # print("---------- ORDEN ENDED -----------")
                    update_status(order.id_oc, "Enviado")
        except:
            print("error revisando la orden")


def pay_invoices():
    pending_invoice = client.service.getInvoices(status="pending", side="client")
    print('payInvoice response:', pending_invoice)
    if pending_invoice == []:
        print("Without pending invoices")
    else:
        print("With pending invoices")
        for i in pending_invoice:
            pending_invoice_id = i["id"]
            pay_invoice = client.service.payInvoice(invoice_id=pending_invoice_id)
            print('payInvoice response:', pay_invoice)


def run_scales():
    bd_delete_expired_orders()
    print("ordenes vencidas eliminadas")
    notificar_rechazos()
    print("rechazos notificados")
    notificar_aceptadas()
    print("ordenes aceptadas notificadas")
    review_orders()
    print("current order revisadas")
    add_ftps()
    print("nuevas ftps agregadas")
    try:
        pay_invoices()
        print("invoices pendientes pagados")
    except:
        print("error en pay_invoices")
    # refill_our_mp(our_mps_lotes)
    print("materias primas refilleadas")

# run_scales()
