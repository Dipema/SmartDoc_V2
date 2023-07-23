import time
import rq
from redis import Redis
from rq.job import Job
from rejson import Client, Path
from pdf2image import convert_from_path
import cv2
from config import DevelopmentConfig
import base64
from PyPDF2 import PdfWriter, PdfReader

import os
import openai
import psycopg2

# openai.organization = DevelopmentConfig.OPENAI_ORGANIZATION
# openai.api_key = DevelopmentConfig.OPENAI_APIKEY
# openai.Model.list()

host = DevelopmentConfig.REDIS_HOST
port = DevelopmentConfig.REDIS_PORT
password = DevelopmentConfig.REDIS_PASSWORD

def extraer_pagina(doc_name, page_num):
    pdf_reader = PdfReader(open(doc_name, 'rb'))
    pdf_writer = PdfWriter()
    pdf_writer.add_page(pdf_reader.pages[page_num])
    with open(f'{doc_name}', 'wb') as doc_file:
        pdf_writer.write(doc_file)

# def categorizar_doc(prompt):
#     completions = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=prompt,
#         max_tokens=1024,
#         n=1,
#         stop=None,
#         temperature=0,
#     )

    # message = completions.choices[0].text
    # return message

def normalizar_vocales(s):
    reemplazos = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ñ", "n")
    )
    for a, b in reemplazos:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

def convertir_base64(ruta_doc):
    with open(ruta_doc, 'rb') as file:
        doc_codificado = base64.b64encode(file.read())

    doc_base64 = doc_codificado.decode('utf-8')
    return doc_base64


def leer_codigo_QR(ruta_doc, dir_uploads):
    resultados_qr = {'valores':[], 'pagina':[]}
    if ruta_doc[-3:] == 'pdf':
        """Read an image and read the QR code.
        
        Args:
            filename (string): Path to file
        
        Returns:
            qr (string): Value from QR code
        """
    
        images = convert_from_path(ruta_doc)
        for i in range(len(images)):
    
        # Save pages as images in the pdf
            #new_page_filename = f'/Users/pears/Desktop/prueba/pagina'+ str(i) +'.jpg'
            new_page_filename = dir_uploads + '/pagina' + str(i) +'.jpeg'
            images[i].save(new_page_filename, 'JPEG')  

            try:
                img = cv2.imread(new_page_filename)
                detect = cv2.QRCodeDetector()
                value, points, straight_qrcode = detect.detectAndDecode(img)
                resultados_qr['valores'].append(value)
                resultados_qr['pagina'].append(i)
            except Exception as e:
                print(e)

    elif ruta_doc[-3:] in ['jpg', 'pgn', 'jpeg']:
        try:
            img = cv2.imread(ruta_doc)
            detect = cv2.QRCodeDetector()
            value, points, straight_qrcode = detect.detectAndDecode(img)
            #print((points))
            resultados_qr['valores'].append(value)
            resultados_qr['pagina'].append(i)
        except Exception as e:
            print(e)

    return resultados_qr['valores']

def validar_documento(texto, tipo_doc, ruta_doc, dir_uploads):

    print(tipo_doc)

    from sat import extraer_datos_ConstanciaSAT
    from ine import extraer_datos_INE
    from curp import validar_CURP
    from cfdi import validar_CFDI
    from pasaporte import extraer_datos_pasaporte
    from solicitud_cred import extraer_datos_sol_cred
    from edo_cta import extraer_datos_edo_cta

    if tipo_doc == 'INE':
        print('Valindando INE')
        info_doc = extraer_datos_INE(texto)

    elif tipo_doc == 'CURP':
        print('Valindando CURP')
        info_doc = validar_CURP(ruta_doc, dir_uploads)
        
    elif tipo_doc == 'ConstanciaSAT':
        print('Valindando Constancia SAT')
        info_doc = extraer_datos_ConstanciaSAT(ruta_doc, dir_uploads)

    elif tipo_doc == 'CFDI':
        print('Valindando CFDI')
        info_doc = validar_CFDI(ruta_doc, dir_uploads)

    elif tipo_doc == 'Pasaporte':
        print('Validando Pasaporte')
        info_doc = extraer_datos_pasaporte(texto)

    elif tipo_doc == 'ComprobanteDomicilio':
        print('Validando Comprobante de domicilio')
        info_doc = 'Sigue en desarrollo'

    elif tipo_doc == 'EdoCta':
        print('Validando Estado de Cuenta')
        info_doc = extraer_datos_edo_cta(ruta_doc, dir_uploads)

    elif tipo_doc == 'SolCred':
        print('Validando Solicitud de Credito')
        info_doc = extraer_datos_sol_cred(ruta_doc, dir_uploads)

    else:
        print('Documento no disponible')
        info_doc = {}

    return info_doc

def verificar_status_trabajos(id, file_path):
    continuar = True
    while continuar:
        time.sleep(5)
        try:
            resultado = Job.fetch(id, connection=Redis(host=host, port=port, password=password))
            status = resultado.get_status()
            if status == 'finished':
                resultado_json = validar_documento(resultado.result, file_path)
                continuar = False
        except Exception as e:
            print(e)
            continuar = False 
    return resultado_json

def consultar_supabse():
    try: 
        connection = psycopg2.connect(
            host = host,
            port = port,
            database = database,
            user = user,
            password = password
            )

        cursor = connection.cursor()
        query = f'''SELECT * FROM bitacora_carga_documentos;'''
        cursor.execute(query)

        respuesta = cursor.fetchall()
        print('=' * 15, 'RESPUESTA','=' * 15, '\n', respuesta, '\n'* 3)
        dtime = respuesta[0][-1]
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

