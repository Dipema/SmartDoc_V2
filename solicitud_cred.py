import os
import re
from pdf2image import convert_from_path
import io
from google.cloud import  vision
from docs import normalizar_vocales
import json

def extraer_datos_sol_cred(ruta_doc, dir_cargas):
    #global info_doc
    ### CHECHAMOS SI ES UN PDF
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

    with io.open(dir_cargas + '/pagina0.jpeg', 'rb') as image:
        content = image.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image = image)
    doc_pag1 = response.text_annotations

    with io.open(dir_cargas + '/pagina1.jpeg', 'rb') as image:
        content = image.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image = image)
    doc_pag2 = response.text_annotations

    #if 'DXN' in doc_pag1[0].description:
    #print(doc_pag2[0].description)
    print('=' * 50)
    app = 's0'
    # SEPARA EL TEXTO DE LA SOLICITUD EN 3 SECCIONES
    y_sec01= []
    x_sec01 = []
    for i in range(len(doc_pag1[1:]) - 2):
        if doc_pag1[i].description.lower() == 'datos' and doc_pag1[i+1].description.lower() == 'del': #and doc_pag1[i+2].description.lower() == 'cliente':
            y_sec01.append(doc_pag1[i].bounding_poly.vertices[0].y)
        elif doc_pag1[i].description.lower() == 'referencias':
            y_sec2 = doc_pag1[i].bounding_poly.vertices[0].y
            x_sec2 = doc_pag1[i].bounding_poly.vertices[0].x
            print("INICIO SECCION 2 (REFERENCIAS):       ", y_sec2)
        
        if 'DXN' in doc_pag1[0].description:
            tipo_sol = 'dxn'
            if doc_pag1[i].description.lower() == 'datos' and doc_pag1[i+1].description.lower() == 'laborales':
                y_sec3 = doc_pag1[i].bounding_poly.vertices[3].y
                x_sec3 = doc_pag1[i].bounding_poly.vertices[3].x
                print("INICIO SECCION 3 (DATOS LABORALES):   ", y_sec3)

    if 'TRES' in doc_pag1[0].description:
        tipo_sol = 'tres'
        for i in range(len(doc_pag2[1:]) - 2):
            if doc_pag2[i].description.lower() == 'datos' and doc_pag2[i+1].description.lower() == 'laborales':
                y_sec3 = doc_pag2[i].bounding_poly.vertices[3].y
                x_sec3 = doc_pag2[i].bounding_poly.vertices[3].x
                print("INICIO SECCION 3 (DATOS LABORALES, PAG 2):   ", y_sec3)
            elif 'evaluacion' in normalizar_vocales(doc_pag2[i].description.lower()):
                y_sec4 = doc_pag2[i].bounding_poly.vertices[0].y
                x_sec4 = doc_pag2[i].bounding_poly.vertices[0].x
                print("INICIO SECCION 4 (EVALUACION):       ", y_sec4)

    y_sec0 = min(y_sec01)
    y_sec1 = max(y_sec01)
    print("INICIO SECCION 0 (DATOS DEL CREDITO): ", y_sec0)
    print("INICIO SECCION 1 (DATOS DEL CLIENTE): ", y_sec1)
        
    #SEPARA LAS PALABRAS POR LINEA
    pal_lineas = {'s0':{}, 's1':{}, 's2':{}, 's3':{}, 'extra':{}}
    for i in range(len(doc_pag1[1:])):
        linea = doc_pag1[i+1].bounding_poly.vertices[3].y
        if linea < y_sec0:
            app = 'extra'
        elif linea < y_sec1:
            app = 's0'
        elif linea < y_sec2:
            app = 's1'
        elif (linea < y_sec3) and (tipo_sol == 'dxn'):
            app = 's2'
        elif (linea > y_sec2) and (tipo_sol == 'tres'):
            app = 's2'
        elif (tipo_sol == 'dxn'):
            app = 's3'
        else:
            app = 'extra'

        pal = doc_pag1[i+1].description.lower()
        x_pal = doc_pag1[i+1].bounding_poly.vertices[3].x
        if linea in pal_lineas[app]:
            pal_lineas[app][linea].append((normalizar_vocales(pal), x_pal))
        else:
            pal_lineas[app][linea] = [(normalizar_vocales(pal), x_pal)]

    if tipo_sol == 'tres':
        for i in range(len(doc_pag1[1:])):
            linea = doc_pag1[i+1].bounding_poly.vertices[3].y
            pal = doc_pag2[i+1].description.lower()
            x_pal = doc_pag2[i+1].bounding_poly.vertices[3].x
            if (linea > y_sec3) and (linea < y_sec4):
                if linea in pal_lineas[app]:
                    pal_lineas['s3'][linea].append((normalizar_vocales(pal), x_pal))
                else:
                    pal_lineas['s3'][linea] = [(normalizar_vocales(pal), x_pal)]
    
    pal_lineas['s0'] = dict(sorted(pal_lineas['s0'].items()))
    pal_lineas['s0'][100000000] = []
    pal_lineas['s1'] = dict(sorted(pal_lineas['s1'].items()))
    pal_lineas['s1'][100000000] = []
    pal_lineas['s2'] = dict(sorted(pal_lineas['s2'].items()))
    pal_lineas['s2'][100000000] = []
    pal_lineas['s3'] = dict(sorted(pal_lineas['s3'].items()))
    #print(json.dumps(pal_lineas['s0'], indent=4))

    ######### SEPARAR LAS LINEAS DE LA SECCION 0

    lineas_s0 = {}
    x = 0
    lista = []
    for l in sorted(pal_lineas['s0']):
        if (l >= x + 30):
            lineas_s0[l] = sorted(lista, key=lambda x: x[1])
            lineas_s0[l] = [j[0] for j in lineas_s0[l]]
            lineas_s0[l] = ' '.join(lineas_s0[l])
            lista = []
            x = l
        lista += pal_lineas['s0'][l]
    #print(i, lista)
    if tipo_sol == 'dxn':
        app_s0 = ['vacio', 'domicilio', 'seccion', 'monto', 'tipo']
    elif tipo_sol == 'tres':
        app_s0 = ['vacio', 'domicilio', 'tipo', 'monto', 'finalidad', 'extra']
    cat = []
    i = 0
    for l in list(lineas_s0.keys()):
        #print(app_s0[i], lineas_s0[l])
        if app_s0[i+1] in lineas_s0[l]:
            lineas_s0[app_s0[i]] = ' '.join(cat)
            i += 1
            cat = []
        cat.append(lineas_s0[l])
    try:
        lineas_s0['finalidad'] = cat[0]
    except:
        lineas_s0['finalidad'] = ''
    print('=' * 60)
    print(' ******** LINEAS SECCION 0 ******** ')
    print('-' * 40)
    print(json.dumps(lineas_s0, indent = 4))
    print('=' * 60)
    
    ######### SEPARAR LAS LINEAS DE LA SECCION 1
    lineas_s1 = {}
    x = 0
    lista = []
    for l in sorted(pal_lineas['s1']):
        if (l >= x + 30):
            lineas_s1[l] = sorted(lista, key=lambda x: x[1])
            lineas_s1[l] = [j[0] for j in lineas_s1[l]]
            lineas_s1[l] = ' '.join(lineas_s1[l])
            lista = []
            x = l
        lista += pal_lineas['s1'][l]
    #print(i, lista)

    app_s1 = ['vacio', 'nombre', 'lugar', 'fecha', 'curp', 'calle', 'tipo', 'tel', 'escolaridad']
    if tipo_sol == 'tres':
        app_s1.append('llamada')
    cat = []
    i = 0
    for l in list(lineas_s1.keys()):
        #print(app_s1[i], lineas_s1[l])
        if app_s1[i+1] in lineas_s1[l]:
            lineas_s1[app_s1[i]] = ' '.join(cat)
            i += 1
            cat = []
        cat.append(lineas_s1[l])
    try:
        lineas_s1['llamada'] = cat[0]
    except:
        lineas_s1['llamada'] = ''
    print(' ******** LINEAS SECCION 1 ******** ')
    print('-' * 40)
    print(json.dumps(lineas_s1, indent = 4))
    print('=' * 60)

    ######### SEPARAR LAS LINEAS DE LA SECCION 2
    lineas_s2 = {}
    x = 0
    lista = []
    for l in sorted(pal_lineas['s2']):
        if (l >= x + 40):
            lineas_s2[l] = sorted(lista, key=lambda x: x[1])
            lineas_s2[l] = [j[0] for j in lineas_s2[l]]
            lineas_s2[l] = ' '.join(lineas_s2[l])
            lista = []
            x = l
        lista += pal_lineas['s2'][l]
    #print(i, lista)

    app_s2 = ['vacio', 'nombre', 'tel', 'adicional', 'recados', 'extra']
    cat = []
    i = 0
    for l in list(lineas_s2.keys()):
        #print(app_s2[i], lineas_s2[l])
        if app_s2[i+1] in lineas_s2[l]:
            lineas_s2[app_s2[i]] = ' '.join(cat)
            i += 1
            cat = []
        cat.append(lineas_s2[l])
    try:
        lineas_s2['recados'] = cat[0]
    except:
        lineas_s2['recados'] = ''
    print(' ******** LINEAS SECCION 2 ******** ')
    print('-' * 40)
    print(json.dumps(lineas_s2, indent = 4))
    print('=' * 60)

    ######### SEPARAR LAS LINEAS DE LA SECCION 3
    lineas_s3 = {}
    x = 0
    lista = []
    for l in sorted(pal_lineas['s3']):
        if (l >= x + 30):
            lineas_s3[l] = sorted(lista, key=lambda x: x[1])
            lineas_s3[l] = [j[0] for j in lineas_s3[l]]
            lineas_s3[l] = ' '.join(lineas_s3[l])
            lista = []
            x = l
        lista += pal_lineas['s3'][l]
    #print(i, lista)

    app_s3 = ['vacio', 'tipo', 'lugar', 'laboral', 'pagina']
    cat = []
    i = 0
    for l in list(lineas_s3.keys()):
        #print(app_s1[i], lineas_s1[l])
        if app_s3[i+1] in lineas_s3[l]:
            lineas_s3[app_s3[i]] = ' '.join(cat)
            i += 1
            cat = []
        cat.append(lineas_s3[l])
    try:
        lineas_s3['pagina'] = cat[0]
    except:
        lineas_s3['pagina'] = ''
    print(' ******** LINEAS SECCION 3 ******** ')
    print('-' * 40)
    print(json.dumps(lineas_s3, indent = 4))
    print('=' * 60)

    nums = '145790'
    letras = 'lastqo'
    trantab = str.maketrans(letras, nums)
    antiguedad = {}

    # TELEFONOS, CORREO, DIRECCION, ESCOLARIDAD
    t = lineas_s1['tel'].replace(' ', '').replace('.', '')
    telefonos = re.findall(r'\d+', t)
    print(telefonos)
    try:
        tel_part = re.findall(r'domicilio(.*)tel', t)[0]
        tel_part = tel_part.translate(trantab)
        if len(tel_part) > 10:
            tel_part = tel_part[0:9]
    except:
        try:
            tel_part = telefonos[0]
        except:
            tel_part = ''

    try:
        tel_cel = re.findall(r'celular(.*)tro', t)[0]
        tel_cel = tel_cel.translate(trantab)
        if len(tel_cel) > 10:
            tel_cel = tel_cel[0:9]
    except:
        tel_cel = ''

    try:
        tel_otro = re.findall(r'otel(.*)correo', t)[0]
        tel_otro = tel_otro.translate(trantab)
        if len(tel_otro) > 10:
            tel_otro = tel_otro[0:9]
    except:
        tel_otro = ''

    try:
        correo = re.findall(r'electronico(.*)$', t)[0]
    except:
        correo = ''

    try:
        domicilio = re.findall(r'domicilio\s+(.*)', lineas_s1['calle'])[0]
    except:
        domicilio = lineas_s1['calle']

    # ESCOLARIDAD
    escolaridad = ['sin estudios', 'primaria', 'secundaria', 'bachillerato / tecnica', 'preparatoria', 'licenciatura', 'posgrado']
    grado_escolaridad = ''
    for e in escolaridad:
        if not re.search(e + ' o', lineas_s1['escolaridad']):
            grado_escolaridad = e
            break

    # TIPO DE EMPLEADO
    empleado = ['activo', 'jubilado / pensionado', 'beneficiario']
    tipo_empleado = ''
    for e in empleado:
        if not re.search(e + ' o', lineas_s3['tipo']):
            tipo_empleado = e
            break

    # EXTENSION, NUM EMPLEADO
    try:
        ext = re.findall(r'ext (.*) numero', lineas_s3['lugar'].relpace('.', ''))[0]
    except:
        ext = ''

    try:
        num_empleado = re.findall(r'afiliacion(.+)', lineas_s3['lugar'].replace('.', ''))[0]
        num_empleado = ''.join(num_empleado.split(' '))
    except:
        num_empleado = ''

    # PUESTO, ANTIGUEDAD, NOMBRE LUGAR TRABAJO
    try:
        puesto = re.findall(r'puesto\s?(.*)\s?departamento', lineas_s3['laboral'].replace('.', ''))[0]
    except:
        puesto = ''

    try:
        lugar_trabajo = re.findall(r'trabajo\s?(.*)\s?tel', lineas_s3['lugar'].replace('.', ''))[0]
    except:
        lugar_trabajo = ''

    try:
        antiguedad['anios'] = re.findall(r'anos\s?(.*)\s?meses', lineas_s3['laboral'].replace('.', ''))[0]
        antiguedad['anios'] = antiguedad['anios'].translate(trantab)
    except:
        antiguedad['anios'] = ''
    try:
        antiguedad['meses'] = re.findall(r'meses\s?(.*)\s?puesto', lineas_s3['laboral'].replace('.', ''))[0]
        antiguedad['meses'] = antiguedad['meses'].translate(trantab)
    except:
        antiguedad['meses'] = ''

    # TIEMPO DE RESIDENCIA
    tiempo_residencia = {}
    tiempo = tiempo_residencia['anios'] = re.findall(r'(\d+)', lineas_s1['tipo'].replace('.', ''))
    try:
        tiempo_residencia['anios'] = tiempo[0]
        tiempo_residencia['anios'] = tiempo_residencia['anios'].translate(trantab)
    except:
        tiempo_residencia['anios'] = ''
    try:
        tiempo_residencia['meses'] = tiempo[1]
        tiempo_residencia['meses'] = tiempo_residencia['meses'].translate(trantab)
    except:
        tiempo_residencia['meses'] = ''

    # PLAZO, MONTO SOLICITADO, DESCUENTO
    try:
        plazo = re.findall(r'plazo\s?(.*)\s?descuento', lineas_s0['monto'])[0]
        
    except:
        plazo = ''

    try:
        monto = re.findall(r'\$\s?(.*)\s?plazo', lineas_s0['monto'])[0]
    except:
        monto = ''

    try:
        descuento = re.findall(r'descuento \$\s?(.*)', lineas_s0['monto'])[0]
    except:
        descuento = ''

    # SUCURSAL, PROMOTOR
    try:
        sucursal = re.findall(r'entrevista\s(.*)\sfecha', lineas_s0['domicilio'])[0]
    except:
        sucursal = ''

    try:
        promotor = re.findall(r'comercial\s(.*)$', lineas_s0['seccion'])[0]
    except:
        promotor = ''

    # REFERENCIAS
    try:
        parentesco = re.findall(r'parentesco\s?(.*)$', lineas_s2['nombre'])[0]
    except:
        parentesco = ''

    try:
        nombre_ref = re.findall(r's\s?(.*)\s?parentesco', lineas_s2['nombre'].replace('!', ''))[0]
        nombre_ref = nombre_ref.replace(')', '')
        nombre_ref = nombre_ref.split(' ')
        nombre_ref = [elem for elem in nombre_ref if elem != '']
        if len(nombre_ref) == 3:
            primer_nombre_ref = nombre_ref[-1]
            segundo_nombre_ref = ''
            ape_paterno_ref = nombre_ref[0]
            ape_materno_ref = nombre_ref[1]
        elif len(nombre_ref) == 2:
            primer_nombre_ref = nombre_ref[1]
            segundo_nombre_ref = ''
            ape_paterno_ref = nombre_ref[0]
            ape_materno_ref = ''
        elif len(nombre_ref) == 4:
            primer_nombre_ref = nombre_ref[2]
            segundo_nombre_ref = nombre_ref[3]
            ape_paterno_ref = nombre_ref[0]
            ape_materno_ref = nombre_ref[1]
        else:
            primer_nombre_ref = ''
            segundo_nombre_ref = ''
            ape_paterno_ref = ''
            ape_materno_ref = ''
    except:
        primer_nombre_ref = ''
        segundo_nombre_ref = ''
        ape_paterno_ref = ''
        ape_materno_ref = ''

    try:
        t = lineas_s2['tel'].replace(' ', '').replace('.', '')
        tel_ref = re.findall(r'(\d+)', t)[0]
        if len(tel_ref) > 10:
            tel_ref = tel_ref[0:10]
    except:
        tel_ref = ''

    info_doc = {
        'telefonoParticular': tel_part,
        'extension': ext,
        'numeroCelular': tel_cel,
        'correo': correo.replace(' ', ''),
        'gradoEscolaridad': grado_escolaridad.upper(),
        'puesto': puesto.upper(),
        'lugarTrabajo': lugar_trabajo.upper(),
        'antiguedadLaboral': antiguedad,
        'direccion': domicilio,
        'otroTelefono': tel_otro,
        'tiempoResidencia': tiempo_residencia,
        'numeroEmpleado': num_empleado.upper(),
        'tipoEmpleado': tipo_empleado.upper(),
        'plazo': plazo.upper().replace('.', ''),
        'montoSolicitado': monto,
        'descuento': descuento,
        'sucursal': sucursal.upper().replace('.', ''),
        'promotor': promotor.upper().replace('.', ''),
        'primerNombreReferencia': primer_nombre_ref.upper(),
        'segundoNombreReferencia': segundo_nombre_ref.upper(),
        'apellidoPaternoReferencia': ape_paterno_ref.upper(),
        'apellidoMaternoReferencia': ape_materno_ref.upper(),
        'parentesco': parentesco.upper(),
        'telefonoReferencia': tel_ref
    }

    return info_doc

    # else:
    #     return 'Tipo de solicitud de crédito no valido'

path = '/Users/pears/Desktop/DocsCM/Mexi/SolCred/SOLICITUD_TRES.pdf'
doc = '/Users/pears/Desktop/DocsCM/Mexi/SolCred/SOLICITUD_DXN.pdf'
doc1 = '/Users/pears/Desktop/DocsCM/Mexi/SolCred/SOLICITUD_DXN_1.pdf'
doc2 = '/Users/pears/Desktop/DocsCM/Mexi/SolCred/SOL_DXN_2.pdf'
doc3 = '/Users/pears/Desktop/DocsCM/Mexi/SolCred/SOL_DXN_3.pdf'
doc4 = '/Users/pears/Desktop/DocsCM/Mexi/SolCred/SOL_DXN_4.pdf'
# doc5 = '/Users/pears/Desktop/DocsCM/Mexi/SolCred/SOLICITUD_DXN_1.pdf'

docs = [doc, doc1, doc2, doc3, doc4]
direc = '/Users/pears/Desktop'

# for d in docs:
#     x = extraer_datos_sol_cred(d, direc)
#     print(' ******** RESULTADOS ******** ')
#     print(json.dumps(x, indent=4))

x = extraer_datos_sol_cred(doc4, direc)
print('=' * 50)
print(' ***** RESULTADOS ***** ')
print(json.dumps(x, indent=4))
#print(x['direccion'])