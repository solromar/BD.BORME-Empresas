import os
import tempfile
import azure.functions as func
from Files_A import file_type_a
from pymongo import MongoClient
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient

database_name = "db_borme_empresas"
DATABASE_URI = os.environ.get('MONGODB_URI')
AZURE_CONNECTION_STRING = os.environ.get('AzureWebJobsStorage')
CONTAINER_NAME = "borme"

app = func.FunctionApp()

# ---------------------------------------------------- CONEXION A MONGO --------------------------------------------
def dbConnection():
    try:
        client = MongoClient(DATABASE_URI)
        db = client[database_name]
        print("Conected: ", db)
        return db
    except Exception as e:
        print(f'Error al conectar a la DB: {e}')
        return None
# --------------------------------------------------VERIFICAR E INSERTAR COMPANY ---------------------------------------------------------
# Verifica si una compañía ya existe en la base de datos.
#Si la compañía existe, comprueba si hay nuevas inscripciones que agregar.
#Si la compañía no existe, la inserta en la base de datos.
def verificar_o_crear_archivo(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        with open(ruta_archivo, 'w') as archivo:
            pass  # Crea el archivo vacío
            
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
        # print(f"Nueva compañía insertada, ID: {result.inserted_id}")

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
def cargar_archivos_procesados(ruta_archivo_registros):
    if not os.path.exists(ruta_archivo_registros):
        return set()

    with open(ruta_archivo_registros, 'r') as archivo:
        lineas = archivo.readlines()
        archivos_procesados = set(linea.split(' - ')[0].strip() for linea in lineas)
    return archivos_procesados        

# ----------------------------------------------------  -------------------------------------------- 
# Similar a la primera versión, pero también verifica si un archivo ya ha sido procesado antes de intentar procesarlo.
def procesar_pdf(blob_service_client, db, ruta_archivo_registros, blob, ruta_archivo_errores, archivos_procesados):
    partes_ruta = blob.name.split('/')
    nombre_archivo = partes_ruta[-1]
    año_blob, mes_blob, día_blob = int(partes_ruta[1]), int(partes_ruta[2]), int(partes_ruta[3])
    fecha_archivo = f"{año_blob}-{mes_blob}-{día_blob}"

    if archivos_procesados and nombre_archivo in archivos_procesados:
        print(f"Archivo ya procesado: {nombre_archivo} (Fecha: {fecha_archivo})")
        return

    try:
        # Descargar el blob a un archivo temporal y procesarlo
        with tempfile.NamedTemporaryFile() as temp_pdf:
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob.name)
            blob_data = blob_client.download_blob()
            blob_data.readinto(temp_pdf)  # Descargar el contenido del blob en el archivo temporal
            temp_pdf.seek(0)  # Retroceder al inicio del archivo

            # Llamar a file_type_a con el archivo temporal
            data_to_insert = file_type_a(temp_pdf.name)
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
    with open(ruta_archivo_registros, 'r') as archivo:
        content = archivo.readlines()
        if not os.path.exists(ruta_archivo_registros):
            return 2009, 1, 1  # Valores por defecto si el archivo no existe
        if content == []:
            return 2009, 1, 1  # Valores por defecto si el archivo esta vacio
        for linea in content:
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
def procesar_blobs_por_orden_y_tipo(blob_service_client, db, ruta_archivo_registros, ruta_archivo_errores, archivos_procesados, año_inicio, mes_inicio, día_inicio):
    prefix = f"dias/{año_inicio}/{str(mes_inicio).zfill(2)}/"
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blobs = container_client.list_blobs(name_starts_with=prefix)
    archivos_procesados_contador = 0

    año_actual_procesado = False
    mes_actual_procesado = False

    for blob in sorted(blobs, key=lambda x: x.name):
        partes_ruta = blob.name.split('/')
        if partes_ruta[-2] == 'pdfs' and partes_ruta[-1].lower().endswith('.pdf'):
            try:
                año_blob, mes_blob, día_blob = int(partes_ruta[1]), int(partes_ruta[2]), int(partes_ruta[3])
                if (año_blob < año_inicio or (año_blob == año_inicio and mes_blob < mes_inicio) or (año_blob == año_inicio and mes_blob == mes_inicio and día_blob < día_inicio)):
                    continue

                if partes_ruta[-1].startswith('BORME-A'):
                    print(f"Procesando archivo: {blob.name} (Fecha: {año_blob}-{mes_blob}-{día_blob})")
                    procesar_pdf(blob_service_client, db, ruta_archivo_registros, blob, ruta_archivo_errores, archivos_procesados)
                    archivos_procesados_contador += 1
                    mes_actual_procesado = True
                año_actual_procesado = True

            except ValueError:
                print(f"Error al procesar la fecha en la ruta del blob: {blob.name}")

    if año_actual_procesado:
        año_inicio = año_blob + 1
        mes_inicio = 1  # Reiniciar mes al comienzo del siguiente año
        día_inicio = 1  # Reiniciar día al comienzo del siguiente año
    elif mes_actual_procesado:
        mes_inicio = mes_blob + 1
        día_inicio = 1  # Reiniciar día al comienzo del siguiente mes

    return archivos_procesados_contador, año_inicio, mes_inicio, día_inicio


@app.function_name(name="HttpProcessBorme")
@app.route(route="start")
async def main(req: func.HttpRequest) -> func.HttpResponse:
    db = dbConnection()
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    # Estos valores deberían ser obtenidos de tu archivo de registros

    # Construir rutas a los archivos utilizando el directorio base
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo_registros = os.path.join(directorio_base, 'files', 'ultimo_archivo_procesado.txt')
    ruta_archivo_errores = os.path.join(directorio_base, 'files', 'archivos_con_error.txt')

    # Verificar y crear archivos si no existen
    verificar_o_crear_archivo(ruta_archivo_registros)
    verificar_o_crear_archivo(ruta_archivo_errores)
    
    # Obtener el año y mes del último archivo procesado
    archivos_procesados = cargar_archivos_procesados(ruta_archivo_registros)
    archivos_procesados_en_esta_ejecución = 0

    resultado_fecha = obtener_ultimo_archivo_procesado(ruta_archivo_registros)
    if resultado_fecha:
        año_inicio, mes_inicio, día_inicio = obtener_fecha_inicio_procesamiento(resultado_fecha)
        archivos_procesados_en_esta_ejecución, año_inicio, mes_inicio, día_inicio = procesar_blobs_por_orden_y_tipo(blob_service_client, db, ruta_archivo_registros, ruta_archivo_errores, archivos_procesados, año_inicio, mes_inicio, día_inicio)
    else:
        print("No se encontró el último archivo procesado o el archivo de registros está vacío.")

    if archivos_procesados_en_esta_ejecución == 0:
        print("No hay más archivos para procesar.")
    return func.HttpResponse("Function processed a request!", status_code=200)