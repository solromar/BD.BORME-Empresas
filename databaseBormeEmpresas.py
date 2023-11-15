from pymongo import MongoClient
import certifi

mongo_host = "mongo"  # Nombre del servicio MongoDB en Lando
mongo_port = "27017"  # Puerto expuesto por MongoDB en Lando
database_name = "db_borme_empresas"  # Nombre de tu base de datos

# Construye la URI de conexión

#DATABASE_URI = 'mongodb+srv://smart-escrow:<borme>@atlascluster.u9utedk.mongodb.net/'
DATABASE_URI = f"mongodb://{mongo_host}:{mongo_port}/{database_name}"

ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient.connect(DATABASE_URI, tlsCAFile=ca)
        db = client["db_borme_empresas"]
    except ConnectionAbortedError:
        print('Error al conectar a la DB')  
    return db 


