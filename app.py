from flask import jsonify, make_response, request, render_template
from api_calls import used_store, used_buffer, get_token, get_almacenes, get_sku_con_stock
from app_setup import app
from scale_flights import add_b2b
from script import run_all
from apscheduler.schedulers.background import BackgroundScheduler

from app_setup import (
    app,
    Orden_Compra
)


def sensor():
    run_all()


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor, 'interval', minutes=20)
sched.start()


@app.route("/")
def home():
    return make_response(jsonify({"mensaje": "Home Page"}), 200)


@app.route("/dashboard_stocks")
def dashboard_stocks():
    token = get_token()
    almacenes = get_almacenes(token)
    store = get_sku_con_stock(token, used_store)
    buffer = get_sku_con_stock(token, used_buffer)
    total_store = almacenes[0]["totalSpace"]
    bussy_store = almacenes[0]["usedSpace"]
    total_buffer = almacenes[1]["totalSpace"]
    bussy_buffer = almacenes[1]["usedSpace"]
    pct_store = str((bussy_store / total_store) * 100) + "%"
    pct_buffer = str((bussy_buffer / total_buffer) * 100) + "%"
    return render_template('stocks.html', ids=[used_store, used_buffer], totales=[total_store, total_buffer], usado=[bussy_store, bussy_buffer],
                           porcentajes=[pct_store, pct_buffer], stocks=[store, buffer])


@app.route("/dashboard_orders")
def dashboard_orders():
    all = []
    for x in Orden_Compra.query.all():
        info = []
        id = x.id_oc
        info.append(id)
        cliente = x.client
        info.append(cliente)
        if (cliente == "20"):
            tipo = "ftp"
        else:
            tipo = "b2b"
        info.append(tipo)
        sku = x.sku
        info.append(sku)
        cantidad = x.quantity
        info.append(str(cantidad))
        estado = x.status
        info.append(estado)
        fecha_creacion = x.time_now
        info.append(fecha_creacion)
        fecha_vencimiento = x.delivery_date
        info.append(fecha_vencimiento)
        all.append(info)

    return render_template('orders.html', stocks=all)


@app.route("/stocks")
def stocks():
    token = get_token()
    stock = get_sku_con_stock(token, used_store)

    return make_response(jsonify(stock), 200)


@app.route("/ordenes-compra/<id_>", methods=["POST"])
def order_received(id_):
    content_type = request.headers.get('Content-Type')
    # Obtenemos el body del request
    if (content_type == 'application/json'):
        json_request = request.json
        received_status = add_b2b(id_, json_request)

        if received_status[0]:

            return make_response(jsonify(received_status[1]), 201)
        else:
            return make_response(jsonify({"mensaje": received_status[1]}), 400)


@app.route("/ordenes-compra/<id_>", methods=["PATCH"])
def our_order_status(id_):
    # Nos avisan si la orden de compra que solicitamos comprar es aceptada o rechazada
    string = "Order " + str(id_) + " Update Received"
    return make_response(jsonify({'Message': string}), 200)


if __name__ == "__main__":
    app.run()
