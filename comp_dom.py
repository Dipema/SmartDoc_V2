import os
from pdf2image import convert_from_path
import io
from google.cloud import  vision
from docs import normalizar_vocales
import re
import json

def extraer_datos_compDom(ruta_doc, dir_cargas):
    ext = os.path.splitext(ruta_doc)[-1].lower()
    if ext == '.pdf':
        images = convert_from_path(ruta_doc)
        for i in range(len(images)):
            new_page_filename = dir_cargas + '/pagina' + str(i) +'.jpeg'
            images[i].save(new_page_filename, 'JPEG')
        imagen = dir_cargas + '/pagina0.jpeg'
    else:
        imagen = ruta_doc

    client = vision.ImageAnnotatorClient()

    with io.open(imagen, 'rb') as image:
        content = image.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image = image)
    doc_pag1 = response.text_annotations
    print(60*'=')
    print('TIPO DE COMPROBANTE DE DOMICILIO:')
    if 'cfe' in doc_pag1[0].description.lower():
        #print(doc_pag1[0].description)
        #SEPARA LA SECCION DONDE ESTA LA DIRECCION
        for i in range(len(doc_pag1[1:]) - 2):
            if doc_pag1[i].description.lower() == 'comisión' and doc_pag1[i+1].description.lower() == 'federal': #and doc_pag1[i+2].description.lower() == 'cliente':
                y_cfe = doc_pag1[i].bounding_poly.vertices[3].y
                x_cfe = doc_pag1[i].bounding_poly.vertices[3].x
                size_cfe = doc_pag1[i].bounding_poly.vertices[2].y - doc_pag1[i].bounding_poly.vertices[0].y
                print(y_cfe, x_cfe)
            elif doc_pag1[i].description.lower() == 'no' and doc_pag1[i+2].description.lower() == 'de' and doc_pag1[i+3].description.lower() == 'servicio':
                y_no =  doc_pag1[i].bounding_poly.vertices[0].y
                x_no =  doc_pag1[i].bounding_poly.vertices[3].x
                size_no = doc_pag1[i].bounding_poly.vertices[2].y - doc_pag1[i].bounding_poly.vertices[0].y
                print(y_no, x_no)
            elif doc_pag1[i].description.lower() == 'total' and doc_pag1[i+2].description.lower() == 'pagar': #and doc_pag1[i+2].description.lower() == 'cliente':
                y_tot = doc_pag1[i].bounding_poly.vertices[3].y
                x_tot = doc_pag1[i].bounding_poly.vertices[3].x
                size_tot = doc_pag1[i].bounding_poly.vertices[2].y - doc_pag1[i].bounding_poly.vertices[0].y
                print(y_tot, x_tot)
                
                    
        #SEPARA POR LINEA
        pal_lineas = {}
        for i in range(len(doc_pag1[1:])):
            #print(doc_pag1[i+1].description, doc_pag1[i+1].bounding_poly.vertices[3].x, doc_pag1[i+1].bounding_poly.vertices[3].y)
            linea = doc_pag1[i+1].bounding_poly.vertices[3].y
            pal = doc_pag1[i+1].description.lower()
            x_pal = doc_pag1[i+1].bounding_poly.vertices[3].x
            if (linea > (y_cfe + 45)) and (linea < (y_no - 10)) and (x_pal < (x_tot - 10)):
                #print(linea, y_cfe + 50)
                if linea in pal_lineas:
                    pal_lineas[linea].append((pal, x_pal))
                else:
                    pal_lineas[linea] = [(pal, x_pal)]
        pal_lineas = dict(sorted(pal_lineas.items()))
        pal_lineas[100000000] = []
        print(pal_lineas)
        print(60*'=')

        lineas = {}
        app = ['vacio', 'nombre', 'calle', 'specs', 'colonia', 'ciudad', 'extra']
        x = 0
        i = 0
        lista = []
        for l in sorted(pal_lineas):
            if l >= x + 10:
                if len(lista) != 1:
                    lineas[app[i]] = sorted(lista, key=lambda x: x[1])
                    lineas[app[i]] = [i[0] for i in lineas[app[i]]]
                    lineas[app[i]] = ' '.join(lineas[app[i]])
                    lista = []
                    i += 1
                x = l
            lista += pal_lineas[l]
        print(lineas)
        print('=' * 60)
        
        # MANZANA Y LOTE
        try:
            manzana = re.findall(r'm(\d+)', lineas['calle'])[0]
            lote = re.findall(r'l(\d+)', lineas['calle'])[0]  
        except:
            manzana = ''
            lote = ''

        # CALLE, NUMERO
        if manzana == '':
            try:
                numero = re.findall(r'\d+', lineas['calle'])[0]
            except:
                numero = ''

            try:
                calle = re.findall(r'^(.*) \d', lineas['calle'])[0]
            except:
                calle = ''
        else:
            numero = ''
            try:
                calle = re.findall(r'^(.*) m\d', lineas['calle'])[0]
            except:
                calle = ''
            
        # COLONIA, CP
        try:
            cp = re.findall(r'\d{5}', lineas['colonia'])[0]
        except:
            cp = ''

        try:
            colonia = re.findall(r'^(.*)cp', lineas['colonia'].replace('.', ''))[0]
        except:
            colonia = ''

        # LOCALIDAD, ESTADO
        try:
            localidad, estado = lineas['ciudad'].split(',')
            localidad = localidad[:-1]
            estado = estado[1:].replace('.', '')
        except:
            localidad = ''
            estado = ''
            
        info_doc = {
            'calle': calle,
            'numero': numero,
            'colonia': colonia,
            'localidad': localidad,
            'municipio': '',
            'estado': estado.upper(),
            'cp': cp,
            'manzana': manzana,
            'lote': lote
        }

        return info_doc

    elif ('junta de aguas y drenaje de la ciudad de matamoros' in doc_pag1[0].description.lower()):
        print('AGUAS Y DRENAJE MATAMOROS')
        print(60*'=')
        y_jad = 0
        x_jad = 0
        for w in doc_pag1[1:]:
            if w.description.lower() == 'jad':
                y_jad = w.bounding_poly.vertices[3].y
                x_jad = w.bounding_poly.vertices[3].x
                size_jad = w.bounding_poly.vertices[2].y - w.bounding_poly.vertices[0].y
                #print(y_jad, x_jad, size_jad)
                break
        
        y_min = y_jad + 120
        y_max = y_jad + 200
        x_min = 100
        x_max = 750

        palabras = []
        direccion = []
        for word in doc_pag1[1:]:
            y_word = word.bounding_poly.vertices[3].y
            x_word = word.bounding_poly.vertices[3].x
            vertices = word.bounding_poly.vertices
            x_diff = vertices[1].x - vertices[0].x
            y_diff = vertices[1].y - vertices[0].y
            if abs(x_diff) > abs(y_diff):
                if (y_word >= y_min) and (y_word <= y_max) and (x_word <= x_max):
                    d = {'dir':word.description.lower(), 'pos_y':word.bounding_poly.vertices[0].y}
                    direccion.append(d)
                    palabras.append(word.description.lower())
        palabras = ' '.join(palabras).replace('.', '')
            
        print(60*'=')
        print('DOMICILIO:')
        print(palabras)
        print(60*'=')
        try:
            calle_num = palabras.split(',')[0]
            calle = calle_num.split('#')[0]
            numero = calle_num.split('#')[1]
        except:
            calle = ''
            numero = ''
        
        try:
            colonia = palabras.split(',')[2]
        except:
            colonia = ''

        info_doc = {
            'pais': 'Mexico',
            'estado': 'Tamaulipas',
            'municipio': 'Matamoros',
            'localidad': 'Heroica Matamoros',
            'colonia': colonia,
            'calle': calle,
            'numero': numero,
            'cp': ''
        }

        return info_doc

    elif all(pal in normalizar_vocales(doc_pag1[0].description.lower()) for pal in ['comision', 'municipal', 'potable', 'nuevo laredo']):
        print('AGUA POTABLE Y ALCANTARILLADO DE NUEVO LAREDO')
        print(60*'=')

        pal_lineas = {}
        for p in doc_pag1[1:]:
            pal = p.description.lower()
            x_pal = p.bounding_poly.vertices[0].x
            linea = p.bounding_poly.vertices[3].y
            if linea in pal_lineas:
                pal_lineas[linea].append((pal, x_pal))
            else:
                pal_lineas[linea] = [(pal, x_pal)]

        pal_lineas = dict(sorted(pal_lineas.items()))
        lineas = {}
        linea = 'comapa'
        for l in pal_lineas:
            if 'usuario' in pal_lineas[l][0]:
                lineas[linea] = sorted(lineas[linea], key=lambda x: x[1])
                lineas[linea] = [i[0] for i in lineas[linea]]
                lineas[linea] = ' '.join(lineas[linea])
                linea = 'usuario'
            elif 'domicilio' in pal_lineas[l][0]:
                lineas[linea] = sorted(lineas[linea], key=lambda x: x[1])
                lineas[linea] = [i[0] for i in lineas[linea]]
                lineas[linea] = ' '.join(lineas[linea])
                linea = 'domicilio'
            elif 'rfc' in pal_lineas[l][0]:
                lineas[linea] = sorted(lineas[linea], key=lambda x: x[1])
                lineas[linea] = [i[0] for i in lineas[linea]]
                lineas[linea] = ' '.join(lineas[linea])
                linea = 'rfc'

            if linea in lineas:
                try:
                    lineas[linea] += pal_lineas[l]
                except Exception as e:
                    e
            else:
                lineas[linea] = pal_lineas[l]

        try:
            domicilio = re.findall(r'domicilio\s+(\w+)\s+(\d+)', lineas['domicilio'])[0]
            calle = domicilio[0]
            numero = domicilio[1]
        except:
            calle = ''
            numero = ''

        info_doc = {
            'pais': 'Mexico',
            'estado': 'Tamaulipas',
            'municipio': 'Nuevo Laredo',
            'localidad': 'Nuevo Laredo',
            'colonia': '',
            'calle': calle,
            'numero': numero,
            'cp': ''
        }

        return info_doc

    elif all(pal in normalizar_vocales(doc_pag1[0].description.lower()) for pal in ['junta', 'municipal', 'saneamiento', 'chihuahua']):
        print('JUNTA DE AGUA Y SANEAMIENTO DE CHIHUAHUA')
        print(60*'=')

        pal_lineas = {}
        for p in doc_pag1[1:]:
            pal = p.description.lower()
            x_pal = p.bounding_poly.vertices[0].x
            linea = p.bounding_poly.vertices[3].y
            if linea in pal_lineas:
                pal_lineas[linea].append((pal, x_pal))
            else:
                pal_lineas[linea] = [(pal, x_pal)]
        pal_lineas = dict(sorted(pal_lineas.items()))

        lineas = {}
        x = 0
        lista = []
        for l in sorted(pal_lineas):
            if (l >= x + 20):
                lineas[l] = sorted(lista, key=lambda x: x[1])
                lineas[l] = [j[0] for j in lineas[l]]
                lineas[l] = ' '.join(lineas[l])
                lista = []
                x = l
            lista += pal_lineas[l]
        #print(json.dumps(lineas, indent=4))

        app = ['vacio', 'direccion', 'sector', 'xxxxx']
        cat = []
        i = 0
        for l in list(lineas.keys()):
            #print(app[i], lineas[l])
            if app[i+1] in lineas[l]:
                #print('NUEVA LINEA')
                lineas[app[i]] = ' '.join(cat)
                i += 1
                cat = []
            cat.append(lineas[l])
        #print(json.dumps(lineas, indent=4))

        print(lineas['direccion'])
        # MANZANA, LOTE
        try:
            manzana = re.findall(r'm(\d+)', lineas['direccion'])[0]
            lote = re.findall(r'l(\d+)', lineas['direccion'])[0]  
        except:
            manzana = ''
            lote = ''

        # CALLE, NUMERO, COLONIA
        calle_num, colonia = lineas['direccion'].split(',')
        try:
            numero = re.findall(r'(\d+)\s?$', calle_num)[0]
            calle = re.findall(r'direccion\s?:\s?(.*?)\d', calle_num)[0]
        except:
            numero = ''
            calle = ''

        info_doc = {
            'pais': 'MEXICO',
            'estado': 'CHIHUAHUA',
            'municipio': '',
            'localidad': 'CHIHUAHUA',
            'colonia': colonia.strip(' ').upper(),
            'calle': calle.strip(' ').upper(),
            'numero': numero,
            'cp': '',
            'manzana': manzana,
            'lote': lote
        }
        return info_doc

    else:
        return 'Tipo de documento no valido'

doc = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMP_CFE_MEXI.pdf'
doc1 = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMP_CFE_1.pdf'
doc2 = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMP_CFE_2.pdf'
doc3 = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMP_CFE_3.pdf'
doc4 = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMP_CFE_4_COLOR.pdf'
doc_tono = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMP_CFE_TONO.jpeg'
doc_matamoros = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMPROBANTE_DOMICILIO.pdf'
doc_tam = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COMP_DOM_TAM.pdf'
doc_chi = '/Users/pears/Desktop/DocsCM/Mexi/CompDom/COM_DOM.pdf'
direc = '/Users/pears/Desktop/'

docs = [doc, doc1, doc2, doc3, doc4, doc_matamoros]

# for d in docs:
#     x = extraer_datos_compDom(d, direc)
#     print(json.dumps(x, indent=4))

x = extraer_datos_compDom(doc_chi, direc)
print(json.dumps(x, indent=4))