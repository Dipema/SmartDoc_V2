import base64
import urllib.request
import re
import codecs
import json
import requests

from docs import leer_codigo_QR, normalizar_vocales

def extraer_datos_ConstanciaSAT(filename, dir_uploads):
    valorQR = leer_codigo_QR(filename, dir_uploads)
    url = valorQR[0]

    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
    try:
        requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass

    try:
        response = requests.get(url, verify=False)
        #print(dir(response))
        #print(response.url, response.text)
        #response = urllib.request.urlopen(url)
    except:
        return 'Calidad de documento baja, no ha sido posible la lectura del codigo QR'
    #responseData = response.read()
    responseData = response.text
    #responseData = codecs.decode(responseData,'UTF-8')

    RFC = re.findall(r'<li>(.*?)</li>', str(responseData))
    RFC = re.findall(r': (.*?),', RFC[0])

    respuesta_QR_SAT = {}
    respuesta_QR_SAT["RFC"] = RFC[0]

    SAT_tablas = re.findall(r'<td(.*?)>(.*?)</td>', str(responseData))

    Llaves = []
    Valores = []
    flag = 'llave'
    for cadaTabla in SAT_tablas:
        infoTabla = re.findall(r'<span style="font-weight: bold;">(.*?):</span>', cadaTabla[1])
        if (flag == 'llave'):
            if ('span' in cadaTabla[1]) and (infoTabla != []):
                llave = normalizar_vocales(infoTabla[0])
                llave = re.sub(r"(_|-)+", " ", llave).title().replace(" ", "")
                Llaves.append(''.join([llave[0].lower(), llave[1:]]))
                flag = 'valor'
        else:
            Valores.append(normalizar_vocales(cadaTabla[1]))
            flag = 'llave'

    numLlaves = len(Llaves)
    for n in range(0, numLlaves-1):
        Llave = Llaves[n]
        respuesta_QR_SAT[Llave] = Valores[n]

    return respuesta_QR_SAT

# x = extraer_datos_ConstanciaSAT('/Users/pears/Desktop/DocsCM/IIN_SAT.pdf')
# print(x)
