from docs import categorizar_doc
import re

def extraer_datos_pasaporte(texto):
    prompt = f'''Con los siguientes campos: Nombre, Apellido paterno, Apellido materno, Fecha de Nacimiento, Nacionalidad, Lugar de nacimiento, Fecha de expedicion, Fecha de caducidad. 
            Me puedes generar un diccionario de python con la info clave de este documento?: {texto}'''

    info_doc_texto = categorizar_doc(texto, prompt)
    print(info_doc_texto)
    nombres = re.findall(r'"Nombre": "(.*?)",', info_doc_texto)[0]
    apellido_paterno = re.findall(r'"Apellido paterno": "(.*?)",', info_doc_texto)[0]
    apellido_materno = re.findall(r'"Apellido materno": "(.*?)",', info_doc_texto)[0]
    fecha_nacimiento = re.findall(r'"Fecha de Nacimiento": "(.*?)",', info_doc_texto)[0]
    nacionalidad = re.findall(r'"Nacionalidad": "(.*?)",', info_doc_texto)[0]
    lugar_nacimiento = re.findall(r'"Lugar de nacimiento": "(.*?)",', info_doc_texto)[0]
    fecha_expedicion = re.findall(r'"Fecha de expedicion": "(.*?)",', info_doc_texto)[0]
    fecha_caducidad = re.findall(r'"Fecha de caducidad": "(.*?)"', info_doc_texto)[0]

    info_doc ={
        'nombres': nombres,
        'apellido_paterno': apellido_paterno,
        'apellido_materno': apellido_materno,
        'fecha_nacimiento': fecha_nacimiento,
        'nacionalidad': nacionalidad,
        'lugar_nacimiento': lugar_nacimiento,
        'fecha_expedicion': fecha_expedicion,
        'fecha_caducidad': fecha_caducidad
    }
    
    print(info_doc)

    return info_doc