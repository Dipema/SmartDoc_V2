import re
from docs import categorizar_doc, normalizar_vocales, extraer_pagina
import os
from pdf2image import convert_from_path
import io
from google.cloud.storage import Blob
from google.cloud import storage, vision

#texto = '''020317 PAGINA 1 DE 3 VEGA RENDON ELIZABETH QUERUBINES 54 MATAMOROS INFONAVIT LOS ANGELES MATAMOROS C.P. 87458 C.R. 13000 SUC 155007 R.F.C. Cliente Sucursal PEDRO CARDENAS 1901 CP 87390 TAMAULIPAS Ciudad VERE610608HM8 PLAZA REAL MATAMOROS, TAMPS. Resumen de Saldos Saldo inicial (+) Depositos (+) Intereses recibidos (Tasa 0.00%) (-) Retiros (-) Comisiones cobradas (-) Impuestos (=) Saldo final de la cuenta @ (+) Saldo final inversiones a plazo 2 (=) Saldo final cuenta + inversiones Sdo. Prom. Min. requerido en cuenta Sdo. Prom. (1) de la Cta. ENERO $17.38 $4,416.82 CAT PROMEDIO 10.3% SIN IVA CALCULADO AL 30 DE SEPTIEMBRE DE 2021 SOBRE LINEAS DE PROTECCION PARA EMERGENCIAS A UNA TASA DE INTERES VARIABLE PROMEDIO ANUAL DE 10.10%. OFERTA VIGENTE AL 30 DE MARZO DE 2022 PARA FINES INFORMATIVOS Y DE COMPARACION. $0.00 $4,400.00 $0.00 $0.00 $34.20 Martinez Mtz. Edgar 07/03/2023 $0.00 1 Es el promedio de los saldos diarios del periodo. Comportamiento de transacciones en tu cuenta 3,900.00 2,600.00 1,300.00 0.00 * Incluye impuestos Depositos $34.20 Por uso de Linea de Sobregiro Tasa de interes ordinaria Tasa de interes moratoria $16.85 Int. efectivamente pagados Comisiones cargadas -1,300.00 -2,600.00 -3,900.00 -5,200.00 $4,416.82 Estado de Cuenta Cuenta CLABE Fecha de corte Periodo No. de dias en el periodo Moneda Banca Scotiabank $0.00 www.scotiabank.com.mx SCOTIA NOMINA CLASIC 15507995113 044818155079951131 13-ENE-23/13-FEB-23 $0.00 13-FEB-23 Intereses Retiros en efectivo 32 Saldo inicial $17.38 Saldo final= $34.20 NACIONAL RED DE SUCURSAL $4,400.00 TE INFORMAMOS QUE EL 23-ENE-23 SE ACTUALIZARA EL CONTRATO UNICO DE PERSONAS FISICAS. CONSULTA SCOTIABANK.COM.MX/CONTRATOS. $0.00 Otros cargos* Comisiones 0.00% 0.00% $0.00 NO APLICAN Estimado cliente, conforme a la reforma fiscal para 2022 su RFC, nombre o denominacion social, domicilio fiscal (C.P.) y regimen fiscal seran validados con la informacion del SAT; agradeceremos nos envie su Constancia de Situacion Fiscal (CSF) no mayor a 3 meses al correo CSF@scotiabank.com.mx, garantizando la emision de su comprobante fiscal (CFDI); de no contar con su CSF, su CFDI se emitira con datos genericos. SI DESEAS RECIBIR PAGOS A TRAVES DE TRANSFERENCIAS ELECTRONICAS DE FONDOSINTERBANCARIOS (APLICA SOLO EN MONEDA NACIONAL), DEBERAS INFORMAR A LAS PERSONAQUE ENVIARAN LOS PAGOS RESPECTIVOS, TU NUMERO DE CLABE: 044818155079951131'''
# texto = '''BANORTE JOSE GUADALUPE ARREDONDO CORONADO CALLE COSME SANTOS TAMAULIPAS 900 ZONA CENTRO VALLE HERMOSO TAMPS. C.P. 87500 SUCURSAL: 0073 VALLE HERMOSO TIPO DE ENVIO: RETENIDO NO. DE CLIENTE: 50870239 RFC: AECG520821CT5 DATOS DE SUCURSAL: PLAZA: 9861 PLAZA VALLE HERMOSO DIRECCION: LAZARO CARDENAS ESQ. TAMAULIPAS O CENTRO TELEFONO: 8420489 Producto NOMINA BANORTE SIN CHEQUER TOTAL DETALLE Resumen del periodo Saldo inicial del periodo + Total de depositos Total de retiros + Intereses Netos Ganados Total de comisiones Cobradas / Pagadas IVA sobre comisiones (16%) Intereses Cobrados / Pagados Saldo actual Saldo disponible al dia* Saldo Promedio Saldo promedio minimo En el Periodo 01 Feb al 28 Feb: Dias que comprende el periodo Detalle de la tarjeta de debito Uso de Cajeros Automaticos Compras en comercios TOTAL DE USOS DE LA TARJETA DE DEBITO Resumen de comisiones Otras comisiones NOMINA BANORTE S/CH No. de Cuenta 0319732203 COT ADO $ 80.42 $ 14,996.53 $ 15,002.22 $ 0.00 $ 0.00 $0.00 $ 0.00 $74.73 $74.73 $ 0.00 $735.32 28 $9,500.00- $ 556.00- $ 10,056.00- $ 0.00 RESUMEN INTEGRAL CLABE G Mario Albedofilie Cour m. bell ll. till 06/03/23 \u0447\u0438 ESTADO DE CUENTA / NOMINA BANORTE SIN CHEQUER 072 826 00319732203 3 BANORTE #KANORTE LA NOMINA FUERTE VISA VISA INFORMACION DEL PERIODO Aplica para cualquier Periodo Fecha de corte 28/Febrero/2023 Moneda Del 01/Febrero/2023 al 28/Febrero/2023 PESOS Saldo anterior $80.42 $80.42 NOMINA BANORTE SIN CHEQUER (Saldo inicial de $80.42) O DEPOSITOS RETIROS COMISIONES OTROS CARGOS SALDO FINAL Saldo al corte $74.73 $74.73 $14,996.53 $15,002.22 $0.00 $0.00 $74.73 Al pagar con tu ayev de 215mida Banerw recibe: Benedett's O N 0 enviflores.com. 15% DE DESCUENTO en compra mina de $450 pesos con el odigo: BANORTE15CFF Api Mega Pizza de 1 ingrediente por $299 pesos. Obten un jugo chico gratis en la compra de un juga grande. Vigencia al 30 de junio de 2023. Conoce mas promociones en Participa Tarjeta de Nomina Banorte. Consulta compra minima, terminos y condiciones en banorte.com/tutarjetafayorita Aplican restricciones. Producto emitido y operado por Banco Mercantil del Norte, S.A., Institucion de Banca Multiple, Grupo Financiero Banorte. Terminos, condiciones, comisiones y requisitos de contratacion en banorte.com En Banorte estamos para servirte en Banortel: Ciudad de Mexico: (55) 5140 5600 | Monterrey: (81) 8156 9600 | Guadalajara: (33) 3669 9000 | Resto del pais: 800 - BANORTE | Visita nuestra pagina: www.banorte.com Banco Mercantil del Norte S.A. Institucion de Banca Multiple Grupo Financiero Banorte, Av. Revolucion No. 3000, Colonia La Primavera C.P64830, Municipio Monterrey Nuevo Leon, RFC BMN930209927'''
# texto = '''BBVA ALMA IRMA MONTOYA AMARO C RIO CONCHOS 157 SAN FRANCISCO MATAMOROS TAM Informacion Financiera Rendimiento Saldo Promedio Dias del Periodo Tasa Bruta Anual Saldo Promedio Gravable Intereses a Favor (+) ISR Retenido (-) Comisiones Cheques pagados Manejo de Cuenta Total Comisiones Cargos Objetados Abonos Objetados Detalle de Movimientos Realizados FECHA OPER LIQ 07/FEB 07/FEB 07/FEB 07/FEB MEXICO DESCRIPCION % 0 0 0 SPEI ENVIADO STP 0402230paso stori 00646180224408975363 CP 87350 91.83 28 0.000 0.00 0.00 0.00 MBAN01002302070053444666 alma montoya amaro FOLY RFC: FOL 810907CJ4 10:20 AUT: 819740 FIRMA. 0.00 0.00 0.00 0.00 0.00 Periodo Fecha de Corte No, de Cuenta No. de Cliente R.F.C No. Cuenta CLABE 0701 SUCURSAL: DIRECCION: PLAZA: TELEFONO: Comportamiento Saldo Anterior Depositos / Abonos (+) Retiros / Cargos (-) Saldo Final Saldo Promedio Minimo Mensual: N/A N/A Total de Apartados Saldo Global MATAMOROS OFNA. PRINCIPAL MATAMOROS 168 COL. CENTRO MEX TM MATAMOROS 8138460 N/A 1,574.00 Referencia ******1975 COTEJADO CON ORIGINAL NOMBRE Angelica Nayara Estado de Cuenta Libreton Basico Cuenta Digital PAGINA 1/7 Otros productos incluidos en el estado de cuenta (inversiones) Tasa de Contrato Producto Interes anual \u0633\u0644\u0629 de l 08/03/23 La GAT Real es el rendimiento que obtendria despues de descontar la inflacion estimada BBVA MEXICO, S.A., INSTITUCION DE BANCA MULTIPLE, GRUPO FINANCIERO BBVA MEXICO Av. Paseo de la Reforma 510, Col. Juarez, Alcaldia Cuauhtemoc; C.P. 06600, Ciudad de Mexico, Mexico R.F.C. BBA830831 LJ2 DEL 07/02/2023 AL 06/03/2023 06/03/2023 1524701666 38708696 5 MOAA601025-ME9 012 818 01524701666 6 MONEDA NACIONAL 21 REFERENCIA CARGOS ABONOS OPERACION 445.00 Referencia 0053444666 646 2,445.62 14,355.98 16,800.07 GAT GAT Total de Nominal Real comisiones ANTES DE IMPUESTOS N/A N/A 426.62 1.53 0.00 SALDO N/A 01 0.00 LIQUIDACION 426.62'''

def extraer_datos_edo_cta(ruta_descarga, dir_downloads):

    # from app.admin.rutas import descargar_blob
    # ruta_descarga = os.path.join(dir_downloads, 'edo_cta.pdf')
    # try:
    #     descargar_blob(gs_bucket, nombre_blob, ruta_descarga)
    # except Exception as e:
    #     print(e)
    #     return 'El documento no ha sido encotrado'

    extraer_pagina(ruta_descarga, 0)

    images = convert_from_path(ruta_descarga)
    for i in range(len(images)):
        new_page_filename = dir_downloads + 'pagina' + str(i) +'.jpeg'
        images[i].save(new_page_filename, 'JPEG')

    client = vision.ImageAnnotatorClient()

    with io.open(new_page_filename, 'rb') as image:
        content = image.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image = image)

    #palabras_doc = response.full_text_annotation
    doc = response.text_annotations
    #print(doc[0].description)

    y_max = doc[0].bounding_poly.vertices[3].y
    y_cabecera = y_max/3

    palabras = []
    for word in doc[1:]:
        y_word = word.bounding_poly.vertices[3].y
        if y_word <= y_cabecera:
            palabras.append(word.description)

    texto = ' '.join(palabras)
    print(texto)

    prompt = f'''Utilizando solo los siguientes campos: Nombre, fecha de corte (dd/mm/aaaa - dd/mm/aaaa), banco, cuenta.
            Me puedes generar un diccionario de python con la info clave de este documento?: {texto}'''
    
    info_doc_texto = categorizar_doc(texto, prompt)
    info_doc_texto = normalizar_vocales(info_doc_texto.lower())
    info_doc_texto = info_doc_texto.replace("'", "\"")
    print(info_doc_texto)

    try:
        nombre = re.findall(r'"nombre": "(.*?)",', info_doc_texto)[0]
    except:
        nombre = ''

    try:
        fecha_corte = re.findall(r'"fecha de corte": "(.*?)",', info_doc_texto)[0]
    except:
        fecha_corte = ''

    try:
        banco = re.findall(r'"banco": "(.*?)",', info_doc_texto)[0]
    except:
        banco = ''
    
    try:
        clabe = re.findall(r'[0-9]{18}', texto)[0]
    except:
        clabe = re.findall(r'[0-9]{3} [0-9]{3} [0-9]{11} [0-9]{1}', texto)[0]

    try:
        cuenta = re.findall(r'"cuenta": "(.*?)"\n', info_doc_texto)[0]
    except:
        cuenta = re.findall(r'"cuenta": "(.*?)",', info_doc_texto)[0]

    if banco in ['bbva', 'BBVA']:
        rfc = re.findall(r'([A-Z]{3,4})([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1]) - ([A-Z\d]{3})', texto)[0]
        rfc = ''.join(rfc)
    else:
        rfc = re.findall(r'([A-Z]{3,4})([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])([A-Z\d]{3})', texto)[0]
        rfc = ''.join(rfc)

    info_doc = {
        'nombre': nombre,
        'rfc': rfc,
        'fechaCorte': fecha_corte,
        'banco': banco,
        'clabe': clabe,
        'cuenta': cuenta,
    }
    return info_doc

nombre_blob = '/Users/pears/Desktop/prueba_ESTADOS_DE_CUENTA_Banorte.pdf'
dir_downloads = '/Users/pears/Desktop/'
# info = extraer_datos_edo_cta(nombre_blob, dir_downloads)
# print(info)