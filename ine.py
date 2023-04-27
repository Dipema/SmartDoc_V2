import requests
import json
import re
from docs import leer_codigo_QR

'''
Ejemplo datos:

datos = {
	"model": 'e',
	"cic": '187745109',
	"citizen_id": '123381712'
}
'''

def comprobar_validez_INE(texto, ruta_doc, dir_uploads):
	datos = extraer_datos_INE(texto, ruta_doc, dir_uploads)
	if datos == 'INE no valida':
		return datos

	url = "https://ine2.p.rapidapi.com/validate-ine"

	payload = datos['payload']

	headers = {
		"content-type": "application/json",
		#"X-RapidAPI-Key": "40f3a89260mshf3800af7c5829ebp1ca84djsn70f4acbe0b01", hotmail
		"X-RapidAPI-Key": "c49b4f2ca8msh755e58514812277p16e970jsn0f2d9a64cb91", #fiinsoft
		"X-RapidAPI-Host": "ine2.p.rapidapi.com"
		}

	try:
		datos_INE = requests.request("POST", url, json=payload, headers=headers)
		datos_INE_json = datos_INE.json()
		if payload['model'] in  ['g', 'e']:
			datos_INE_json['name'] = datos['name']
		return datos_INE_json

	except Exception as e:
		print(e)
		return

def extraer_datos_INE(texto, ruta_doc, dir_uploads):
	datos_INE = {}
	datos_INE['payload'] = {}
	emision = int(re.findall(r'EMISION (.*?) ', texto)[0])
	
	if 'NACIONAL' in texto:
		try:
			valorQR = leer_codigo_QR(nombre_doc, dir_uploads)[0]
			infoQR = re.findall(r'qr.ine.mx/(.*?)/')[0]
			datos_INE['payload']['cic'] = infoQR[:-9]
			datos_INE['payload']['citizen_id'] = infoQR[4:13]

		except:
			datos_INE['payload']['cic'] = re.findall(r'IDMEX(.*?)[0-9]{1}<<', texto)[0]
			datos_INE['payload']['citizen_id'] = re.findall(r'<<(.*?) ', texto)[0][4:13]

		if emision > 2019:
			datos_INE['payload']['model'] = 'g'
		else:
			datos_INE['payload']['model'] = 'e'

	elif ('FOLIO' not in texto) and ('FEDERAL' in texto):
		datos_INE['payload']['model'] = 'd'
		datos_INE['payload']['cic'] = re.findall(r'IDMEX(.*?)[0-9]{1}<<', texto)[0]
		datos_INE['payload']['ocr'] = re.findall(r'<<([0-9]{13})', texto)[0]

	elif emision < 2014:
		datos_INE['payload']['model'] = 'c'
		datos_INE['payload']['ocr'] = re.findall(r'FIRMA (.*?) ESTE', texto)[0]
		datos_INE['payload']['elector_code'] = re.findall(r'[A-Z]{6}[0-9]{8}[A-Z]{1}[0-9]{3}', texto)[0]
		for x in ['00', '01', '02']:
			if x in texto:
				datos_INE['issue_number'] = x

	else:
		datos_INE = 'INE no valida'

	if datos_INE['payload']['model'] in  ['g', 'e']:
		texto = ''.join(texto.split(' '))
		texto = re.findall(r'<([0-9]{5}<[0-9](.*))<', texto)[0][1]
		texto = texto.split('<')
		nombre = []
		for t in texto:
			if t != '':
				nombre.append(t)

		datos_INE['name'] = ' '.join(nombre)
	
	return datos_INE