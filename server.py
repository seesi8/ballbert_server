import base64
import os
import re
from typing import AsyncGenerator
import uuid
import zlib
from Backend.websocket import Server, Client_Assistant
import speech_recognition as sr
import openai
from MessageHandler import MessageHandler
from Backend.Action import Action, Parameter
from google.cloud import texttospeech
from Backend.db import MongoManager
from Config import Config
from Backend.skill_manager import check_if_skill_is_alright, ready_temp_dir, clone_skill, remove_skill, get_skill_requirements, get_name
from Backend.sentament import get_sentament
import logging

config = Config()
    
app = Server()

mongo_manager = MongoManager()

recogniser = sr.Recognizer()
openai.api_key = config["OPENAI_API_KEY"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./Data/creds.json"
punctuations = "!?."

@app.route("Authentication")
async def authentication(client: Client_Assistant, UID: str):
    return

@app.route()
async def foward(client: Client_Assistant, foward_type: str, kwargs: dict):
    await client.send_message(foward_type, kwargs)

@app.route()
async def echo(client: Client_Assistant, message):
    await client.send_message("echo", message=message)

@app.route()
async def approved_skills(client: Client_Assistant):
    skills = mongo_manager.get_approved_skills(client.uid)
    skills_names = [skill["name"] for skill in skills]
    
    await client.send_message("approved_skills", skills=skills_names)

@app.route()
async def get_porcupine_api_key(client: Client_Assistant):
    await client.send_message(
        "get_porcupine_api_key",
        key=config["PORQUPINE_API_KEY"],
    )


@app.route()
async def get_openai_api_key(client: Client_Assistant):
    await client.send_message(
        "get_openai_api_key",
        key=config["OPENAI_API_KEY"]
    )


@app.route()
async def add_skill(
    client: Client_Assistant, version: float | None, url: str
):   
    
    # Cloning
    ready_temp_dir()
    skill_uuid = str(uuid.uuid4())
    clone_skill(url, skill_uuid)
    
    
    name = get_name(skill_uuid)
    
    #checking
    if name in [skill["name"] for skill in mongo_manager.get_user_installed_skills(client.uid)]:
        return

    
    if not check_if_skill_is_alright(name, version, skill_uuid):
        remove_skill(skill_uuid)
        raise Exception("Skill is invalid")

    #requirementing
    requirements = get_skill_requirements(skill_uuid)
    
    for requirement in requirements:
        if isinstance(requirement, dict):
            requirement_url, requirement_version = list(requirement.items())[0]
        else:
            requirement_url, requirement_version = requirement, None
        
        try:
            await add_skill(client, requirement_version, requirement_url)
        except Exception as e:
            remove_skill(skill_uuid)
            raise e
    
    
    remove_skill(skill_uuid)

    #clienting
    await client.send_message("add_skill", version= version, url=url, name=name)
    
    result = await client.wait_for_message(f"skill_added/{name}")
    
    succeeded : bool = result.get("succeeded")
    if not succeeded:
        client.send_message("remove_skill", name=name)
        raise Exception("Skill Could Not Be Installed")
    
    new_action_dict = result["new_action_dict"]
    
    #actioning
    actions = []
    
    mongo_manager.add_skill_to_user(name, version, client.uid)

    for action_id, action in new_action_dict.items():
        action_object = Action.from_dict(action)
        actions.append(action_object)

    mongo_manager.add_actions_to_user(client.uid, actions)


@app.route("remove_skill")
async def remove_a_skill(
    client: Client_Assistant, name: str
):
    await client.send_message("remove_skill", name=name)
    mongo_manager.remove_skill_from_user(name, client.uid)
    
    



@app.route()
async def handle_audio(client: Client_Assistant, audio_data, sample_rate, sample_width):
    decoded_compressed_data = base64.b64decode(audio_data)
    decompressed_frame_data = zlib.decompress(decoded_compressed_data)

    audio = sr.AudioData(
        frame_data=decompressed_frame_data,
        sample_rate=sample_rate,
        sample_width=sample_width,
    )
    
    try:
        transcript = recogniser.recognize_google_cloud(audio, "./Data/creds.json")
        logging.log(transcript)
    except:
        transcript = ""
    
    await handle_text(client, transcript)


@app.route()
async def handle_text(client: Client_Assistant, transcript: str):
    logging.info(f"TRANSCRIPT {transcript}")
    await handle_generator_to_audio(client, handle_transcript(client, transcript))

        

async def handle_generator_to_audio(client, gen):
    await client.send_message("indecator_bar_color", color="green")

    async for chunk in gen:
        logging.log(f"chunk {chunk}")
        sentament = get_sentament(chunk)

        chunk = re.sub("(?<=\d)\.(?=\d)", " point ", chunk)
        
        proccessed_text = proccess_text(chunk)
        compressed_audio_data = zlib.compress(proccessed_text)

        # Convert compressed data to base64-encoded string
        base64_compressed_audio_data = base64.b64encode(compressed_audio_data).decode(
            "utf-8"
        )
        await client.send_message("sentament", sentament=sentament)
        await client.send_message("audio", audio=base64_compressed_audio_data)
    await client.send_message("audio", audio="stop!")

@app.route()
async def function_result(client: Client_Assistant, result, function_name: str, original_message: str, succeded: bool):
    try:
        result = str(result)
    except:
        result = ""
        succeded = False
    
    if not succeded:
        result = "the function call did not succeed"
        
    await handle_generator_to_audio(client, handle_function_result(client, result, function_name, original_message, succeded))

async def handle_function_result(client: Client_Assistant, result, function_name: str, original_message: str, succeeded: bool):
    message_handler = MessageHandler(original_message, client)

    async for chunk in convert_generator_to_setance_generator(
        message_handler.handle_function(result, function_name)
    ):
        yield chunk

@app.route()
async def get_installed_skills(client: Client_Assistant):
    installed_skills = mongo_manager.get_user_installed_skills(client.uid)
    await client.send_message("get_installed_skills", installed_skills=installed_skills)


@app.route()
async def get_installed_actions(client: Client_Assistant):
    installed_skills = mongo_manager.get_user_installed_actions(client.uid)
    await client.send_message(
        "get_installed_actions", installed_skills=installed_skills
    )


def proccess_text(text: str):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=24000
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    audio_bytes = response.audio_content
    return audio_bytes


async def handle_transcript(client: Client_Assistant, transcript: str):
    message_handler = MessageHandler(transcript, client)

    async for chunk in convert_generator_to_setance_generator(
        message_handler.handle_message()
    ):
        yield chunk




async def convert_generator_to_setance_generator(generator : str):
    buffer = ""

    async for chunk in generator:
        for punctuation in punctuations:
            if punctuation in chunk:
                buffer += chunk
                yield buffer
                buffer = ""
                break
        else:
            buffer += chunk


app.serve()

