from . import bp_admin
from app.models import Bitacora_Consultas
from docs import convertir_base64

from flask import request, current_app
from google.cloud import storage
from redisearch import Client
import psycopg2

import json
import os
import logging
from datetime import datetime

storage_client = storage.Client()

def descargar_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
    except:
        return False

@bp_admin.route('/consultar-documento/', methods=['GET', 'POST'])
def consultar():

    '''Al recibir el tipo de documento y el RFC asociado a este documento, regresa el documento en base64'''

    RFC = request.args.get('rfc')
    clave_empresa = request.args.get('clave')
    tipo_documento = request.args.get('tdoc')
    token = request.args.get('token')
    tipo_consulta = request.args.get('tcons')

    try: 
        connection = psycopg2.connect(
            host = current_app.config['SQL_HOST'],
            port = current_app.config['SQL_PORT'],
            database = current_app.config['SQL_DATABASE'],
            user = current_app.config['SQL_USER'],
            password = current_app.config['SQL_PASSWORD']
        )

        cursor = connection.cursor()
        query = f'''SELECT nombre_documento, informacion_documento FROM bitacora_carga_documentos WHERE (tipo_documento = '{tipo_documento}' AND rfc = '{RFC}' AND clave_empresa = '{clave_empresa}');'''
        cursor.execute(query)
        respuesta = cursor.fetchall()
        info_doc = respuesta[0][1]
        if tipo_consulta == 's':
            try:
                consulta = Bitacora_Consultas()
                consulta.clave_empresa = clave_empresa
                consulta.rfc = RFC
                consulta.tipo_documento = tipo_documento
                consulta.fecha_consulta = datetime.utcnow().isoformat()
                consulta.save()
            except Exception as e:
                print(e)

            return info_doc

        elif tipo_consulta == 'c':
            nombre_doc = respuesta[0][0]
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = current_app.config['GOOGLE_CLOUD_CREDENTIALS']
            gs_bucket = current_app.config['GOOGLE_CLOUD_BUCKET']
            ruta_descarga = os.path.join(current_app.config['DIR_DESCARGAS'], nombre_doc)
            nombre_blob = f"{clave_empresa}/{RFC}/{tipo_documento}/{nombre_doc}"

            try:
                descargar_blob(gs_bucket, nombre_blob, ruta_descarga)
            except Exception as e:
                print(e)
                return 'El documento no ha sido encotrado'

            doc_base64 = convertir_base64(ruta_descarga)
            try:
                consulta = Bitacora_Consultas()
                consulta.clave_empresa = clave_empresa
                consulta.rfc = RFC
                consulta.tipo_documento = tipo_documento
                consulta.fecha_consulta = datetime.utcnow().isoformat()
                consulta.save()
            except Exception as e:
                print(e)

            return [info_doc, doc_base64]
        
        else:
            return 'Tipo de consulta no valida', 400

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


@bp_admin.route('/consultar-rfc/', methods=['GET', 'POST'])
def consultar_rfc():

    '''Al recibir un RFC y la clave de la empresa, regresa todos los documentos asociados a ese RFC en base64 y el tipo de doc'''

    RFC = request.args.get('rfc')
    clave_empresa = request.args.get('clave')
    token = request.args.get('token')

    try: 
        connection = psycopg2.connect(
            host = current_app.config['SQL_HOST'],
            port = current_app.config['SQL_PORT'],
            database = current_app.config['SQL_DATABASE'],
            user = current_app.config['SQL_USER'],
            password = current_app.config['SQL_PASSWORD']
        )

        cursor = connection.cursor()
        query = f'''SELECT tipo_documento, informacion_documento FROM bitacora_carga_documentos WHERE  (rfc = '{RFC}' AND clave_empresa = '{clave_empresa}');'''
        cursor.execute(query)
        respuesta = cursor.fetchall()

        try:
            consulta = Bitacora_Consultas()
            consulta.clave_empresa = clave_empresa
            consulta.rfc = RFC
            consulta.tipo_documento = f'Todos los documentos asociados a {RFC}'
            consulta.fecha_consulta = datetime.utcnow().isoformat()
            consulta.save()
        except Exception as e:
            print(e)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)
        return
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        return respuesta            
