import os
import dotenv


class Config:
    def __init__(self):
        self.data = {}
        self.populate_values()

    def __getitem__(self, key, default=None):
        self.populate_values()
        return self.data.get(key, default)

    def __setitem__(self, key, value):
        os.environ[key] = value
        dotenv.load_dotenv()
        self.populate_values()
        self.data[key] = value

    def populate_values(self):

        for key, value in os.environ.items():
            if value == "True":
                self.data[key] = True
                continue
            elif value == "False":
                self.data[key] = False
                continue
            try:
                num = float(value)
                self.data[key] = num
                continue
            except:
                pass
            try:
                num = int(value)
                self.data[key] = num
                continue
            except:
                pass
            self.data[key] = value

    def __delitem__(self, key):
        self.populate_values()
        try:
            del self.data[key]
        except:
            pass

    def __contains__(self, key):
        self.populate_values()
        return key in self.data

    def __len__(self):
        self.populate_values()
        return len(self.data)

    def __str__(self):
        self.populate_values()
        return str(self.data)

    def keys(self):
        self.populate_values()
        return self.data.keys()

    def values(self):
        self.populate_values()
        return self.data.values()

    def items(self):
        self.populate_values()
        return self.data.items()
