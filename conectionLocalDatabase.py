from pymongo import MongoClient
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

if __name__ == '__main__':
    db = dbConnection()
    if db is not None:
        # Llamar a file_type_a con la ruta del PDF
        pdf_path = "files/BORME-A-2010-210-13.pdf"
        data_to_insert = file_type_a(pdf_path)

        # Imprimir el tipo de data_to_insert
        print("Tipo de data_to_insert:", type(data_to_insert))

        # Verificar la estructura de un elemento
        if isinstance(data_to_insert, list) and data_to_insert:
            print("Ejemplo de documento a insertar:", data_to_insert[0])
        else:
            print("data_to_insert no es una lista o está vacía")

        # Insertar los documentos en MongoDB
        if isinstance(data_to_insert, list):
            for company in data_to_insert:
                try:
                    result = db['company'].insert_one(company)
                    print(f"Documento insertado, ID: {result.inserted_id}")
                except Exception as e:
                    print(f"Error al insertar el documento: {e}")
