from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json

app = Flask(__name__)

# Cadena de conexión de Azure Blob Storage
connect_str = "DefaultEndpointsProtocol=https;AccountName=apigptokok;AccountKey=MKh1TJKpb2oJfP+rsgaHwrqqk9dA75xP1H7yktaGuBd528K/HAXLN1brq9h0ZjsmjmJfdMTZanS7+AStmyuASg==;EndpointSuffix=core.windows.net"
container_name = "datos"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

def leer_datos():
    try:
        blob_client = container_client.get_blob_client(blob="nombres.json")
        blob_data = blob_client.download_blob().readall()
        return json.loads(blob_data)
    except Exception as e:
        print(e)
        return {"nombres": []}

def guardar_datos(datos):
    try:
        blob_client = container_client.get_blob_client(blob="nombres.json")
        blob_client.upload_blob(json.dumps(datos), overwrite=True)
    except Exception as e:
        print(e)

@app.route('/crearNombre', methods=['POST'])
def crear_nombre():
    data = request.json
    nombre = data.get('nombre')
    if not nombre:
        return jsonify({"error": "Nombre es requerido"}), 400
    
    datos = leer_datos()
    datos.setdefault('nombres', []).append(nombre)
    guardar_datos(datos)
    
    return jsonify({"mensaje": "Nombre almacenado con éxito"})

@app.route('/obtenerNombres', methods=['GET'])
def obtener_nombres():
    datos = leer_datos()
    return jsonify(datos)

if __name__ == '__main__':
    app.run(debug=True)
