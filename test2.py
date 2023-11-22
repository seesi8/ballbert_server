import openai
from Config import Config
import numpy as np

config = Config()

def generate_embedding(text):
    try:
        response = openai.Embedding.create(model="text-embedding-ada-002", input=text)
    except:
        openai.api_key = config["OPENAI_API_KEY"]
        return generate_embedding(text)
    return np.array(response["data"][0]["embedding"])

print(generate_embedding("hi"))