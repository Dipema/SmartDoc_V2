from docs import leer_codigo_QR
import requests
import re
from zeep import Client
import json

#file = '/Users/pears/Desktop/DocsCM/IIN_Comprobante_Recibo_Telmex_Misisipi_202208.pdf'

def validar_CFDI(ruta_doc, dir_uploads):
    try:
        resultados = leer_codigo_QR(ruta_doc, dir_uploads)
        #print(resultados)
        for res in resultados:
            if res != '':
                url = res
            
        #print(url)

        try:
            UUID_timbrado = re.findall(r'id=(.*?)&', url)[0]
            RFC_emisor = re.findall(r're=(.*?)&', url)[0]
            RFC_receptor = re.findall(r'rr=(.*?)&', url)[0]
            Total_Facturado = re.findall(r'tt=(.*?)&', url)[0]
        except:
            return 'Calidad de documento baja, no ha sido posible la lectura del codigo QR'

        #print(UUID_timbrado,RFC_emisor, RFC_receptor, Total_Facturado)

        soap_request = f'?re={RFC_emisor}&rr={RFC_receptor}&tt={Total_Facturado}&id={UUID_timbrado}'
        #print(soap_request)
        wsdl = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?WSDL'
        cliente  = Client(wsdl)
        respuesta = cliente.service.Consulta(soap_request)

        respuesta_json = {
            'CodigoEstatus': re.findall(r"'CodigoEstatus': '(.*?)',", str(respuesta))[0],
            'EsCancelable': re.findall(r"'EsCancelable': '(.*?)',", str(respuesta))[0],
            'Estado': re.findall(r"'Estado': '(.*?)',", str(respuesta))[0],
            'EstatusCancelacion': re.findall(r"'EstatusCancelacion': (.*?),", str(respuesta))[0],
            'ValidacionEFOS': re.findall(r"'ValidacionEFOS': '(.*?)'", str(respuesta))[0]
        }
        return respuesta_json

    except Exception as e:
        print(e)

def validarCFDI_texto(texto):

    uuid = re.findall(r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}', texto)[0]
    RFCs = re.findall(r'([A-Z]{3,4})([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])([A-Z\d]{3})', texto)
    RFCs = [''.join(x) for x in RFCs]

    try:
        soap_request = f'?re={RFC_emisor}&rr={RFC_receptor}&tt={Total_Facturado}&id={UUID_timbrado}'
        print(soap_request)
        wsdl = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?WSDL'
        cliente  = Client(wsdl)
        response = cliente.service.Consulta(soap_request)
        return response
    except Exception as e:
        print(e)


# x = validar_CFDI(file)
# print(x)
# print(type(x))