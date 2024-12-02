import sys
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# Додаємо кореневу директорію до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.drones import drones_bp
from routes.enemies import enemies_bp
from routes.analyze import analyze_bp

# Ініціалізація Flask
app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend")
CORS(app)

# Реєструємо маршрути
app.register_blueprint(drones_bp, url_prefix="/drones")
app.register_blueprint(enemies_bp, url_prefix="/enemies")
app.register_blueprint(analyze_bp, url_prefix="/analyze")

# Маршрут для відображення фронтенду
@app.route('/')
def serve_frontend():
    return send_from_directory(app.template_folder, "index.html")

# Маршрут для статичних файлів
@app.route('/static/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)
