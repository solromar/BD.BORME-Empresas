from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import re

# Asegúrate de reemplazar esto con tus propias credenciales y nombres
AZURE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=ifinancierastorage;AccountKey=FvDbRrrMUAafYuY77xolcJMR4TrywKaEW7iE3ouNfcqmVLt0PRxurQ8GGruKXVwRb+uQ7H8jBDEL+AStG2gNdw==;EndpointSuffix=core.windows.net'
CONTAINER_NAME = "borme"

# ---------------------------------------------------- PROCESAMIENTO PDF -------------------------------------------- 
def procesar_pdf(blob_name, fecha_archivo):
    print(f"Procesando archivo: {blob_name} (Fecha: {fecha_archivo})")
    # Aquí iría el código para procesar el blob si fuera necesario
    # Por ahora, solo imprime que el archivo está siendo procesado.

# ---------------------------------------------------- OBTENER FECHA DE INICIO DE PROCESAMIENTO ---------------------
def obtener_fecha_inicio_procesamiento(última_fecha_procesada):
    fecha_inicio = datetime(última_fecha_procesada[0], última_fecha_procesada[1], última_fecha_procesada[2]) + timedelta(days=1)
    return fecha_inicio.year, fecha_inicio.month, fecha_inicio.day 

# ---------------------------------------------------- PROCESAR BLOBS POR ORDEN Y TIPO ------------------------------
def procesar_blobs_por_orden_y_tipo(blob_service_client, container_name, año_inicio, mes_inicio, día_inicio):
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs()

    for blob in blobs:
        print(f"Ruta del blob: {blob.name}")  # Imprimir la ruta para entender la estructura
        partes_ruta = blob.name.split('/')

        if len(partes_ruta) >= 7 and partes_ruta[-2] == 'pdfs' and partes_ruta[-1].endswith('.pdf'):
            try:
                año_blob, mes_blob, día_blob = int(partes_ruta[2]), int(partes_ruta[3]), int(partes_ruta[4])
                if (año_blob > año_inicio or
                    (año_blob == año_inicio and mes_blob > mes_inicio) or
                    (año_blob == año_inicio and mes_blob == mes_inicio and día_blob >= día_inicio)):
                    fecha_archivo = f"{año_blob}-{mes_blob}-{día_blob}"
                    print(f"Procesando archivo: {blob.name} (Fecha: {fecha_archivo})")
                    # Aquí iría la lógica para procesar el archivo
                    # ...
            except ValueError:
                print(f"Error al procesar la fecha en la ruta del blob: {blob.name}")
        else:
            continue

# Llamar a la función con los parámetros apropiados

# ---------------------------------------------------- MAIN ----------------------------------------------------------
if __name__ == '__main__':
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

    # Estos valores deberían ser obtenidos de tu archivo de registros
    año_inicio, mes_inicio, día_inicio = 2023, 1, 2  # Ajustar según  necesidades

    procesar_blobs_por_orden_y_tipo(blob_service_client, CONTAINER_NAME, año_inicio, mes_inicio, día_inicio)
