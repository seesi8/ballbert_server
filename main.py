import os
from Config import Config
import dotenv

config = Config()

if __name__ == "__main__":
    if not os.path.exists("./Data/logs.log"):
        open("./Data/logs.log", "W")
        
    if os.path.exists("./Data/.env"):
        dotenv.load_dotenv("./Data/.env")
    
    import server