from docs import leer_codigo_QR
import requests
import json

def extraer_CURP(nombre_doc, dir_uploads):
    valorQR = leer_codigo_QR(nombre_doc, dir_uploads)[0]
    valorQR = valorQR.split('|')
    curp = valorQR[0]

    return curp

def validar_CURP(nombre_doc, dir_uploads):

    curp = extraer_CURP(nombre_doc, dir_uploads)

    url = "https://curp-renapo.p.rapidapi.com/v1/curp"
    payload = {"curp": curp}
    headers = {
        "content-type": "application/json",
        #"X-RapidAPI-Key": "40f3a89260mshf3800af7c5829ebp1ca84djsn70f4acbe0b01", hotmail
        "X-RapidAPI-Key": "c49b4f2ca8msh755e58514812277p16e970jsn0f2d9a64cb91", #fiinsoft
        "X-RapidAPI-Host": "curp-renapo.p.rapidapi.com"
    }

    try:
        datos_CURP = requests.request("POST", url, json=payload, headers=headers)
        datos_CURP_json = json.dumps(datos_CURP.json(), indent=4)
        
    except Exception as e:
        print(e)
        return
    
    return datos_CURP.text
