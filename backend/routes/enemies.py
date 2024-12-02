from flask import Blueprint, request, jsonify

enemies_bp = Blueprint('enemies', __name__)
enemies = []

@enemies_bp.route('/add', methods=['POST'])
def add_enemy():
    data = request.json
    if data not in enemies:
        enemies.append(data)
    return jsonify({"message": "Enemy added", "enemies": enemies})

@enemies_bp.route('/list', methods=['GET'])
def list_enemies():
    return jsonify(enemies)
