from Config import Config
from typing import List, Any

config = Config()


class Weaviate:
    def __init__(self, openai_api_key: str):
        pass

    def add_list(self, datas: list, skill_name: str):
        pass

    def get(self, data: str):
        pass

    def clear(self) -> str:
        pass

    def get_relevant(self, data: str, num_relevant: int = 5) -> List[str]:
        pass

    def delete(self, where: dict = {}) -> Any:
        pass

    def delete_uuids(self, uuuids: List[str]) -> None:
        pass
