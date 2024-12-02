class Enemy:
    def __init__(self, lat, lng, radius):
        self.lat = lat
        self.lng = lng
        self.radius = radius

    def to_dict(self):
        return {"lat": self.lat, "lng": self.lng, "radius": self.radius}
