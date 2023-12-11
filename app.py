from flask import Flask, request, jsonify
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import uuid

app = Flask(__name__)

# Configuración de Azure Cosmos DB
endpoint = "https://cayu.documents.azure.com:443/"
key = "WJgGNXaeczY5lFKTl0ayEl0YNnkBvzlMLGHSUeqssMCYCvpV3JS6HD62kObSiqwmwBf5UVhXUJdGACDbSH7T2A=="
database_name = "ToDoList"
container_name = "Items"

# Configuración de Azure Blob Storage
storage_connection_string = "AccountEndpoint=https://cayu.documents.azure.com:443/;AccountKey=WJgGNXaeczY5lFKTl0ayEl0YNnkBvzlMLGHSUeqssMCYCvpV3JS6HD62kObSiqwmwBf5UVhXUJdGACDbSH7T2A==;"
blob_container_name = "documentos"

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
    nombres = [{"nombre": item['nombre'], "archivo_url": item.get('archivo_url')} for item in items]
    return jsonify({"nombres": nombres})

if __name__ == '__main__':
    app.run(debug=True)



