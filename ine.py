import requests
import json
import re
from docs import leer_codigo_QR, normalizar_vocales
from pdf2image import convert_from_path
from google.cloud import  vision
import os
import io

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

def extraer_datos_INE(ruta_doc, dir_cargas):
    ext = os.path.splitext(ruta_doc)[-1].lower()
    if ext == '.pdf':
        images = convert_from_path(ruta_doc)
        for i in range(len(images)):
            new_page_filename = dir_cargas + '/pagina' + str(i) +'.jpeg'
            images[i].save(new_page_filename, 'JPEG')
    else:
        new_page_filename = ruta_doc

    ## PASAMOS LA IMAGEN POR GOOGLE VISION
    client = vision.ImageAnnotatorClient()

    with io.open(new_page_filename, 'rb') as image:
        content = image.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image = image)
    doc_pag1 = response.text_annotations
    #print(doc_pag1[0].description)

    if 'nacional' in doc_pag1[0].description.lower():
        # print('=' * 60)
        # print('\t ******** INE ********')
        # print('=' * 60)
        # SEPARA EL TEXTO DE LA SOLICITUD EN 3 SECCIONES
        for i in range(len(doc_pag1[1:])):
            if doc_pag1[i].description.lower() == 'credencial':
                y_nombre = doc_pag1[i].bounding_poly.vertices[3].y
                x_nombre = doc_pag1[i].bounding_poly.vertices[3].x
                print('INICIO SECCION 1 (NOMBRE):           (', x_nombre, ', ', y_nombre, ')')
            elif doc_pag1[i].description.lower() == 'domicilio':
                y_dom = doc_pag1[i].bounding_poly.vertices[3].y
                x_dom = doc_pag1[i].bounding_poly.vertices[3].x
                print("INICIO SECCION 3 (DOMICILIO):        (", x_dom, ', ', y_dom, ')')
            elif doc_pag1[i].description.lower() == 'clave':
                y_clave = doc_pag1[i].bounding_poly.vertices[3].y
                x_clave = doc_pag1[i].bounding_poly.vertices[3].x
                print("INICIO SECCION 4 (CLAVE ELECTORAL):  (", x_clave, ', ', y_clave, ')')
            elif doc_pag1[i].description.lower() == 'nacimiento':
                y_fecha = doc_pag1[i].bounding_poly.vertices[3].y
                x_fecha = doc_pag1[i].bounding_poly.vertices[3].x - 40
                print("INICIO SECCION 2 (FECHA NACIMIENTO): (", x_fecha, ', ', y_fecha, ')')
            elif doc_pag1[i].description.lower() in ['sexo', 'sexom', 'sexoh']:
                y_sexo = doc_pag1[i].bounding_poly.vertices[3].y
                x_sexo = doc_pag1[i].bounding_poly.vertices[3].x - 40
                print("INICIO SECCION 2 (SEXO):             (", x_sexo, ', ', y_sexo, ')')

        print('=' * 60)

        #SEPARA POR LINEA
        pal_lineas = {'s0':{}, 's1':{}, 's2':{}, 's3':{}, 's4':{}}
        for w in doc_pag1[1:]:
            linea = w.bounding_poly.vertices[3].y
            pal = normalizar_vocales(w.description.lower())
            x_pal = w.bounding_poly.vertices[3].x
            #print(pal, x_pal)
            if (linea < y_nombre + 30):
                app = 's0'
            elif (linea < y_dom) and (x_pal > x_sexo - 175) and (x_pal < x_sexo + 250):
                app = 's2'
            elif (linea < y_dom) and (x_pal < x_sexo - 175):
                app = 's1'
            elif (linea < y_clave - 10) and (x_pal < x_sexo) and (x_pal >= x_nombre - 25):
                app = 's3'
            elif (linea < y_clave + 300) and (x_pal < x_sexo) and (x_pal >= x_nombre - 25):
                app = 's4'
            else:
                #print(linea, x_pal)
                app = 's0'

            if linea in pal_lineas[app]:
                pal_lineas[app][linea].append((pal, x_pal))
            else:
                if pal not in ['inter', 'fos', 'hard']:
                    pal_lineas[app][linea] = [(pal, x_pal)]

        pal_lineas['s1'] = dict(sorted(pal_lineas['s1'].items()))
        pal_lineas['s2'] = dict(sorted(pal_lineas['s2'].items()))
        pal_lineas['s3'] = dict(sorted(pal_lineas['s3'].items()))
        pal_lineas['s4'] = dict(sorted(pal_lineas['s4'].items()))
        pal_lineas['s1'][100000000] = []
        pal_lineas['s2'][100000000] = []
        pal_lineas['s4'][100000000] = []
        # print(y_dom)
        # print(json.dumps(pal_lineas['s2'], sort_keys=True, indent = 4))
        # print('=' * 50)

        if y_fecha < y_clave:
            app_s4 = ['vacio', 'clave', 'curp', 'estado', 'localidad', 'extra1', 'extra2', 'extra3']
            nuevo = False
        else:
            app_s4 = ['vacio', 'clave', 'extra1','curp_registro', 'extra2', 'dob_vigencia', 'extra3']
            nuevo = True

        ######### SEPARAR LAS LINEAS DE LA SECCION 1
        lineas_s1 = {}
        x = 0
        lista = []
        for l in sorted(pal_lineas['s1']):
            if l >= x + 10:
                lineas_s1[l] = sorted(lista, key=lambda x: x[1])
                lineas_s1[l] = [j[0] for j in lineas_s1[l]]
                lineas_s1[l] = ' '.join(lineas_s1[l])
                lista = []
                x = l
            lista += pal_lineas['s1'][l]
            #print(lista)
        # print(json.dumps(lineas_s1, indent = 4))
        # print('=' * 60)

        for l in range(len(list(lineas_s1.keys()))):
            if 'nombre' in lineas_s1[list(lineas_s1.keys())[l]]:
                try:
                    nombres = lineas_s1[list(lineas_s1.keys())[l+3]]
                except:
                    nombres = ''
                try:
                    ape_materno = lineas_s1[list(lineas_s1.keys())[l+2]]
                except:
                    ape_materno = ''
                try:
                    ape_paterno = lineas_s1[list(lineas_s1.keys())[l+1]]
                except:
                    ape_paterno = ''

        ######### SEPARAR LAS LINEAS DE LA SECCION 2
        lineas_s2 = {}
        x = 0
        lista = []
        for l in sorted(pal_lineas['s2']):
            if l >= x + 10:
                lineas_s2[l] = sorted(lista, key=lambda x: x[1])
                lineas_s2[l] = [j[0] for j in lineas_s2[l]]
                lineas_s2[l] = ' '.join(lineas_s2[l])
                lista = []
                x = l
            lista += pal_lineas['s2'][l]
            #print(lista)
        # print(json.dumps(lineas_s2, indent = 4))
        # print('=' * 60)

        for l in range(len(list(lineas_s2.keys()))):
            if 'fecha' in lineas_s2[list(lineas_s2.keys())[l]]:
                try:
                    dob = lineas_s2[list(lineas_s2.keys())[l+1]]
                except:
                    dob = ''
            elif 'sexo' in lineas_s2[list(lineas_s2.keys())[l]]:
                try:
                    sexo = re.findall(r'sexo?\s(.*)', lineas_s2[list(lineas_s2.keys())[l]])[0]
                except:
                    sexo = ''

        ######### SEPARAR LAS LINEAS DE LA SECCION 4
        lineas_s4 = {}
        x = 0
        i = 0
        lista = []
        for l in sorted(pal_lineas['s4']):
            if (l >= x + 18) and (len(lista) != 1):
                # print(l, x)
                # print(i, lista)
                lineas_s4[app_s4[i]] = sorted(lista, key=lambda x: x[1])
                lineas_s4[app_s4[i]] = [j[0] for j in lineas_s4[app_s4[i]]]
                lineas_s4[app_s4[i]] = ' '.join(lineas_s4[app_s4[i]])
                lista = []
                x = l
                i += 1
            lista += pal_lineas['s4'][l]
            #print(lista)
        # print(json.dumps(lineas_s4, indent = 4))
        # print('=' * 60)

        # CURP, FOLIO, EMISION, VIGENCIA, (DOB)
        if nuevo:
            try:
                t_dob = lineas_s4['dob_vigencia']
            except:
                t_dob = ''

            try:
                t_curp = lineas_s4['curp_registro'].upper()
            except:
                t_curp = ''

            try:
                t_vigencia = lineas_s4['dob_vigencia']
            except:
                t_vigencia = ''

            c_vigencia = r'-(\d+)'
            c_emision = r'(\d+)-'
        else:
            t_dob = dob

            try:
                t_curp = lineas_s4['curp'].upper()
            except:
                t_curp = ''

            try:
                t_vigencia = lineas_s4['localidad']
            except:
                t_vigencia = ''

            c_vigencia = r'vigencia\s?(\d+)'
            c_emision = r'emision\s?(\d+)'

        try:
            curp = re.findall(r"[A-Z]{4}\d{6}[A-Z]{6}[\dA-Z]{1}\d", t_curp)[0]
        except:
            curp = ''

        try:
            folio = re.findall(r"[A-Z]{6}\d{8}[A-Z]{1}\d{3}", lineas_s4['clave'].upper())[0]
        except:
            folio = ''

        try:
            emision = re.findall(c_emision, t_vigencia)[0]
        except:
            emision = ''

        try:
            vigencia = re.findall(c_vigencia, t_vigencia)[0]

        except:
            vigencia = ''

        if nuevo:
            try:
                dob = re.findall(r'(\d+/\d+/\d+)', t_dob)[0]
            except:
                dob = ''


        info_doc = {
            'nombres': nombres.upper(),
            'apellidoPaterno': ape_paterno.upper(),
            'apellidoMaterno': ape_materno.upper(),
            'fechaNacimiento': dob,
            'genero': sexo.upper(),
            'curp': curp,
            'folio': folio,
            'fechaExpedicion': emision,
            'fechaVencimiento': vigencia
        }

        return info_doc

    else:
        return 'Tipo de INE no valido'

doc = '/Users/pears/Desktop/DocsCM/Mexi/INE/INE.pdf'
doc1 = '/Users/pears/Desktop/DocsCM/Mexi/INE/INE_1.pdf'
doc2 = '/Users/pears/Desktop/DocsCM/Mexi/INE/INE_2.pdf'
doc3 = '/Users/pears/Desktop/DocsCM/Mexi/INE/INE_3.pdf'
doc4 = '/Users/pears/Desktop/DocsCM/Mexi/INE/INE_4.pdf'
doc5 = '/Users/pears/Desktop/DocsCM/Mexi/INE/INE_5.pdf'
doc_diego = '/Users/pears/Desktop/DocsCM/INE_frontal_Diego.pdf'

docs = [doc, doc1, doc2, doc3, doc4, doc5]
direc = '/Users/pears/Desktop'

for d in docs:
    x = extraer_datos_INE(d, direc)
    print(json.dumps(x, indent=4))

# x = extraer_datos_INE(doc, direc)
# print(json.dumps(x, indent = 4))