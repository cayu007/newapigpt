from flask import Flask, request, jsonify
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__)

# Configuración directa de Azure Cosmos DB
endpoint = "https://cayu.documents.azure.com:443/"
key = "WJgGNXaeczY5lFKTl0ayEl0YNnkBvzlMLGHSUeqssMCYCvpV3JS6HD62kObSiqwmwBf5UVhXUJdGACDbSH7T2A=="
database_name = "ToDoList"
container_name = "Items"

# Crear una instancia del cliente Cosmos
client = CosmosClient(endpoint, key)

# Crear una base de datos si no existe
try:
    database = client.create_database_if_not_exists(id=database_name)
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(database_name)

# Crear un contenedor si no existe
try:
    container = database.create_container_if_not_exists(
        id=container_name, 
        partition_key=PartitionKey(path="/miClaveDeParticion"),
        offer_throughput=400
    )
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(container_name)

# Funciones para interactuar con Cosmos DB
def crear_item(item):
    try:
        container.create_item(item)
    except exceptions.CosmosHttpResponseError as e:
        print('Error al crear el item:', e)

def obtener_items():
    try:
        items = list(container.read_all_items(max_item_count=10))
        return items
    except exceptions.CosmosHttpResponseError as e:
        print('Error al leer los items:', e)
        return []

def actualizar_item(id_item, updated_item):
    try:
        container.replace_item(item=id_item, body=updated_item)
    except exceptions.CosmosHttpResponseError as e:
        print('Error al actualizar el item:', e)

def eliminar_item(id_item, partition_key):
    try:
        container.delete_item(item=id_item, partition_key=partition_key)
    except exceptions.CosmosHttpResponseError as e:
        print('Error al eliminar el item:', e)

# Rutas de la aplicación Flask
@app.route('/crearNombre', methods=['POST'])
def crear_nombre():
    data = request.json
    nombre = data.get('nombre')
    if not nombre:
        return jsonify({"error": "Nombre es requerido"}), 400
    
    crear_item({'id': nombre, 'miClaveDeParticion': nombre})
    return jsonify({"mensaje": "Nombre almacenado con éxito"})

@app.route('/obtenerNombres', methods=['GET'])
def obtener_nombres():
    datos = obtener_items()
    nombres = [item['id'] for item in datos]
    return jsonify({"nombres": nombres})

if __name__ == '__main__':
    app.run(debug=True)


