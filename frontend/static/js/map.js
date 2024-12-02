// Ініціалізація карти з початковим шаром OpenStreetMap
const map = L.map('map', {
    minZoom: 6,
    maxZoom: 18
}).setView([50.4501, 30.5234], 6);

// Шар OpenStreetMap
const openStreetMapLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Шар ESRI Imagery
const esriLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; <a href="https://www.esri.com/">ESRI</a>'
});

// Шар підписів (кордони та назви міст)
const esriLabels = L.tileLayer(
    'https://services.arcgisonline.com/arcgis/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Дані © <a href="https://www.arcgis.com/">ArcGIS</a>',
        maxZoom: 18
    }
);

// Додавання перемикача шарів
const baseMaps = {
    "OpenStreetMap": openStreetMapLayer,
    "ESRI Satellite": esriLayer,
    "ESRI Satellite + Labels": L.layerGroup([esriLayer, esriLabels]) // Комбінуємо Imagery та Labels
};

L.control.layers(baseMaps).addTo(map);

// Змінні
let droneMarker = null;
let enemyMarkers = [];
let startPoint = null;
let endPoint = null;
let startCircle = null;
let endCircle = null;
let routeLine = null;

// Стиль маршруту
const routeStyle = {
    color: 'blue',
    weight: 5,
    opacity: 0.8,
    smoothFactor: 1.5
};

// Специфічні іконки для старту, фінішу та дрона
const startIcon = L.icon({
    iconUrl: '/static/img/marker.png',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
});

const endIcon = L.icon({
    iconUrl: '/static/img/marker.png',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
});

const droneIcon = L.icon({
    iconUrl: '/static/img/drone.png',
    iconSize: [22, 22],
    iconAnchor: [11, 11]
});

// Оновлення стану кнопки "Розрахувати маршрут"
function updateCalculateButtonState() {
    const calculateRouteButton = document.getElementById('calculate-route-btn');
    calculateRouteButton.disabled = !(startPoint && endPoint && droneMarker);
}

// Додавання дрона
document.getElementById('add-drone-btn').addEventListener('click', () => {
    map.once('click', (e) => {
        if (droneMarker) map.removeLayer(droneMarker);
        droneMarker = L.marker(e.latlng, { icon: droneIcon }).addTo(map);
        alert(`Дрон додано на координати: ${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`);
        updateCalculateButtonState();
    });
});

// Додавання ворога
document.getElementById('add-enemy-btn').addEventListener('click', () => {
    map.once('click', (e) => {
        const radius = prompt("Введіть радіус ураження ворога (в км):", "5");

        if (!radius || isNaN(radius) || radius <= 0) {
            alert("Некоректний радіус! Введіть додатне число.");
            return;
        }

        // Додаємо іконку ворога
        const enemyIcon = L.icon({
            iconUrl: '/static/img/enemy.png',
            iconSize: [25, 25],
            iconAnchor: [12, 12]
        });

        const enemyMarker = L.marker(e.latlng, { icon: enemyIcon }).addTo(map);

        // Додаємо круг для зони ураження
        const enemyCircle = L.circle(e.latlng, {
            radius: radius * 1000, // Перетворюємо радіус у метри
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.5
        }).addTo(map);

        // Зберігаємо інформацію про ворога
        enemyMarkers.push({
            marker: enemyMarker,
            circle: enemyCircle,
            lat: parseFloat(e.latlng.lat.toFixed(4)),
            lng: parseFloat(e.latlng.lng.toFixed(4)),
            radius: parseFloat(radius) * 1000
        });

        alert(`Ворог доданий: ${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)} з радіусом ${radius} км.`);
    });
});

// Розрахувати маршрут
document.getElementById('calculate-route-btn').addEventListener('click', () => {
    if (!startPoint || !endPoint || !droneMarker) {
        alert("Будь ласка, оберіть початкову, кінцеву точки та додайте дрон!");
        return;
    }

    const requestData = {
        start_lat: startPoint.lat,
        start_lng: startPoint.lng,
        end_lat: endPoint.lat,
        end_lng: endPoint.lng,
        enemies: enemyMarkers.map(marker => ({
            lat: marker.lat,
            lng: marker.lng,
            radius: marker.radius
        }))
    };

    fetch('http://127.0.0.1:5000/analyze/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`Помилка: ${data.error}`);
            return;
        }

        // Очищення попереднього маршруту
        if (routeLine) map.removeLayer(routeLine);

        // Відображення нового маршруту
        routeLine = L.polyline(data.route.map(coord => [coord[0], coord[1]]), routeStyle).addTo(map);
        map.fitBounds(routeLine.getBounds());
    })
    .catch(error => console.error('Помилка маршруту:', error));
});

// Вибір маршруту
document.getElementById('select-route-btn').addEventListener('click', () => {
    map.once('click', (e) => {
        startPoint = { lat: e.latlng.lat, lng: e.latlng.lng };
        if (startCircle) map.removeLayer(startCircle);
        startCircle = L.marker(e.latlng, { icon: startIcon }).addTo(map);

        map.once('click', (e) => {
            endPoint = { lat: e.latlng.lat, lng: e.latlng.lng };
            if (endCircle) map.removeLayer(endCircle);
            endCircle = L.marker(e.latlng, { icon: endIcon }).addTo(map);
            updateCalculateButtonState();
        });
    });
});

// Очищення карти
document.getElementById('clear-map-btn').addEventListener('click', () => {
    [droneMarker, startCircle, endCircle, routeLine].forEach(item => item && map.removeLayer(item));
    enemyMarkers.forEach(marker => {
        map.removeLayer(marker.circle);
        map.removeLayer(marker.marker);
    });

    droneMarker = startPoint = endPoint = routeLine = startCircle = endCircle = null;
    enemyMarkers = [];
    updateCalculateButtonState();
    alert("Карта очищена!");
});
