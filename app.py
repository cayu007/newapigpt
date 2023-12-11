from flask import Flask, request, jsonify
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import config

app = Flask(__name__)

# Configuración de Azure Cosmos DB desde config.py
HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

# Crear una instancia del cliente Cosmos
client = CosmosClient(HOST, {'masterKey': MASTER_KEY})

# Crear una base de datos si no existe
try:
    database = client.create_database(DATABASE_ID)
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(DATABASE_ID)

# Crear un contenedor si no existe
try:
    container = database.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path="/miClaveDeParticion"))
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(CONTAINER_ID)

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

# Ejemplo de uso
@app.route('/crearItem', methods=['POST'])
def crear_nombre():
    data = request.json
    crear_item(data)
    return jsonify({"mensaje": "Item creado con éxito"})

@app.route('/obtenerItems', methods=['GET'])
def obtener_nombres():
    items = obtener_items()
    return jsonify({"items": items})

@app.route('/actualizarItem/<id_item>', methods=['PUT'])
def actualizar_nombre(id_item):
    data = request.json
    actualizar_item(id_item, data)
    return jsonify({"mensaje": "Item actualizado con éxito"})

@app.route('/eliminarItem/<id_item>', methods=['DELETE'])
def eliminar_nombre(id_item):
    eliminar_item(id_item, request.args.get('partition_key'))
    return jsonify({"mensaje": "Item eliminado con éxito"})

if __name__ == '__main__':
    app.run(debug=True)


