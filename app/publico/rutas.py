from . import bp_publico
from app.models import Carga_Documentos

from flask import redirect, request, current_app
from werkzeug.utils import secure_filename

from google.cloud import storage, vision

from docs import verificar_status_trabajos, validar_documento, normalizar_vocales

from rejson import Client, Path
from redis import Redis
from rq.job import Job
from rq import Queue

import os
import io
import json
from datetime import datetime
import re
import time
import base64

storage_client = storage.Client()
client = vision.ImageAnnotatorClient()

#Subir documento al bucket
def cargar_al_bucket(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return True
    except Exception as e:
        print(e)
        return False

#Extraer documento usando Google vision
def extraer_texto(file_path, clave_empresa, RFC, blob_name, gc_bucket):

    if file_path[-3:] == 'pdf':
        batch_size = 2
        mime_type = 'application/pdf'
        feature = vision.Feature(
            type=vision.Feature.Type.DOCUMENT_TEXT_DETECTION
                )

        gcs_source_uri = f"gs://{gc_bucket}/{clave_empresa}/{RFC}/{blob_name}"
        gcs_source = vision.GcsSource(uri=gcs_source_uri)
        input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

        gcs_destination_uri = f"gs://{gc_bucket}/{clave_empresa}/{RFC}/{blob_name}"
        gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
        output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

        async_request = vision.AsyncAnnotateFileRequest(
            features=[feature], input_config=input_config, output_config=output_config)

        operation = client.async_batch_annotate_files(requests=[async_request])
        operation.result(timeout=180)

        storage_client = storage.Client()
        match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
        bucket_name = match.group(1)
        prefix = match.group(2)
        bucket = storage_client.get_bucket(bucket_name)

        blob_list = list(bucket.list_blobs(prefix=prefix))

        file_text = ''
        for blob in blob_list[1:]:
                
            output = blob
            json_string = output.download_as_string()
            response = json.loads(json_string)

            try:
                for r in response['responses']:
                    annotation = r['fullTextAnnotation']
                    file_text = file_text + ' ' + annotation['text']
            except Exception as e:
                print(e)


        file_text_with_space = file_text.replace('\n', ' ')
        file_text_with_space = normalizar_vocales(file_text_with_space)
        return file_text_with_space
        
    elif file_path[-3:] in ['jpg', 'jpeg']:
        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response_labels = client.label_detection(image=image)
        labels = response_labels.label_annotations

        file_text = []
        response_text = client.text_detection(image=image)

        for r in response_text.text_annotations:
            d = {
                        'text': r.description
                    }
            file_text.append(d)

        file_text_with_space = file_text[0]['text'].replace('\n', ' ')
        file_text_with_space = normalizar_vocales(file_text_with_space)
        return file_text_with_space
    
    else:
        return 'Formato de documento no valido (pdf, jpg, jpeg)'

#Endpoints:

@bp_publico.route('/cargar-documento/', methods=['GET', 'POST'])
def cargar_documento():

    '''Carga el documento a la nube y procede a validarlo'''

    clave_empresa = request.args.get('clave')
    RFC = request.args.get('rfc')
    tipo_documento = request.args.get('tdoc')
    ruta_documento = request.args.get('rdoc')
    token = request.args.get('token')

    nombre_doc = ruta_documento.split('/')[-1]
    blob_name = f"{RFC}-{tipo_documento}-{datetime.utcnow().isoformat()}-{nombre_doc}"
    blob_name = blob_name.replace(':', '-')

    gc_bucket = current_app.config['GOOGLE_CLOUD_BUCKET']
    print(f'Subiendo documento {blob_name}')
    cargar_al_bucket(f"{clave_empresa}/{RFC}/{blob_name}", ruta_documento, gc_bucket)
    print(f'Extrayendo texto del documento {blob_name}')
    try:
        texto = extraer_texto(ruta_documento, clave_empresa, RFC, blob_name, gc_bucket)
    except Exception as e:
        print(e)
        return "No ha sido posible la extracción de información del documento"

    dir_uploads = current_app.config['DIR_UPLOADS']
    info_documento = validar_documento(texto, tipo_documento, ruta_documento, dir_uploads)
    print(f'Documento {blob_name} validado')

    doc = {
        'clave_empresa': clave_empresa,
        'RFC': RFC,
        'tipo_documento': tipo_documento,
        'nombre_documento': blob_name,
        'texto_documento': texto,
        'info_documento': info_documento,
        'google_cloud_url': f'gs://{gc_bucket}/{clave_empresa}/{RFC}/{blob_name}',
        'fecha_carga': datetime.utcnow().isoformat()
        }

    host = current_app.config['REDIS_HOST']
    port = current_app.config['REDIS_PORT']
    password = current_app.config['REDIS_PASSWORD']

    try:
        rj = Client(host=host, port=port, password=password)       
        rj.jsonset('doc:{}'.format(blob_name), Path.rootPath(), doc)
    except Exception as e:
        print(e)

    try:
        documento = Carga_Documentos()
        documento.clave_empresa = clave_empresa
        documento.rfc = RFC
        documento.tipo_documento = tipo_documento
        documento.nombre_documento = blob_name
        documento.texto_documento = texto
        documento.informacion_documento = info_documento
        documento.url_google_cloud = f'gs://{gc_bucket}/{clave_empresa}/{RFC}/{blob_name}'
        documento.fecha_carga = datetime.utcnow().isoformat()
        documento.save()
    except Exception as e:
        print(e)
    return doc