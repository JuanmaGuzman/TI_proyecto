from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey123"
# Tienen que descomentar esta linea y comentar la de abajo para trabajar en local
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://grupo12:grupo12@localhost:5432/proyecto"
db = SQLAlchemy(app)


class Orden_Compra(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    id_oc = db.Column(db.Text(), unique=True)
    sku = db.Column(db.Integer())
    client = db.Column(db.Text())
    time_now = db.Column(db.Text())
    delivery_date = db.Column(db.Text())
    quantity = db.Column(db.Integer())
    notification_url = db.Column(db.Text())
    status = db.Column(db.Text())


class To_Do_Orders(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    sku = db.Column(db.Text())
    quantity = db.Column(db.Integer())
    moment = db.Column(db.Integer())


class In_Production(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    sku = db.Column(db.Text())
    quantity = db.Column(db.Integer())


class External_OC(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    id_oc = db.Column(db.Text(), unique=True)
    cliente = db.Column(db.Text())
    proveedor = db.Column(db.Text())
    sku = db.Column(db.Text())
    cantidad = db.Column(db.Integer())
    despachado = db.Column(db.Integer())
    estado = db.Column(db.Text())
    historial = db.Column(db.Text())
    creada = db.Column(db.Text())
    actualizada = db.Column(db.Text())
    vencimiento = db.Column(db.Text())
