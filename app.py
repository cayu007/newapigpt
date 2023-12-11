from flask import Flask, request, jsonify
from azure.cosmos import CosmosClient, PartitionKey, exceptions

app = Flask(__name__)

# Configuración de Azure Cosmos DB
endpoint = "https://cayu.documents.azure.com:443/"
key = "hgvaBeJuUTKHvASooOGTcljYtTUbHvMIYosFyPJaoRSQ258k8IuiUTNby4bFxqhk1OdT80kIfBUjACDbyDXbPQ=="
client = CosmosClient(endpoint, key)
database_name = 'ToDoList'
database = client.create_database_if_not_exists(id=database_name)
container_name = 'Items'
container = database.create_container_if_not_exists(
    id=container_name, 
    partition_key=PartitionKey(path="/nombre"),
    offer_throughput=400
)

def leer_datos():
    try:
        query = "SELECT * FROM c"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        return items
    except Exception as e:
        print(e)
        return []

def guardar_datos(nombre):
    try:
        container.create_item({"id": nombre, "nombre": nombre})
    except Exception as e:
        print(e)

@app.route('/crearNombre', methods=['POST'])
def crear_nombre():
    data = request.json
    nombre = data.get('nombre')
    if not nombre:
        return jsonify({"error": "Nombre es requerido"}), 400
    
    guardar_datos(nombre)
    return jsonify({"mensaje": "Nombre almacenado con éxito"})

@app.route('/obtenerNombres', methods=['GET'])
def obtener_nombres():
    datos = leer_datos()
    nombres = [item['nombre'] for item in datos]
    return jsonify({"nombres": nombres})

if __name__ == '__main__':
    app.run(debug=True)
