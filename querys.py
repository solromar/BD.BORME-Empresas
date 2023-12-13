from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb+srv://smart-escrow:borme@atlascluster.u9utedk.mongodb.net/?retryWrites=true&w=majority")
db = client.db_borme_empresas
collection = db.company

# Fecha que quieres buscar
fecha_buscada = "02/01/2009"

# Realizar la consulta
resultados = collection.find({"companyInscription.bormeDate": fecha_buscada})

# Imprimir los resultados
for documento in resultados:
    print(documento)
