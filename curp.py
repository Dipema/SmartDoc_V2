from docs import leer_codigo_QR, categorizar_doc, normalizar_vocales
import requests
import json
import re

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

def extraer_datos_CURP(texto):
    prompt = f'''Con los siguientes campos: Nombre, Apellido paterno, Apellido materno, Fecha de Inscripcion, Folio. 
            Me puedes generar un diccionario de python con la info clave de este documento?: {texto}'''

    info_doc_texto = categorizar_doc(texto, prompt)
    info_doc_texto = normalizar_vocales(info_doc_texto.lower())
    print(info_doc_texto)

    info_doc = {}
    try:
        nombres = re.findall(r'"nombre": "(.*?)",', info_doc_texto)[0]
    except:
        nombres = ''

    try:
        apellido_paterno = re.findall(r'"apellido paterno": "(.*?)",', info_doc_texto)[0]
    except:
        apellido_paterno = ''

    try:
        apellido_materno = re.findall(r'"apellido materno": "(.*?)",', info_doc_texto)[0]
    except:
        apellido_materno = ''

    try:
        fecha_inscripcion = re.findall(r'"fecha de inscripcion": "(.*?)",', info_doc_texto)[0]
    except:
        fecha_inscripcion = ''

    try:
        folio = re.findall(r'"folio": "(.*?)"', info_doc_texto)[0]
    except:
        folio = ''

    try:
        curp = re.findall(r"[A-Z]{4}\d{6}[A-Z]{6}[\dA-Z]{1}\d", texto)[0]
        entidad_registro = curp[11:13]
    except:
        curp = ''
        entidad_registro = ''

    if (apellido_paterno in ):


    info_doc ={
        'nombres': nombres,
        'apellido_paterno': apellido_paterno,
        'apellido_materno': apellido_materno,
        'fecha_inscripcion': fecha_inscripcion,
        'folio': folio,
        'curp': curp,
        'entidad_registro': entidad_registro
    }
    return info_doc

texto = 'ATCER SEGOB SECRETARIA DE GOBERNACION Soy Mexico 119039195900325 ESTADOS UNIDOS MEXICANOS CONSTANCIA DE LA CLAVE UNICA DE REGISTRO DE POBLACION Clave: GOMG590110MNL 8 07. UNIDOS MARIA GUADALUPE GONGORA MARTINEZ Nombre MARIA GUADALUPE GONGORA MARTINEZ Fecha de inscripcion 10/12/1998 Folio 27699251 DIRECCION GENERAL DEL REGISTRO NACIONAL DE POBLACION E IDENTIDAD Entidad de registro NUEVO LEON CURP Certificada: verificada con el Registro Civil PRESENTE Ciudad de Mexico, a 04 de julio de 2022 El derecho a la identidad esta consagrado en nuestra Constitucion. En la Secretaria de Gobernacion trabajamos todos los dias para garantizar que las y los mexicanos gocen de este derecho plenamente; y de esta forma puedan acceder de manera mas sencilla a tramites y servicios. Nuestro objetivo es que el uso y adopcion de la Clave Unica de Registro de Poblacion (CURP) permita a la poblacion tener una sola llave de acceso a servicios gubernamentales, ser atendida rapidamente y poder realizar tramites desde cualquier computadora con acceso a internet dentro o fuera del pais. SECRETARIO DE GOBERNACION Nuestro compromiso es que la identidad de cada persona este protegida y segura, por ello contamos con los maximos estandares para la proteccion de los datos personales. En este marco, es importante que verifiques que la informacion contenida en la constancia anexa sea correcta para contribuir a la construccion de un registro fiel y confiable de la identidad de la poblacion. Agradezco tu participacion. LIC. ADAN AUGUSTO LOPEZ HERNANDEZ Estamos a sus ordenes para cualquier aclaracion o duda sobre la conformacion de su clave en TELCURP, marcando el 800 911 11 11 La Impresion de la constancia CURP en papel bond, a color o blanco y negro, es valida y debe ser aceptada para realizar todo tramite. TRAMITE GRATUITO Los Datos Personales recabados, incorporados y tratados en la Base de Datos Nacional de la Clave Unica de Registro de Poblacion, son utilizados como elementos de apoyo en la funcion de la Secretaria de Gobernacion, a traves de la Direccion General del Registro Nacional de Poblacion e Identidad en el registro y acreditacion de la identidad de la poblacion del pais, y de los nacionales residentes en el extranjero; asignando y expidiendo la Clave Unica de Registro de Poblacion. Dicha Base de Datos, se encuentra registrada en el Sistema Persona del Instituto Nacional de Transparencia, Acceso a la Informacion Publica y Proteccion de Datos Personales (http://persona.ifai.org.mx/persona/welcome.do). La transferencia de los Datos Personales y el ejercicio de los derechos de acceso, rectificacion, cancelacion y oposicion, deben realizarse conforme a la Ley General de Proteccion de Datos Personales en Posesion de los Sujetos Obligados, y demas normatividad aplicable. Para ver la version integral del aviso de privacidad ingresar a https://renapo.gob.mx/'
x = extraer_datos_CURP(texto)
print(x)

