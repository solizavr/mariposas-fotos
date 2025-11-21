from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import certifi

# Cadena de conexión de mongo
MONGO_URI = "mongodb+srv://miguelsolis_db_user:geronimo@cluster0.04qbhl7.mongodb.net/?appName=Cluster0"

try:
    # Conectar a mongo atlas
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["mariposas_bd"]

    # Probar conexión
    client.admin.command("ping")
    print("Conectado exitosamente a MongoDB Atlas.")

except ConnectionFailure as e:
    print("Error de conexión:", e)
    db = None
