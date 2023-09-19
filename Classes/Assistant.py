import inspect
import os
import time

from .SkillMangager import SkillMangager
from Classes import Weaviate, Websocket_Client
from Config import Config

config = Config()


class NoVoiceException(Exception):
    pass


class Assistant:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.action_dict = dict()
        self.installed_skills = dict()
        self.pm = None
        self.websocket_client: Websocket_Client = Websocket_Client()

        self.porcupine_api_key = ""
        self.openai_api_key = ""

        time.sleep(1)
        self.setup_config()

        time.sleep(5)
        self.pm = Weaviate(self.openai_api_key)
        self.skill_manager = SkillMangager(self.openai_api_key)
        voice = self.setup_voice()
        self.voice = voice

    def setup_config(self):
        pass

    def setup_voice(self):
        pass

    def voice_to_voice_chat(self):
        pass


# Module-level variable to store the shared instance
assistant = None


# Initialization function to create the instance
def initialize_assistant():
    pass
