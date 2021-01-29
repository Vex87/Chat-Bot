LANGUAGE = "en"

from gtts import gTTS 
import playsound
import json
import random
import os
import speech_recognition
import queue
import threading
import shutil
import re

def delete_contents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def say_text(message):
    audio = gTTS(text = message, lang = LANGUAGE, slow = False) 
    file_name = "TTS\\output_message.mp3"
    delete_contents("TTS")
    audio.save(file_name) 
    playsound.playsound(file_name)

def get_response(input_text):
    for info in data:
        for pattern in info["pattern"]:
            if pattern in input_text:
                if "base_responses" in info:
                    random_base_response = random.choice(info["base_responses"])
                    while ("FILL_RESPONSE" in random_base_response):
                        for match in re.finditer("FILL_RESPONSE", random_base_response):
                            match_in_response = random_base_response[match.start():match.end() + 2]
                            random_fill_response = random.choice(info[f"fill_responses_{random_base_response[match.end() + 1:match.end() + 2]}"])
                            random_base_response = random_base_response.replace(f"[{match_in_response}]", random_fill_response)
                            break
                    return random_base_response
                else:
                    return random.choice(info["responses"])

def get_voice():
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        audio = recognizer.listen(source)

        try:
            return recognizer.recognize_google(audio) 
        except Exception:
            pass

def watch_voice(voice_queue):
    while (True):
        voice_text = get_voice()
        if (voice_text):
            print(voice_text)
            voice_queue.put(voice_text.lower())

def create_queue(callback):
    new_queue = queue.Queue()
    threading.Thread(
        target = callback,
        args = (new_queue,),
        daemon = True
    ).start()

    return new_queue

def main():
    with open('messages.json') as f:
        global data
        data = json.load(f)

    global voice_queue
    voice_queue = create_queue(watch_voice)

    say_text("Awaiting voice input")
    while (True):
        input_voice = (voice_queue.qsize() > 0) and voice_queue.get()
        if (input_voice):
            response = get_response(input_voice)
            if (response):
                say_text(response)

main()