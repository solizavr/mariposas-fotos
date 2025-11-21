from database import db

if db is not None:
    print("Conexión establecida correctamente.")
    print("Colecciones disponibles:", db.list_collection_names())
else:
    print("No se pudo conectar a la base de datos.")
