from sakura.interface.Mapper import Mapper


class JsonMapper(Mapper):
    key_mapping = {
        "1Key0": "C", "1Key1": "D", "1Key2": "E", "1Key3": "F", "1Key4": "G",
        "1Key5": "A", "1Key6": "B", "1Key7": "C1", "1Key8": "D1", "1Key9": "E1",
        "1Key10": "F1", "1Key11": "G1", "1Key12": "A1", "1Key13": "B1", "1Key14": "C2",
        "2Key0": "C", "2Key1": "D", "2Key2": "E", "2Key3": "F", "2Key4": "G",
        "2Key5": "A", "2Key6": "B", "2Key7": "C1", "2Key8": "D1", "2Key9": "E1",
        "2Key10": "F1", "2Key11": "G1", "2Key12": "A1", "2Key13": "B1", "2Key14": "C2"
    }

    def get_key_mapping(self):
        return self.key_mapping
