from pymongo import MongoClient
import os
from main import file_type_a


mongo_host = "localhost"
mongo_port = "27017"
database_name = "db_borme_empresas"
DATABASE_URI = f"mongodb://{mongo_host}:{mongo_port}/{database_name}"

def dbConnection():
    try:
        client = MongoClient(DATABASE_URI)
        db = client[database_name]
        print("Conexión exitosa")
        return db
    except Exception as e:
        print(f'Error al conectar a la DB: {e}')
        return None

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

# Ejemplo de uso en el bucle principal
if __name__ == '__main__':
    directory = '/home/soledad/BD.BORME-Empresas/files'
    db = dbConnection()

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf') and 'borme-a' in file.lower():
                pdf_path = os.path.join(root, file)
                print(f"Procesando archivo: {pdf_path}")
                data_to_insert = file_type_a(pdf_path)

                if isinstance(data_to_insert, list):
                    for company in data_to_insert:
                        verificar_e_insertar_compania(db, company)
