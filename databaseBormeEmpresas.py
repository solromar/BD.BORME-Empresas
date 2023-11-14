from pymongo import MongoClient
import certifi

#MONGO_URI = 'mongodb+srv://smart-escrow:<borme>@atlascluster.u9utedk.mongodb.net/'
DATABASE_URI='mongodb://mongo:27017/db_borme_empresas'
ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient.connect(DATABASE_URI, tlsCAFile=ca)
        db = client["db_borme_empresas"]
    except ConnectionAbortedError:
        print('Error al conectar a la DB')  
    return db 


