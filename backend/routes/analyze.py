from flask import Blueprint, request, jsonify
from utils.calculate import calculate_safe_route

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/route', methods=['POST'])
def analyze_route():
    try:
        data = request.json
        print("Received data for route analysis:", data)

        # Витягуємо координати та дані про ворогів, з конвертацією в числа
        start = (float(data['start_lat']), float(data['start_lng']))
        end = (float(data['end_lat']), float(data['end_lng']))
        enemies = [
            {
                'lat': float(enemy['lat']),
                'lng': float(enemy['lng']),
                'radius': float(enemy['radius'])
            }
            for enemy in data.get('enemies', [])
        ]

        print(f"Start: {start}, End: {end}, Enemies: {enemies}")

        # Перевірка на наявність даних
        if not start or not end:
            return jsonify({"error": "Початкова або кінцева точка не вказана."}), 400

        # Розрахунок маршруту
        route = calculate_safe_route(start, end, enemies)

        if isinstance(route, dict) and 'error' in route:
            print("Route calculation failed:", route["error"])
            return jsonify({"error": route["error"]}), 400

        print("Calculated Route:", route)
        return jsonify({"route": route}), 200

    except KeyError as e:
        print(f"Missing required data: {e}")
        return jsonify({"error": f"Відсутнє обов'язкове поле: {str(e)}"}), 400
    except Exception as e:
        print(f"Unexpected error during route analysis: {e}")
        return jsonify({"error": "Непередбачена помилка при аналізі маршруту."}), 500
