
import os

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"

NoneType = type(None)

def rmtree_hard(path, _prev=None):
    ...


def deepcopy(original_dict):
    ...


class SkillMangager:
    def __init__(self, openai) -> None:
        self.openai = openai


    def add_skill(self, assistant, skill):
        """Adds a skill to the memeory

        Keyword arguments:
        assistant -- Assistant instance
        assistant -- Name of skill
        Return: return_description
        """

        ...

    def add_skill_from_url(self, assistant, url: str, name: str):
        """downloads the skill from github

        Args:
            assistant (Assistant): The assistant instance
            url (str): the url of the skill
            name (str): the name of the skill

        Returns:
            dict: the new actions_dict of the skill
        """
        
        ...
