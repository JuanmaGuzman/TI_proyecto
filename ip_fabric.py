from app_setup import app, To_Do_Orders, In_Production
import random
from api_calls import used_store, used_buffer, get_token, get_sku_en_almacen, make_order, move_product, send_product
from bdd_manage import orders_to_do, drop_to_do, order_add, bd_producting, production_ready, reset_and_creat_db
import pandas as pd

all_materials = ['FRJETA1', 'FRCREW', 'FRBOE747', 'FRCMD', 'FRAB330',
                 'FROFC', 'AUJETA1', 'AUCREW', 'AUAB340', 'AUCPT', 'AUBOE747', 'AUCMD']

all_direct_flights = ['CDGMEL', 'CDGPEK', 'CDGSCL',
                      'CDGIAD', 'MELPEK', 'MELCDG', 'MELIAD', 'MELSCL']

all_scale_flights = ['CDGMELPEK', 'CDGMELIAD',
                     'CDGMELSCL', 'MELCDGPEK', 'MELCDGSCL', 'MELCDGIAD']


def read_csv():
    products_dict = {}
    df_productos = pd.read_csv("Static_Data/productos.csv", delimiter=",")
    product_list = df_productos.SKU.values.tolist()
    lote_list = df_productos.Lote.values.tolist()
    groups_list = df_productos.Grupos.values.tolist()
    for x in range(0, len(product_list)):
        products_dict[product_list[x]] = {"lote": int(
            lote_list[x]), "grupos": groups_list[x]}

    return products_dict


def production_formulas():
    production_formulass = pd.read_csv(
        "Static_Data/formulas.csv", delimiter=";")
    formulas_dict = {}
    for sku in all_direct_flights:
        paquete = {}
        for ind in production_formulass.index:
            if sku == production_formulass["Producto"][ind]:
                ingrediente = production_formulass["Ingrediente"][ind]
                quantity = production_formulass["Cantidad"][ind]
                paquete[ingrediente] = quantity

        formulas_dict[sku] = paquete

    return formulas_dict


def check_df_store():
    bearer_token = get_token()
    direct_flights_stored = {}
    direct_flights_to_expire = {}
    for df in all_direct_flights:
        direct_flights_stored[df] = 0
        direct_flights_to_expire[df] = 0

    for sku in direct_flights_stored.keys():
        store = get_sku_en_almacen(bearer_token, used_store, sku)
        result = store
        direct_flights_stored[sku] += len(result)

    return direct_flights_stored


def check_df_incoming(direct_flights):
    with app.app_context():
        for sku in direct_flights.keys():
            incoming_quantity = [
                x.quantity for x in To_Do_Orders.query.filter_by(sku=sku).all()]
            total_quantity = 0
            for quantity in incoming_quantity:
                total_quantity += quantity

            direct_flights[sku] += total_quantity

        return direct_flights


def check_df_created(direct_flights):
    with app.app_context():
        for sku in direct_flights.keys():
            incoming_quantity = [
                x.quantity for x in In_Production.query.filter_by(sku=sku).all()]
            total_quantity = 0
            for quantity in incoming_quantity:
                total_quantity += quantity

            direct_flights[sku] += total_quantity
            production_ready(sku)

    return direct_flights


def df_order():
    direct_flights_stored = check_df_store()
    # print(f"check_df_store: {direct_flights_stored}")
    direct_flights_stored = check_df_incoming(direct_flights_stored)
    # print(f"check_df_incoming: {direct_flights_stored}")
    direct_flights_stored = check_df_created(direct_flights_stored)
    # print(f"check_df_created: {direct_flights_stored}")

    # print(f"Direct flights stored: {direct_flights_stored}")

    return direct_flights_stored


def products_order_one():
    order_resume = {}
    direct_flights_stored = df_order()
    direct_flights_order = {}
    direct_flights_inventory = {}

    for df in all_direct_flights:
        direct_flights_inventory[df] = 8

    for sku in direct_flights_stored.keys():
        if direct_flights_inventory[sku] > direct_flights_stored[sku]:
            dif = direct_flights_inventory[sku] - direct_flights_stored[sku]
            if dif <= 4:
                direct_flights_order[sku] = dif
                order_resume[sku] = dif
            else:
                direct_flights_order[sku] = 4
                order_resume[sku] = 4

        else:
            direct_flights_order[sku] = 0
            order_resume[sku] = 0

    # print(f"Direct flights order: {direct_flights_order}")

    total = 0
    for quantity in order_resume.values():
        total += quantity

    # print(f"We need {total} direct flights to keep the inventory:")
    # print(f"order resume: {order_resume}")

    return order_resume


def products_order_two():
    formula = production_formulas()
    order_resume = products_order_one()
    products_needed = {}

    for p in all_materials:
        products_needed[p] = 0

    for sku, quantity in order_resume.items():
        dic = formula[sku]
        for k, v in dic.items():
            product = k
            order = v * quantity
            products_needed[product] += order

    # print(f"The raw materials that we need to order to maintain the minimum inventory of direct and scale flights that we need are: {products_needed}")

    return products_needed, order_resume


def products_order_three():
    bearer_token = get_token()
    total = 0
    products_needed, order_resume = products_order_two()

    for sku, quantity in order_resume.items():
        if quantity != 0:
            order_add(sku, quantity, 0)

    # print(f"Products needed: {products_needed}")
    for sku, quantity in products_needed.items():
        lote = read_csv()[sku]["lote"]

        store = get_sku_en_almacen(bearer_token, used_store, sku)
        actual_quantity = len(store)

        if quantity >= actual_quantity:
            quantity = quantity - actual_quantity
            if quantity <= lote and quantity != 0:
                total += lote
                make_order(bearer_token, sku, int(lote))

            elif quantity > lote:
                if quantity % 2 != 0:
                    total += quantity + 1
                    make_order(bearer_token, sku, int(quantity + 1))
                else:
                    total += quantity
                    make_order(bearer_token, sku, int(quantity))

            else:
                pass

    # print(f"Total products ordered: {total}")
    return True


def df_production(to_do_list):
    bearer_token = get_token()
    formularium = production_formulas()

    for tuple in to_do_list:
        sku = tuple[0]
        total_amount = tuple[1]

        if sku in list(formularium.keys()):
            # print(f"Send to produce: {total_amount} {sku}")
            make_order(bearer_token, sku, total_amount)
            bd_producting(sku, total_amount)

    return True


def clear_up_warehouse():
    bearer_token = get_token()
    all = read_csv()
    for sku in all:
        for p in get_sku_en_almacen(bearer_token, used_store, sku):
            pid = p["_id"]
            move_product(bearer_token, pid, used_buffer)

    return True


def clean_all():
    bearer_token = get_token()
    products_dict = read_csv()

    for sku in products_dict:
        n = random.randint(1, 14)
        if n == 12:
            n = 14
        for product in get_sku_en_almacen(bearer_token, used_buffer, sku):
            response = send_product(bearer_token, product["_id"], n)
            # print(response)

        for product in get_sku_en_almacen(bearer_token, used_store, sku):
            response = send_product(bearer_token, product["_id"], n)
            # print(response)


def start_ip():
    # Esperar 15 min entre iteraciones.
    to_do_list = orders_to_do()
    # print("Direct flights production.")
    df_production(to_do_list)
    drop_to_do()
    # print("Start order generation.")
    products_order_three()

    return True
