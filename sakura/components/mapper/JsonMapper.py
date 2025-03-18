from sakura.interface.Mapper import Mapper


class JsonMapper(Mapper):
    key_mapping = {
        "1Key0": "C4", "1Key1": "D4", "1Key2": "E4", "1Key3": "F4", "1Key4": "G4",
        "1Key5": "A4", "1Key6": "B4", "1Key7": "C5", "1Key8": "D5", "1Key9": "E5",
        "1Key10": "F5", "1Key11": "G5", "1Key12": "A5", "1Key13": "B5", "1Key14": "C6",
        "2Key0": "C4", "2Key1": "D4", "2Key2": "E4", "2Key3": "F4", "2Key4": "G4",
        "2Key5": "A4", "2Key6": "B4", "2Key7": "C5", "2Key8": "D5", "2Key9": "E5",
        "2Key10": "F5", "2Key11": "G5", "2Key12": "A5", "2Key13": "B5", "2Key14": "C6"
    }

    def get_key_mapping(self):
        return self.key_mapping
