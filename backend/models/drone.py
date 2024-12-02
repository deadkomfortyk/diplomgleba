class Drone:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def to_dict(self):
        return {"lat": self.lat, "lng": self.lng}
