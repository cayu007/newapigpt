from flask import Flask, request, jsonify
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import uuid

app = Flask(__name__)

# Configuración de Azure Cosmos DB
endpoint = "https://cayu.documents.azure.com:443/"
key = "Zhedb71jSLiJW17vKZ6GIrmBBNGdO6GhxqTdqyPLdYNKbLv9vl7nQE7OTEPvAl4G6lyQHvJASOtdACDb7NS0Ug=="
database_name = "ToDoList"
container_name = "Items"

# Configuración de Azure Blob Storage
storage_connection_string = "DefaultEndpointsProtocol=https;AccountName=apigptokok;AccountKey=MKh1TJKpb2oJfP+rsgaHwrqqk9dA75xP1H7yktaGuBd528K/HAXLN1brq9h0ZjsmjmJfdMTZanS7+AStmyuASg==;EndpointSuffix=core.windows.net"
blob_container_name = "datos"

# Crear una instancia del cliente Cosmos
cosmos_client = CosmosClient(endpoint, key)
database = cosmos_client.create_database_if_not_exists(id=database_name)
container = database.create_container_if_not_exists(
    id=container_name, 
    partition_key=PartitionKey(path="/miClaveDeParticion"),
    offer_throughput=400
)

# Crear una instancia del cliente Blob
blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
blob_container_client = blob_service_client.get_container_client(blob_container_name)

@app.route('/crearNombre', methods=['POST'])
def crear_nombre():
    data = request.json
    nombre = data.get('nombre')
    if not nombre:
        return jsonify({"error": "Nombre es requerido"}), 400

    # Generar un ID único para el documento
    doc_id = str(uuid.uuid4())

    # Crear un item con el ID y el nombre
    item = {'id': doc_id, 'nombre': nombre}

    # Añadir lógica para manejar la subida de archivos si está presente
    file = request.files.get('archivo')
    if file:
        blob_name = f"{doc_id}/{file.filename}"
        blob_client = blob_container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(file)

        # Guardar la URL del blob en el item
        item['archivo_url'] = blob_client.url

    container.create_item(item)
    return jsonify({"mensaje": "Nombre almacenado con éxito", "id": doc_id})

@app.route('/obtenerNombres', methods=['GET'])
def obtener_nombres():
    items = list(container.read_all_items(max_item_count=10))
    nombres = []
    for item in items:
        nombre = item.get('nombre') or item.get('miClaveDeParticion') or item['id']
        archivo_url = item.get('archivo_url', 'No disponible')
        nombres.append({"nombre": nombre, "archivo_url": archivo_url})
    return jsonify({"nombres": nombres})

@app.route('/agregarArchivo/<usuario_id>', methods=['POST'])
def agregar_archivo(usuario_id):
    file = request.files.get('archivo')
    if not file:
        return jsonify({"error": "Archivo es requerido"}), 400

    try:
        # Subir archivo a Blob Storage
        blob_name = f"{usuario_id}/{file.filename}"
        blob_client = blob_container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(file)

        # Actualizar Cosmos DB con la URL del archivo
        item = container.read_item(item=usuario_id, partition_key=usuario_id)
        item['archivo_url'] = blob_client.url
        container.replace_item(item=usuario_id, body=item)

        return jsonify({"mensaje": "Archivo agregado con éxito"})
    except exceptions.CosmosResourceNotFoundError:
        return jsonify({"error": "Usuario no encontrado"}), 404
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



