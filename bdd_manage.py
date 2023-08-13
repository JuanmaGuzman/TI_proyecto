from app_setup import (
    db,
    app,
    Orden_Compra,
    To_Do_Orders,
    In_Production,
    External_OC
)
from datetime import datetime, timezone
from metomi.isodatetime.parsers import TimePointParser


def reset_and_creat_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
    return True

#reset_and_creat_db()


def oc_reception_add(id_oc, sku, client, delivery_date, quantity, notification_url, status, time_now):
    print("agregado")
    with app.app_context():
        to_do_list = [(x)
                      for x in Orden_Compra.query.filter_by(id_oc=id_oc).all()]
        if len(to_do_list) == 0:
            # print("New oc added to the DB.")
            OC = Orden_Compra(id_oc=id_oc, sku=sku, client=client, delivery_date=delivery_date,
                              quantity=quantity, notification_url=notification_url, status=status, time_now=time_now)
            db.session.add(OC)
            db.session.commit()
            return (True, "Success")

        else:
            # print("Duplicated oc.")
            return (False, "Duplicated")


# oc_reception_add("1", "sku", "client", "delivery_date", 1,
#                  "notification_url", "status", "time_now")


def to_notificate(value):
    with app.app_context():
        if value == 0:
            to_accept = [(x) for x in Orden_Compra.query.filter_by(
                status="Notificar Aceptada").all()]
        elif value == 1:
            to_accept = [(x) for x in Orden_Compra.query.filter_by(
                status="Notificar Rechazo").all()]
        return to_accept


def current_orders():
    with app.app_context():
        return Orden_Compra.query.all()


def update_status(id_, status):
    with app.app_context():
        item_to_update = Orden_Compra.query.filter_by(id_oc=id_).first()
        item_to_update.status = status
        db.session.commit()


def orders_by_sku(sku):
    with app.app_context():
        return Orden_Compra.query.filter_by(sku=sku).all()


def oc_delete(id_oc):
    with app.app_context():
        Orden_Compra.query.filter_by(id_oc=id_oc).delete()
        db.session.commit()
        return True


def orders_to_do():
    with app.app_context():
        to_do_list = [(x.sku, x.quantity)
                      for x in To_Do_Orders.query.filter_by(moment=0).all()]

        return to_do_list


def drop_to_do():
    with app.app_context():
        To_Do_Orders.query.filter_by(moment=0).delete()
        db.session.commit()
        return True


def order_add(sku_, cantidad_, momento_):
    with app.app_context():
        order = To_Do_Orders(sku=sku_, quantity=cantidad_, moment=momento_)
        db.session.add(order)
        db.session.commit()
        return True


def bd_producting(sku_, quantity_):
    with app.app_context():
        new = In_Production(sku=sku_, quantity=quantity_)
        db.session.add(new)
        db.session.commit()
        return True


def production_ready(sku_):
    with app.app_context():
        In_Production.query.filter_by(sku=sku_).delete()
        db.session.commit()
        return True


def add_external_oc(id_oc_, cliente_, proveedor_, sku_, cantidad_, despachado_, estado_, historial_, creada_, actualizada_, vencimiento_):
    with app.app_context():
        new = External_OC(id_oc=id_oc_, cliente=cliente_, proveedor=proveedor_, sku=sku_, cantidad=cantidad_, despachado=despachado_,
                          estado=estado_, historial=historial_, creada=creada_, actualizada=actualizada_, vencimiento=vencimiento_)
        db.session.add(new)
        db.session.commit()
        return True


def see_external_oc():
    with app.app_context():
        external_oc_list = [(x.id_oc, x.cliente, x.proveedor, x.sku, x.cantidad, x.despachado, x.estado, x.historial, x.creada, x.actualizada, x.vencimiento)
                            for x in External_OC.query.all()]

        return external_oc_list


def see_accepted_oc():
    with app.app_context():
        accepted_oc_list = [(x.id_oc)
                            for x in External_OC.query.filter_by(estado="aceptada").all()]
        return accepted_oc_list


def see_created_oc():
    with app.app_context():
        created_oc_list = [(x.id_oc)
                           for x in External_OC.query.filter_by(estado="creada").all()]
        return created_oc_list


def remove_from_db_oc(id_):
    with app.app_context():
        External_OC.query.filter_by(id_oc=id_).delete()
        db.session.commit()
        return True


def update_to_accepted_oc(id_):
    with app.app_context():
        External_OC.query.filter_by(id_oc=id_).update({'estado': 'aceptada'})
        db.session.commit()
        return True


def bd_delete_expired_orders():
    time_now = datetime.now(timezone.utc)
    time_now = time_now.isoformat().replace("+00:00", "Z")
    time_now = TimePointParser().parse(time_now)
    with app.app_context():
        query = Orden_Compra.query.all()
        for x in query:
            id_oc, expire_date = "1", "1667840042000"
            if expire_date[0:5] == "2022-":
                expire_date = TimePointParser().parse(expire_date)

            else:
                expire_date = expire_date[0:10]
                expire_date = datetime.utcfromtimestamp(int(expire_date))
                expire_date = expire_date.isoformat().replace("+00:00", "Z")
                expire_date = TimePointParser().parse(expire_date)

            dif = expire_date - time_now
            if dif.days <= 0 and dif.hours <= 0 and dif.minutes <= 0:
                Orden_Compra.query.filter_by(id_oc=id_oc).delete()
                db.session.commit()
