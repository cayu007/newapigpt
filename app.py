from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
datos_path = 'datos/nombres.json'

def leer_datos():
    if not os.path.exists(datos_path):
        return {"nombres": []}
    with open(datos_path, 'r') as file:
        return json.load(file)

def guardar_datos(datos):
    with open(datos_path, 'w') as file:
        json.dump(datos, file, indent=4)

@app.route('/crearNombre', methods=['POST'])
def crear_nombre():
    data = request.json
    nombre = data.get('nombre')
    if not nombre:
        return jsonify({"error": "Nombre es requerido"}), 400
    
    datos = leer_datos()
    datos['nombres'].append(nombre)
    guardar_datos(datos)
    
    return jsonify({"mensaje": "Nombre almacenado con éxito"})

@app.route('/obtenerNombres', methods=['GET'])
def obtener_nombres():
    datos = leer_datos()
    return jsonify(datos)

if __name__ == '__main__':
    app.run(debug=True)
