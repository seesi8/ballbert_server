def reset():

    from Backend.db import MongoManager

    mongo_manager = MongoManager("mongodb://localhost:27017/", "Ballbert_Local", "Users")

    mongo_manager.clear_collection()

    mongo_manager.insert_document({"uid": "03560274-043C-0560-0106-120700080009"})

    print("reset")

if __name__ == "__main__":
    reset()