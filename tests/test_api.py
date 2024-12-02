import requests

BASE_URL = "http://127.0.0.1:5000"

def test_analyze_route_with_large_step():
    url = f"{BASE_URL}/analyze/route"
    data = {
        "start_lat": 50.4501,  # Київ
        "start_lng": 30.5234,
        "end_lat": 50.5,       # Кінцева точка у зоні ворога
        "end_lng": 23.5,
        "enemies": [
            {"lat": 50.5, "lng": 23.5, "radius": 50000}  # Ворог із радіусом ураження 50 км
        ]
    }
    response = requests.post(url, json=data)
    print("Analyze Route Response:", response.json())


if __name__ == "__main__":
    print("Running Tests...\n")
    test_analyze_route_with_large_step()

    print("\nAll tests passed!")
