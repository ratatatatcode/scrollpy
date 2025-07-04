import speech_recognition as sr
import pyttsx3
import pyautogui
import time
import threading
import sounddevice as sd
import numpy as np

recognizer = sr.Recognizer()
press_direction = None
scroll_direction = None
speed = 0.1
duration = 0.2
threshold = 40

last_clap_time = 0


def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


def clap_detect(indata, frames, time_info, status):
    global press_direction, scroll_direction, last_clap_time
    volume_norm = np.linalg.norm(indata) * 10
    now = time.time()
    if volume_norm > threshold and (now - last_clap_time) > 0.5:
        if scroll_direction == "up" or scroll_direction == "down" or press_direction == "up" or press_direction == "down":
            scroll_direction = None
            print(f"Volume: {volume_norm}")
        else:
            scroll_direction = "down"
            press_direction = None
        last_clap_time = now


def listen():
    global press_direction, scroll_direction, speed

    while True:
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = recognizer.listen(source)

                text = recognizer.recognize_google(audio, language='en-in')
                text = text.lower()

                print(f"Speech to Text: {text}")
                SpeakText(text)

                if "increase speed" in text:
                    if speed > 0.1:
                        speed -= 0.2
                elif "decrease speed" in text:
                    speed += 0.2

                if "stop" in text:
                    press_direction = None
                    scroll_direction = None

                if "scroll up" in text:
                    scroll_direction = "up"
                elif "scroll down" in text:
                    scroll_direction = "down"

                if "press up" in text:
                    press_direction = "up"
                elif "press down" in text:
                    press_direction = "down"

                print(f"Current speed: {speed}")

            except Exception as e:
                import traceback
                print("Error:", e)
                traceback.print_exc()
                continue


def clap_listener():
    with sd.InputStream(callback=clap_detect):
        while True:
            time.sleep(0.1)


def scroll():
    global press_direction, scroll_direction, speed

    while (True):
        if press_direction:
            if press_direction == "up":
                scroll_direction = None
                pyautogui.press("up")
            elif press_direction == "down":
                scroll_direction = None
                pyautogui.press("down")
            time.sleep(1)

        if scroll_direction:
            if scroll_direction == "up":
                press_direction = None
                pyautogui.scroll(100)
            elif scroll_direction == "down":
                pyautogui.scroll(-100)
            elif scroll_direction == None:
                press_direction = None
                pyautogui.scroll(0)
            time.sleep(speed)


threading.Thread(target=listen, daemon=True).start()
threading.Thread(target=scroll, daemon=True).start()
threading.Thread(target=clap_listener, daemon=True).start()

while True:
    time.sleep(0.1)
