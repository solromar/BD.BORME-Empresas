from azure.storage.blob import BlobServiceClient

def contar_pdfs_por_tipo_en_azure(contenedor_nombre, conexion_string):
    total_contador = 0
    borme_a_contador = 0
    borme_b_contador = 0
    borme_c_contador = 0
    borme_s_contador = 0

    blob_service_client = BlobServiceClient.from_connection_string(conexion_string)
    contenedor_client = blob_service_client.get_container_client(contenedor_nombre)

    blob_list = contenedor_client.list_blobs()

    for blob in blob_list:
        if blob.name.lower().endswith('.pdf'):
            total_contador += 1
            if 'borme-a' in blob.name.lower():
                borme_a_contador += 1
            elif 'borme-b' in blob.name.lower():
                borme_b_contador += 1
            elif 'borme-c' in blob.name.lower():
                borme_c_contador += 1
            elif 'borme-s' in blob.name.lower():
                borme_s_contador += 1

    return total_contador, borme_a_contador, borme_b_contador, borme_c_contador, borme_s_contador

# Reemplaza con tus propios valores
contenedor_nombre = 'borme'
conexion_string = 'DefaultEndpointsProtocol=https;AccountName=ifinancierastorage;AccountKey=FvDbRrrMUAafYuY77xolcJMR4TrywKaEW7iE3ouNfcqmVLt0PRxurQ8GGruKXVwRb+uQ7H8jBDEL+AStG2gNdw==;EndpointSuffix=core.windows.net'

total_pdfs, total_pdfs_borme_a, total_pdfs_borme_b, total_pdfs_borme_c, total_pdfs_borme_s = contar_pdfs_por_tipo_en_azure(contenedor_nombre, conexion_string)
print(f"Total de archivos PDF en Azure Blob Storage: {total_pdfs}")
print(f"Total de archivos PDF 'BORME-A': {total_pdfs_borme_a}")
print(f"Total de archivos PDF 'BORME-B': {total_pdfs_borme_b}")
print(f"Total de archivos PDF 'BORME-C': {total_pdfs_borme_c}")
print(f"Total de archivos PDF 'BORME-S': {total_pdfs_borme_s}")




