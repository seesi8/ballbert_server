from pymongo import MongoClient

name = input("name: ")

mongo_url="mongodb://localhost:27017/"

db_name="Ballbert_Local"

client = MongoClient(mongo_url)

db = client[db_name]

approved_skills = db["Approved_Skills"]

approved_skills.insert_one({"name": name, "approved": True})