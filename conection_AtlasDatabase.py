from pymongo import MongoClient
import os
from datetime import datetime, timedelta
from Files_A import file_type_a
from Files_B import file_type_b

database_name = "db_borme_empresas"
DATABASE_URI = "mongodb+srv://smart-escrow:borme@atlascluster.u9utedk.mongodb.net/?retryWrites=true&w=majority"




# ---------------------------------------------------- CONEXION A MONGO --------------------------------------------
def dbConnection():
    try:
        client = MongoClient(DATABASE_URI)
        db = client[database_name]
        print("Conexión exitosa")
        return db
    except Exception as e:
        print(f'Error al conectar a la DB: {e}')
        return None
# --------------------------------------------------VERIFICAR E INSERTAR COMPANY ---------------------------------------------------------
# Verifica si una compañía ya existe en la base de datos.
#Si la compañía existe, comprueba si hay nuevas inscripciones que agregar.
#Si la compañía no existe, la inserta en la base de datos.

def verificar_e_insertar_compania(db, company):
    # Buscar si la compañía ya existe en la base de datos
    existing_company = db['company'].find_one({'companyName': company['companyName']})

    if existing_company:
        # La compañía ya existe, verificar si la inscripción es nueva
        existing_inscription = db['company'].find_one({
            'companyName': company['companyName'],
            'companyInscription.inscriptionNumber': {'$in': [i['inscriptionNumber'] for i in company['companyInscription']]}
        })

        if not existing_inscription:
            # Agregar la nueva inscripción a la compañía existente
            db['company'].update_one(
                {'_id': existing_company['_id']},
                {'$push': {'companyInscription': {'$each': company['companyInscription']}}}
            )
            print(f"Inscripción agregada a la compañía existente: {company['companyName']}")
        else:
            print(f"La compañía e inscripción ya existen: {company['companyName']}")
    else:
        # La compañía no existe, insertarla nueva
        result = db['company'].insert_one(company)
        print(f"Nueva compañía insertada, ID: {result.inserted_id}")

# ------------------------------------------- GUARDAR EN UN TXT LOS BORME PROCESADOS Y CON ERRORES  -----------------------
# Guardo en un txt el ultimo archivo procesados correctamente y en otro la lista de todos los archivos con error
       
def guardar_registro_archivo(nombre_archivo, fecha_archivo, ruta_archivo_registros):
    # Sobrescribe el archivo con el nombre del último archivo procesado correctamente
    with open(ruta_archivo_registros, 'w') as archivo:
        archivo.write(f"{nombre_archivo} - {fecha_archivo} - PROCESADO\n")  

def guardar_registro_error(nombre_archivo, fecha_archivo, ruta_archivo_errores):
    # Agrega el nombre de todos los archivos con error a un archivo de texto separado
    with open(ruta_archivo_errores, 'a') as archivo:
        archivo.write(f"{nombre_archivo} - {fecha_archivo} - ERROR\n")
       

# ---------------------------------------------------- PROCESAMIENTO PDF  -------------------------------------------- 
#Procesa un archivo PDF individual.
#Extrae los datos del archivo PDF y los inserta en la base de datos.
#Registra el archivo como procesado o con error en el archivo de registro.

def procesar_pdf(db, ruta_archivo_registros, pdf_path,ruta_archivo_errores, archivos_procesados=None):
    nombre_archivo = os.path.basename(pdf_path)

    # Extraer la fecha del path del archivo
    partes_path = pdf_path.split('/')
    # Seleccionar las partes que corresponden a año, mes y día
    if len(partes_path) > 3:
        fecha_archivo = f"{partes_path[-5]}-{partes_path[-4]}-{partes_path[-3]}"
    else:
        fecha_archivo = "Fecha desconocida"

    if archivos_procesados and nombre_archivo in archivos_procesados:
        #print(f"Archivo ya procesado: {nombre_archivo}")
        return
        
    print(f"Procesando archivo: {pdf_path} (Fecha: {fecha_archivo})")
    try:
        if nombre_archivo.startswith('BORME-A'):
            data_to_insert = file_type_a(pdf_path)
        elif nombre_archivo.startswith('BORME-B'):
            data_to_insert = file_type_b(pdf_path)
        else:
            raise ValueError(f"Tipo de archivo desconocido: {nombre_archivo}")
        
       
        if isinstance(data_to_insert, list):
            for company in data_to_insert:
                verificar_e_insertar_compania(db, company)
        # Guardar el registro del archivo procesado
        guardar_registro_archivo(nombre_archivo, fecha_archivo, ruta_archivo_registros)
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_path} (Fecha: {fecha_archivo})")
        # Guardar el registro del archivo con error
        guardar_registro_error(nombre_archivo, fecha_archivo, ruta_archivo_errores)
        
 # ----------------------------------------------------   --------------------------------------------  
 #Carga un conjunto de nombres de archivos que ya han sido procesados a partir de un archivo de texto.
 #Esto evita el reprocesamiento de archivos que ya han sido manejados.      
def cargar_archivos_procesados(ruta_archivo_registros):
    if not os.path.exists(ruta_archivo_registros):
        return set()

    with open(ruta_archivo_registros, 'r') as archivo:
        lineas = archivo.readlines()
        archivos_procesados = set(linea.split(' - ')[0].strip() for linea in lineas)
    return archivos_procesados        

# ----------------------------------------------------  -------------------------------------------- 
# Similar a la primera versión, pero también verifica si un archivo ya ha sido procesado antes de intentar procesarlo.

def procesar_pdf(db, ruta_archivo_registros, pdf_path, ruta_archivo_errores, archivos_procesados):
    nombre_archivo = os.path.basename(pdf_path)
    # Extraer la fecha del path del archivo
    partes_path = pdf_path.split('/')
    # Seleccionar las partes que corresponden a año, mes y día
    if len(partes_path) > 3:
        fecha_archivo = f"{partes_path[-5]}-{partes_path[-4]}-{partes_path[-3]}"
    else:
        fecha_archivo = "Fecha desconocida"

    if archivos_procesados and nombre_archivo in archivos_procesados:
        print(f"Archivo ya procesado: {nombre_archivo} (Fecha: {fecha_archivo})")
        return
        
    print(f"Procesando archivo: {pdf_path} (Fecha: {fecha_archivo})")
    try:
        if nombre_archivo.startswith('BORME-A'):
            data_to_insert = file_type_a(pdf_path)
        elif nombre_archivo.startswith('BORME-B'):
            data_to_insert = file_type_b(pdf_path)
        else:
            raise ValueError(f"Tipo de archivo desconocido: {nombre_archivo}")
        
        if isinstance(data_to_insert, list):
            for company in data_to_insert:
                # Establecer las fechas para la compañía
                company['createdAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                company['updatedAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for inscription in company['companyInscription']:
                    # Establecer las fechas para cada inscripción
                    inscription['createdAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    inscription['updatedAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                verificar_e_insertar_compania(db, company)
        guardar_registro_archivo(nombre_archivo, fecha_archivo, ruta_archivo_registros)
    except Exception as e:
        print(f"Error al procesar el archivo {nombre_archivo} (Fecha: {fecha_archivo}): {e}")
        guardar_registro_error(nombre_archivo, fecha_archivo, ruta_archivo_errores)
        
# ----------------------------------------------------------------------------------------------------
def obtener_ultimo_archivo_procesado(ruta_archivo_registros):
    if not os.path.exists(ruta_archivo_registros):
        return 2009, 1, 1  # Valores por defecto si el archivo no existe

    with open(ruta_archivo_registros, 'r') as archivo:
        for linea in reversed(archivo.readlines()):
            if "PROCESADO" in linea:
                _, fecha, _ = linea.split(' - ')
                año, mes, día = map(int, fecha.split('-'))
                return año, mes, día
    return None  

def obtener_fecha_inicio_procesamiento(última_fecha_procesada):
    # Convertir a objeto datetime y sumar un día
    fecha_inicio = datetime(última_fecha_procesada[0], última_fecha_procesada[1], última_fecha_procesada[2]) + timedelta(days=1)
    return fecha_inicio.year, fecha_inicio.month, fecha_inicio.day 
        

# ----------------------------------------------------   -------------------------------------------- 
# Procesa archivos PDF en un directorio específico, ordenándolos por año, mes y día.
# Maneja archivos de tipo 'BORME-A', 'BORME-B', 'BORME-C' y 'BORME-S', aunque actualmente solo procesa archivos 'BORME-A'.

def procesar_pdfs_por_orden_y_tipo(directory, db, ruta_archivo_registros, ruta_archivo_errores, archivos_procesados, año_inicio, mes_inicio, día_inicio):
    archivos_procesados_contador = 0
    año_actual_procesado = False
    mes_actual_procesado = False

    for year in sorted(os.listdir(directory)):
        año_actual = int(year)
        if año_actual < año_inicio:
            continue

        path_year = os.path.join(directory, year)
        if os.path.isdir(path_year):
            for month in sorted(os.listdir(path_year)):
                mes_actual = int(month)
                if año_actual == año_inicio and mes_actual < mes_inicio:
                    continue

                path_month = os.path.join(path_year, month)
                if os.path.isdir(path_month):
                    for day in sorted(os.listdir(path_month)):
                        día_actual = int(day)
                        if año_actual == año_inicio and mes_actual == mes_inicio and día_actual < día_inicio:
                            continue

                        path_day = os.path.join(path_month, day, 'pdfs')
                        if os.path.isdir(path_day):
                            archivos = sorted([f for f in os.listdir(path_day) if f.lower().endswith('.pdf')])
                            for archivo in archivos:
                                if archivo.startswith('BORME-A'):
                                    procesar_pdf(db, ruta_archivo_registros, os.path.join(path_day, archivo), ruta_archivo_errores, archivos_procesados)
                                    archivos_procesados_contador += 1
                                if archivo.startswith('BORME-B'):
                                    procesar_pdf(db, ruta_archivo_registros, os.path.join(path_day, archivo), ruta_archivo_errores, archivos_procesados)
                                    archivos_procesados_contador += 1    

                    mes_actual_procesado = True
            año_actual_procesado = True

            if año_actual_procesado:
                año_inicio = año_actual + 1
                mes_inicio = 1  # Reiniciar mes al comienzo del siguiente año
                día_inicio = 1  # Reiniciar día al comienzo del siguiente año
            elif mes_actual_procesado:
                mes_inicio = mes_actual + 1
                día_inicio = 1  # Reiniciar día al comienzo del siguiente mes
      
                #for archivo in archivos:
                # if archivo.startswith(('BORME-B', 'BORME-C', 'BORME-S')) and not archivo.startswith('BORME-A'):
                #    procesar_pdf(db, ruta_archivo_registros, os.path.join(path_day, archivo),ruta_archivo_errores, archivos_procesados)
    return archivos_procesados_contador



if __name__ == '__main__':
    directory = '/home/soledad/BD.BORME-Empresas/files/pruebas chicas/prueba_A'
    db = dbConnection()
    ruta_archivo_registros = '/home/soledad/BD.BORME-Empresas/files/ultimo_archivo_procesadoAyB.txt'
    ruta_archivo_errores = '/home/soledad/BD.BORME-Empresas/files/archivos_con_errorAyB.txt'
    archivos_procesados = cargar_archivos_procesados(ruta_archivo_registros)
    # Obtener el año y mes del último archivo procesado
    archivos_procesados_en_esta_ejecución = 0

    resultado_fecha = obtener_ultimo_archivo_procesado(ruta_archivo_registros)
    if resultado_fecha:
        año_inicio, mes_inicio, día_inicio = obtener_fecha_inicio_procesamiento(resultado_fecha)
        archivos_procesados_en_esta_ejecución = procesar_pdfs_por_orden_y_tipo(directory, db, ruta_archivo_registros, ruta_archivo_errores, archivos_procesados, año_inicio, mes_inicio, día_inicio)
    else:
        print("No se encontró el último archivo procesado o el archivo de registros está vacío.")

    if archivos_procesados_en_esta_ejecución == 0:
        print("No hay más archivos para procesar.")
