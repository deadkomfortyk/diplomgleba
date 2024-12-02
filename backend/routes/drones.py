from flask import Blueprint, request, jsonify

drones_bp = Blueprint('drones', __name__)
drones = []

@drones_bp.route('/add', methods=['POST'])
def add_drone():
    data = request.json
    if data not in drones:
        drones.append(data)
    return jsonify({"message": "Drone added", "drones": drones})

@drones_bp.route('/list', methods=['GET'])
def list_drones():
    return jsonify(drones)
