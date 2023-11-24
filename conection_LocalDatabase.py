from pymongo import MongoClient
import os
from datetime import datetime
from Files_A import file_type_a


mongo_host = "localhost"
mongo_port = "27017"
database_name = "db_borme_empresas"
DATABASE_URI = f"mongodb://{mongo_host}:{mongo_port}/{database_name}"

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
       
def guardar_registro_archivo(nombre_archivo, fecha_archivo, ruta_archivo_registros, es_error=False):
    # Sobrescribe el archivo con el nombre del último archivo procesado correctamente
    with open(ruta_archivo_registros, 'w') as archivo:
        archivo.write(f"{nombre_archivo} - {fecha_archivo} - PROCESADO\n")  

def guardar_registro_error(nombre_archivo, fecha_archivo, ruta_archivo_registros):
    # Agrega el nombre de todos los archivos con error a un archivo de texto separado
    with open(ruta_archivo_registros, 'a') as archivo:
        archivo.write(f"{nombre_archivo} - {fecha_archivo} - ERROR\n")
       

# ---------------------------------------------------- PROCESAMIENTO PDF  -------------------------------------------- 
#Procesa un archivo PDF individual.
#Extrae los datos del archivo PDF y los inserta en la base de datos.
#Registra el archivo como procesado o con error en el archivo de registro.

def procesar_pdf(db, ruta_archivo_registros, pdf_path, archivos_procesados=None):
    nombre_archivo = os.path.basename(pdf_path)

    # Extraer la fecha del path del archivo
    partes_path = pdf_path.split('/')
    # Seleccionar las partes que corresponden a año, mes y día
    if len(partes_path) > 3:
        fecha_archivo = f"{partes_path[-5]}-{partes_path[-4]}-{partes_path[-3]}"
        print(fecha_archivo)
    else:
        fecha_archivo = "Fecha desconocida"

    if archivos_procesados and nombre_archivo in archivos_procesados:
        print(f"Archivo ya procesado: {nombre_archivo}")
        return
        
    print(f"Procesando archivo: {pdf_path} (Fecha: {fecha_archivo})")
    try:
        data_to_insert = file_type_a(pdf_path)
        if isinstance(data_to_insert, list):
            for company in data_to_insert:
                verificar_e_insertar_compania(db, company)
        # Guardar el registro del archivo procesado
        guardar_registro_archivo(nombre_archivo, fecha_archivo, ruta_archivo_registros)
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_path} (Fecha: {fecha_archivo})")
        # Guardar el registro del archivo con error
        guardar_registro_error(nombre_archivo, fecha_archivo, ruta_archivo_registros)
        
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

def procesar_pdf(db, ruta_archivo_registros, pdf_path, archivos_procesados):
    nombre_archivo = os.path.basename(pdf_path)
    print (nombre_archivo)
    print (pdf_path)
    # Extraer la fecha del path del archivo
    partes_path = pdf_path.split('/')
    # Seleccionar las partes que corresponden a año, mes y día
    if len(partes_path) > 3:
        fecha_archivo = f"{partes_path[-5]}-{partes_path[-4]}-{partes_path[-3]}"
        print(fecha_archivo)    
    else:
        fecha_archivo = "Fecha desconocida"

    if archivos_procesados and nombre_archivo in archivos_procesados:
        print(f"Archivo ya procesado: {nombre_archivo} (Fecha: {fecha_archivo})")
        return
        
    print(f"Procesando archivo: {pdf_path} (Fecha: {fecha_archivo})")
    try:
        data_to_insert = file_type_a(pdf_path)
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
        guardar_registro_error(nombre_archivo, fecha_archivo, ruta_archivo_registros)

# ----------------------------------------------------   -------------------------------------------- 
# Procesa archivos PDF en un directorio específico, ordenándolos por año, mes y día.
# Maneja archivos de tipo 'BORME-A', 'BORME-B', 'BORME-C' y 'BORME-S', aunque actualmente solo procesa archivos 'BORME-A'.

def procesar_pdfs_por_orden_y_tipo(directory, db, ruta_archivo_registros, archivos_procesados):
    for year in sorted(os.listdir(directory)):
        path_year = os.path.join(directory, year)
        if os.path.isdir(path_year):
            for month in sorted(os.listdir(path_year)):
                path_month = os.path.join(path_year, month)
                if os.path.isdir(path_month):
                    for day in sorted(os.listdir(path_month)):
                        path_day = os.path.join(path_month, day, 'pdfs')
                        if os.path.isdir(path_day):
                            archivos = sorted([f for f in os.listdir(path_day) if f.lower().endswith('.pdf')])
                            for archivo in archivos:
                                if archivo.startswith('BORME-A'):
                                    procesar_pdf(db, ruta_archivo_registros, os.path.join(path_day, archivo), archivos_procesados)
                            for archivo in archivos:
                                if archivo.startswith(('BORME-B', 'BORME-C', 'BORME-S')) and not archivo.startswith('BORME-A'):
                                    procesar_pdf(db, ruta_archivo_registros, os.path.join(path_day, archivo), archivos_procesados)




if __name__ == '__main__':
    directory = '/home/soledad/BD.BORME-Empresas/files/pruebas chicas/prueba_A'
    db = dbConnection()
    ruta_archivo_registros = '/home/soledad/BD.BORME-Empresas/files/registro_archivos_prueba.txt'
    archivos_procesados = cargar_archivos_procesados(ruta_archivo_registros)

    procesar_pdfs_por_orden_y_tipo(directory, db, ruta_archivo_registros, archivos_procesados)
