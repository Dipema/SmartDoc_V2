from docs import categorizar_doc, normalizar_vocales
import re

def extraer_datos_pasaporte(texto):
    prompt = f'''Con los siguientes campos: Nombre, Apellido paterno, Apellido materno, Fecha de Nacimiento, Nacionalidad, Lugar de nacimiento, Fecha de expedicion, Fecha de caducidad. 
            Me puedes generar un diccionario de python con la info clave de este documento?: {texto}'''

    info_doc_texto = categorizar_doc(texto, prompt)
    info_doc_texto = normalizar_vocales(info_doc_texto.lower())
    print(info_doc_texto)
    nombres = re.findall(r'"nombre": "(.*?)",', info_doc_texto)[0]
    apellido_paterno = re.findall(r'"apellido paterno": "(.*?)",', info_doc_texto)[0]
    apellido_materno = re.findall(r'"apellido materno": "(.*?)",', info_doc_texto)[0]
    fecha_nacimiento = re.findall(r'"fecha de nacimiento": "(.*?)",', info_doc_texto)[0]
    nacionalidad = re.findall(r'"nacionalidad": "(.*?)",', info_doc_texto)[0]
    lugar_nacimiento = re.findall(r'"lugar de nacimiento": "(.*?)",', info_doc_texto)[0]
    fecha_expedicion = re.findall(r'"fecha de expedicion": "(.*?)",', info_doc_texto)[0]
    fecha_caducidad = re.findall(r'"fecha de caducidad": "(.*?)"', info_doc_texto)[0]

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

# texto = '''Maliyy PASAPORTE 16143055 Estados Unidos Mexicanos Clave del pais de expedicion MEX issuing state codel Code du pays emetteur Tipo Typel Catfigorie P Apellidos/Sumame/Nom HERNANDEZ VALLADOLID Nombres/Given names/Prenoms ANDREA Pasaporte No. Passport No./ Ne di Passepor G35064513 Nacionalidad/Nationality National MEXICANA Fecha de nacimientorDate of bev Date de naissance CURP/Personal No./No. personnel 01 06 2001 Sexo Sex Sex F Observaciones/ta/Observations HEVA010601MMCRLNA1 Lugar de nacimiento/Pace of Lieu de naissance MEXICO Fecha de expedicion/date/Date de dirance Fecha de caducidad/Expiry Dadplator 25 06 2019 25 06 2029 Firma del titular Holder's signature/Signature dure Autoridad/Autorty Autor 44 IZTACALCO P<MEXHERNANDEZ<VALLADOLID<<ANDREA<<<<<<<<<<<< G350645139MEX0106016F2906254<<<<< <<<<00'''

# info_doc = extraer_datos_pasaporte(texto)