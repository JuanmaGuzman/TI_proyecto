import paramiko
import requests
import datetime
from dateutil import parser
from api_calls import used_link, used_token, used_credentials


all_materials = ['FRJETA1', 'FRCREW', 'FRBOE747', 'FRCMD', 'FRAB330',
                 'FROFC', 'AUJETA1', 'AUCREW', 'AUAB340', 'AUCPT', 'AUBOE747', 'AUCMD']

all_direct_flights = ['CDGMEL', 'CDGPEK', 'CDGSCL',
                      'CDGIAD', 'MELPEK', 'MELCDG', 'MELIAD', 'MELSCL']

all_scale_flights = ['CDGMELPEK', 'CDGMELIAD',
                     'CDGMELSCL', 'MELCDGPEK', 'MELCDGSCL', 'MELCDGIAD']

everything = all_materials + all_direct_flights + all_direct_flights


def get_token():
    url_token = "{}/ordenes-compra/autenticar".format(used_link)
    data_sent = {"group": 12, "secret": used_token}
    response = requests.post(url=url_token, json=data_sent)
    return response.json()["token"]


def get_ftp():
    contador = 0
    # retorna diccionario con todas las órdenes ftp recibidas que NO ESTÁN VENCIDAS.
    host, port = "martillo.ing.puc.cl", 22
    transport = paramiko.Transport((host, port))
    username, password = used_credentials[0], used_credentials[1]
    transport.connect(None, username, password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(path='pedidos')
    archivos = sftp.listdir()
    ordenes_ftp = []

    for xml_file in archivos:

        if xml_file != ".cache":
            with sftp.open(xml_file) as remote_file:
                for line in remote_file.readlines():
                    if line[1] == "o":
                        _id = line[11:35]
                        url_almacenes = "{}/ordenes-compra/ordenes/{}".format(
                            used_link, _id)
                        headers_ = {
                            "Authorization": "Bearer {}".format(get_token())}
                        response = requests.request(
                            "GET", url_almacenes, headers=headers_)
                        arreglo = (response.json())

                        fecha_entrega = arreglo['vencimiento']
                        time_now = datetime.datetime.now(datetime.timezone.utc)
                        time_now2 = time_now.isoformat().replace("+00:00", "Z")

                        date1 = parser.parse(fecha_entrega)
                        date2 = parser.parse(time_now2)
                        horas_agregar = datetime.timedelta(hours=int(2))
                        date3 = date2 + horas_agregar
                        if date1 > date3:
                            ordenes_ftp.append(arreglo)
                            sftp.remove(xml_file)
                        else:
                            sftp.remove(xml_file)

    sftp.close()
    transport.close()
    # retorna una lista con puros diccionarios de ordenes FTP activas (no vencidas) y elimina las que están vencidas.
    return ordenes_ftp


# print(get_ftp())
