# PROYECTO 2022'2: INTEGRAR.COM

El objetivo del proyecto final del curso es que los alumnos desarrollen en grupo la
automatización de un proceso mediante técnicas de integración de sistemas.
Se espera que después de este proyecto, los alumnos sean capaces de:
1. Diseñar un proceso y determinar las integraciones necesarias para llevar a cabo un
objetivo de negocio
2. Diseñar integraciones para interoperar con sistemas de terceros
3. Implementar un sistema capaz de interoperar con sistemas de terceros



# all_scale_flights = ['SCLIADCDG', 'SCLIADMEL', 'SCLIADPEK', 'SCLCDGIAD', 'SCLCDGMEL', 'SCLCDGPEK', 'SCLMELIAD', 'SCLMELCDG', 'SCLMELPEK', 'SCLPEKIAD',
#                      'SCLPEKCDG', 'SCLPEKMEL', 'IADSCLCDG', 'IADSCLMEL', 'IADSCLPEK', 'IADCDGSCL', 'IADCDGMEL', 'IADCDGPEK', 'IADMELSCL', 'IADMELCDG',
#                      'IADMELPEK', 'IADPEKSCL', 'IADPEKCDG', 'IADPEKMEL', 'CDGSCLIAD', 'CDGSCLMEL', 'CDGSCLPEK', 'CDGIADSCL', 'CDGIADMEL', 'CDGIADPEK',
#                      'CDGMELSCL', 'CDGMELIAD', 'CDGMELPEK', 'CDGPEKSCL', 'CDGPEKIAD', 'CDGPEKMEL', 'MELSCLIAD', 'MELSCLCDG', 'MELSCLPEK', 'MELIADSCL',
#                      'MELIADCDG', 'MELIADPEK', 'MELCDGSCL', 'MELCDGIAD', 'MELCDGPEK', 'MELPEKSCL', 'MELPEKIAD', 'MELPEKCDG', 'PEKSCLIAD', 'PEKSCLCDG',
#                      'PEKSCLMEL', 'PEKIADSCL', 'PEKIADCDG', 'PEKIADMEL', 'PEKCDGSCL', 'PEKCDGIAD', 'PEKCDGMEL', 'PEKMELSCL', 'PEKMELIAD', 'PEKMELCDG']


# all_direct_flights = ['SCLIAD', 'IADCDG', 'IADMEL', 'IADPEK', 'SCLCDG',
#                       'CDGIAD', 'CDGMEL', 'CDGPEK', 'SCLMEL', 'MELIAD',
#                       'MELCDG', 'MELPEK', 'SCLPEK', 'PEKIAD', 'PEKCDG',
#                       'PEKMEL', 'IADSCL', 'CDGSCL', 'MELSCL', 'PEKSCL']


### fabricar.py ###

1. read_csv()
- Entrega diccionario con información de productos.csv.
- return: {'CLJETA1': {'lote': 4, 'grupos': "['1', '2', '3', '4']"}, 'USJETA1': {'lote': 4, 'grupos': "['1', '2', '3', '4', '5', '6']"},.....}

2. production_formulas()
- Entrega un diccionario con las fórmulas de los vuelos directos.
- {'SCLIAD': {'CLJETA1': 5, 'CLCREW': 4, 'CLAB330': 1, 'CLOFC': 1}, 'IADCDG': {'USJETA1': 5, 'USCREW': 4, 'USAB330': 1, 'USOFC': 1},....}

3. check_sf_store()
-  Calcula el número de cada sc (scale_flights) disponibles en el inventario buffer, con vencimiento mayor a 20 minutos. 

4. check_sf_incoming(scale_flights)
- Calcula el número de cada sc (scale_flights) en camino según la base de datos To_Do_Orders.

5. check_sf_created(scale_flights)
- Calcula el número de cada sc (scale_flights) que están en producción según la base de datos In_Production.
- Limpia la bd ya que para la próxima iteración debiesen estar listos.

6. sf_order()
- Corre las 3 funciones de sc para entragar un diccionario {sku: cantidad ....} que muestra lo que tenemos actualmente de vuelos con escala.

7. check_df_store(), check_df_incoming(), check_df_created(scale_flights), df_order()
- Repiten todo lo anterior pero para vuelos directos.

8. products_order_one()
- Aca se define el inventario mínimo de sc y df.
- Calcula la cantidad de vuelos directos que hay que pedir para mantener los inventarios ok. (todo en términos de vuelos directos)

9. products_order_two()
- Acá elegimos un posible stok mínimo de materias primas.
- Calcula la cantidad de materias primas que hay que pedir para mantener los inventarios ok. (todo en términos de materias primas)

10. products_order_three()
- Manda a producir todas las materias primas necesarias.
- Agrega a la base de datos To_Do_Orders lo que esta por venir, y en que momento debe ser preparado. (sku, cantidad, momento)

11. dispach_sf()
- Función para despachar (aún no se usa)

12. clear_up_warehouse()
- Mueve todos los productos desde store a buffer.

13. df_production()
- Lee To_Do_Orders en momento 0 solo de vuelos directos.
- Mueve las materas primas necesarias desde buffer a store.
- Fabrica los vuelos directos que se deben hacer esta iteración.
- Actualiza base de datos To_Do_Orders según la cantidad que se pudo mandar a producir.
- Actualiza base de datos In_Production según la cantidad que se pudo mandar a producir.

14. sf_production()
- Lee To_Do_Orders en momento 0 solo de vuelos directos.
- Mueve las materas primas necesarias desde buffer a store.
- Fabrica los vuelos directos que se deben hacer esta iteración.
- Actualiza base de datos To_Do_Orders según la cantidad que se pudo mandar a producir.
- Actualiza base de datos In_Production según la cantidad que se pudo mandar a producir.
- Mueve todo lo de momento 1 a momento 0 para la próxima iteración.

15. start()
- Corre el flujo.


# Cosas por mejorar:
- Que no se "pidan" productos negativos, dejar en 0. 
- Mejorar cálculo de materias primas a pedir sgn df y sf faltantes, se está pidiendo menos de lo necesarios.
- Mejorar fabricación de df y sf, se hacen más de algunos.