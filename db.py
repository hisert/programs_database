import json

class JSONDatabase:
    def __init__(self, filename="data.json"):
        self.filename = filename

    def load_data(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            self.save_data({})
            return {}

    def save_data(self, data):
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

    def set_data(self, key, value):
        data = self.load_data()
        data[key] = value
        self.save_data(data)

    def get_data(self, key):
        data = self.load_data()
        return data.get(key, None)
