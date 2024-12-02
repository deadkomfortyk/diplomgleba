import math
import networkx as nx
from pyproj import Transformer
from concurrent.futures import ThreadPoolExecutor

# Ініціалізація трансформера для перетворення координат
transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
transformer_back = Transformer.from_crs("epsg:3857", "epsg:4326", always_xy=True)

def project_coordinates(lat, lng):
    """Перетворення координат у метри (EPSG:3857)."""
    x, y = transformer.transform(lng, lat)
    return x, y

def unproject_coordinates(x, y):
    """Перетворення координат з метрів у географічні (EPSG:4326)."""
    lng, lat = transformer_back.transform(x, y)
    return lat, lng

def calculate_buffer_distance(radius):
    """Розраховує буферну відстань на основі радіуса зони ураження."""
    radius_km = radius / 1000  # Перетворюємо радіус в кілометри
    if radius_km < 100:
        buffer_km = 40
    else:
        buffer_km = 70
    buffer_meters = buffer_km * 1000  # Перетворюємо буфер в метри
    return buffer_meters

def is_point_in_enemy_zone(point, enemies):
    """Перевірка, чи точка знаходиться всередині будь-якої зони ураження з буфером."""
    for enemy in enemies:
        ex, ey = project_coordinates(enemy['lat'], enemy['lng'])
        radius = enemy['radius']
        buffer_distance = calculate_buffer_distance(radius)
        adjusted_radius = radius + buffer_distance
        distance = math.hypot(point[0] - ex, point[1] - ey)
        if distance <= adjusted_radius:
            return True
    return False

def line_intersects_circle(p1, p2, circle_center, circle_radius):
    """Перевіряє, чи перетинає відрізок коло."""
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = circle_center
    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - circle_radius * circle_radius
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False  # Немає перетину
    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)
    if (0 <= t1 <= 1) or (0 <= t2 <= 1):
        return True
    return False

def determine_grid_size(start, end):
    """Визначає розмір сітки залежно від відстані між точками."""
    sx, sy = project_coordinates(start[0], start[1])
    ex, ey = project_coordinates(end[0], end[1])
    distance = math.hypot(ex - sx, ey - sy)
    if distance > 500000:  # Якщо дистанція більше 500 км
        return 3000
    elif distance > 200000:  # Якщо дистанція більше 200 км
        return 2000
    else:
        return 1000

def generate_grid(start, end, enemies, grid_size):
    """Генерація сітки та графа для пошуку шляху."""
    # Визначаємо межі
    min_lat = min(start[0], end[0]) - 1
    max_lat = max(start[0], end[0]) + 1
    min_lng = min(start[1], end[1]) - 1
    max_lng = max(start[1], end[1]) + 1

    # Проектуємо межі в метри
    min_x, min_y = project_coordinates(min_lat, min_lng)
    max_x, max_y = project_coordinates(max_lat, max_lng)

    # Створюємо граф
    G = nx.Graph()

    # Генеруємо сітку
    x_coords = list(range(int(min_x), int(max_x), grid_size))
    y_coords = list(range(int(min_y), int(max_y), grid_size))

    # Створюємо вузли
    nodes = []
    for x in x_coords:
        for y in y_coords:
            if not is_point_in_enemy_zone((x, y), enemies):
                lat, lng = unproject_coordinates(x, y)
                G.add_node((x, y), pos=(lat, lng))
                nodes.append((x, y))

    # Зв'язуємо сусідні вузли
    for node in nodes:
        x, y = node
        neighbors = [
            (x + grid_size, y),
            (x - grid_size, y),
            (x, y + grid_size),
            (x, y - grid_size),
            (x + grid_size, y + grid_size),
            (x - grid_size, y - grid_size),
            (x + grid_size, y - grid_size),
            (x - grid_size, y + grid_size),
        ]
        for neighbor in neighbors:
            if neighbor in G.nodes:
                # Перевіряємо, чи ребро перетинає зони ураження
                intersects = False
                for enemy in enemies:
                    ex, ey = project_coordinates(enemy['lat'], enemy['lng'])
                    radius = enemy['radius']
                    buffer_distance = calculate_buffer_distance(radius)
                    adjusted_radius = radius + buffer_distance
                    if line_intersects_circle(node, neighbor, (ex, ey), adjusted_radius):
                        intersects = True
                        break
                if not intersects:
                    distance = math.hypot(neighbor[0] - x, neighbor[1] - y)
                    G.add_edge(node, neighbor, weight=distance)

    return G

def find_nearest_node(G, point):
    """Знаходить найближчий вузол графа до заданої точки."""
    x, y = project_coordinates(point[0], point[1])
    min_node = None
    min_distance = float('inf')
    for node in G.nodes:
        distance = math.hypot(node[0] - x, node[1] - y)
        if distance < min_distance:
            min_distance = distance
            min_node = node
    return min_node

def calculate_safe_route(start, end, enemies):
    """Розрахунок безпечного маршруту."""
    grid_size = determine_grid_size(start, end)  # Визначення розміру сітки
    G = generate_grid(start, end, enemies, grid_size=grid_size)

    # Знаходимо найближчі вузли до початку і кінця
    start_node = find_nearest_node(G, start)
    end_node = find_nearest_node(G, end)

    if start_node is None or end_node is None:
        print("Не вдалося знайти доступний шлях.")
        return None

    try:
        # Знаходимо найкоротший шлях
        path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
    except nx.NetworkXNoPath:
        print("Немає доступного шляху між початковою та кінцевою точками.")
        return None

    # Перетворюємо вузли в координати
    route = []
    for node in path:
        lat, lng = unproject_coordinates(node[0], node[1])
        route.append((lat, lng))

    # Додаємо початкову та кінцеву точки до маршруту
    route.insert(0, start)
    route.append(end)

    return route
