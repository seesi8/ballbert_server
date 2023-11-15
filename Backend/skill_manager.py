import importlib
import os
import re
import shutil
import uuid
from git import Repo
import yaml

def rmtree_hard(path, _prev=None):
    try:
        shutil.rmtree(path)
    except PermissionError as e:
        if e == _prev:
            return
        match = re.search(r"Access is denied: '(.*)'", str(e))
        if match:
            file_path = match.group(1)
            os.chmod(file_path, 0o777)

            # Delete the file
            os.remove(file_path)
            rmtree_hard(path, _prev=e)
        else:
            raise e
        
def check_if_skill_is_alright(skill_name :str, skill_version: str | None, skill_uuid: str) -> bool:
    """checks if a skill is ok

    Args:
        skill_name (str): the name of the skill
        skill_version (float): the version of the skill
        skill_uuid (str): the uuid of the skill
    """

    
    is_valid =  is_folder_valid(skill_name, skill_uuid)
    

    return is_valid



def check_valid_python_code(code):
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        return False

def remove_skill(skill_uuid: str):
    skill_path = os.path.join("./Data/temp", skill_uuid)
    if os.path.exists(skill_path):
        rmtree_hard(skill_path)
    
    
def ready_temp_dir():
    if not os.path.exists("./Data/temp"):
        os.mkdir("./Data/temp")

def clone_skill(skill_url: str, skill_uuid: SyntaxError) -> Repo:
    """clones the skill from the url into a subfolder in the temp directory named the skill_uuid ex. ./Data/temp/skill_uuid

    Args:
        skill_url (str): the url of the skill
        skill_uuid (_type_): the temporary uuid of the skill
    
    Returns:
        (Repo) the repo object
    """
    repo = Repo.clone_from(skill_url, os.path.join("./Data/temp", skill_uuid))
    
    return repo

def is_folder_valid(name: str, uuid: str) -> bool:
        # Read the config file
        
        try:
            folder_path = os.path.join("./Data/temp", uuid)

            config_file_path = os.path.join(folder_path, "config.yaml")
            with open(config_file_path, "r") as config_file:
                config = yaml.safe_load(config_file)

            # Get the name from the config
            config_name = config.get("name")
            
            if config_name != name:
                print("not equal", config_name, name)
                return False

            # Check if the name matches a file in the folder
            file_names = os.listdir(folder_path)
            if f"{name}.py" not in file_names:
                print("name not in file names")
                return False

            # Check if the folder contains a class with the same name
            module_file_path = os.path.join(folder_path, f"{name}.py")
            if not os.path.isfile(module_file_path):
                print("module file path not a file")
                return False

            # Read the file contents
            with open(module_file_path, "r") as module_file:
                file_contents = module_file.read()

            # Check if the class with the same name exists in the file
            if f"class {name}" not in file_contents:
                print("class name not in file contents")
                return False

            if not check_valid_python_code(file_contents):
                return False

        except Exception as e:
            print(e)
            return False
        return True

def get_skill_requirements(skill_uuid):
    config_file_path = os.path.join("./Data/temp", skill_uuid, "config.yaml")
    
    with open(config_file_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    
    requirements = config.get("requirements", [])
    
    return requirements
        

def get_name(skill_uuid):
    config_file_path = os.path.join("./Data/temp", skill_uuid, "config.yaml")
    
    with open(config_file_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    
    requirements = config.get("name", '')
    
    return requirements
        
