import sounddevice as sd
import wavio as wv
import threading
import keyboard
import time
import speech_recognition as sr
import tempfile
import http.client
import json
import pyttsx3


# Sampling frequency
freq = 44100
duration = 100

RAPID_API_KEY = "YOUR KEY"
RAPID_API_HOST = "YOUR HOST"

def start_recording():
    global recording, start_time
    print("Recording... press 'END' to stop")
    start_time = time.time()
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)
    sd.wait()

def stop_recording():
    global recording_stopped
    recording_stopped = True
    sd.stop()

def save_recording():
    global recording, start_time

    end_time = time.time()
    recorded_duration = end_time - start_time

    # Find the index where the recording stops
    stop_index = int(recorded_duration * freq)

    # Trim the recording to the stop index
    trimmed_recording = recording[:stop_index]

    # Save trimmed audio to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False) as temp_wav_file:
        temp_wav_file_name = temp_wav_file.name
        wv.write(temp_wav_file_name, trimmed_recording, freq, sampwidth=2)
        # Convert the temporary WAV file to AudioFile for speech recognition

        with sr.AudioFile(temp_wav_file_name) as source:
            audio = recognizer.record(source)
            try:
                recognized_text = recognizer.recognize_google(audio)
                print("Recognized Text: " + recognized_text)
                return recognized_text
            except sr.UnknownValueError:
                print("Speech recognition could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
    return None

#calls API and gets back the result. Enter individual key and host
def chat(text):
    conn = http.client.HTTPSConnection("chatgpt-gpt4-ai-chatbot.p.rapidapi.com")
    payload = "{\r\n    \"query\": \"" + text + "\"\r\n}"
    headers = {
        'content-type': "application/json",
        'X-RapidAPI-Key': RAPID_API_KEY,
        'X-RapidAPI-Host': RAPID_API_HOST
    }
    conn.request("POST", "/ask", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response_json = json.loads(data.decode("utf-8"))
    response_text =  response_json.get("response")
    print("Response: " + response_text)
    return response_text

#converts text to speech
def text_to_speech(text):
    SpeakText(text)

#Function that converts text to speech
def SpeakText(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

#records audio and outputs the recognized speech as a string 
if __name__ == "__main__":
    print("Starting chatbot")
    recognizer = sr.Recognizer()
    while True:
        recording = None
        recording_thread = None
        recording_stopped = False
        start_time = None
        input("\nPress Enter to start recording")

        recording_thread = threading.Thread(target=start_recording)
        recording_thread.start()

        keyboard.wait("End")  # Wait for 'End' key to be pressed

        if not recording_stopped:
            stop_recording()

        recording_thread.join()  # Wait for the recording thread to finish
        result = save_recording()
        if (result):                   
            text = chat(result)
            text_to_speech(text)
        print("----press 'space' to keep asking question or press 'delete' to end program----")
        end_prgram = keyboard.read_event()
        if end_prgram.name == "delete":
            print("***************exiting program****************")
            exit()
