import os
import subprocess
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment

# -----------------------------
# SETTINGS
# -----------------------------
OUTPUT_DIR = "C:/Users/ridaa/translator_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Target language code for Indian languages (examples: 'hi' = Hindi, 'ta' = Tamil, 'bn' = Bengali)
TARGET_LANG = 'hi'

# Video file path
VIDEO_FILE = r"C:\Users\ridaa\Downloads\python project\IPR project\ipr video.mp4"
FINAL_VIDEO_FILE = os.path.join(OUTPUT_DIR, "final_video_translated.mp4")

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def run_command(command):
    print(f"Running command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command {command}: {e}")
        return False
    return True

def extract_audio(video_file, audio_file):
    """Extract audio from video using FFmpeg."""
    command = ["ffmpeg", "-y", "-i", video_file, "-q:a", "0", "-map", "a", audio_file]
    return run_command(command)

def convert_to_wav(input_file, output_file):
    """Convert audio to WAV for transcription."""
    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="wav")
        return True
    except Exception as e:
        print(f"Error converting to WAV: {e}")
        return False

def transcribe_audio(audio_file):
    """Transcribe audio to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Request failed: {e}")
        return ""

def translate_text(text, target_lang):
    """Translate English text to target Indian language."""
    try:
        return GoogleTranslator(source='en', target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return ""

def text_to_speech(text, audio_file, lang):
    """Convert text to speech using gTTS."""
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_file)
        return True
    except Exception as e:
        print(f"Text-to-speech failed: {e}")
        return False

def replace_audio_in_video(video_file, audio_file, output_file):
    """Replace original audio with translated audio using FFmpeg."""
    command = [
        "ffmpeg", "-y", "-i", video_file, "-i", audio_file,
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", output_file
    ]
    return run_command(command)

# -----------------------------
# MAIN PROCESS
# -----------------------------
def process_video(video_file, output_file, target_lang):
    print("Step 1: Extracting audio...")
    audio_mp3 = os.path.join(OUTPUT_DIR, "audio.mp3")
    if not extract_audio(video_file, audio_mp3):
        return

    print("Step 2: Converting to WAV...")
    audio_wav = os.path.join(OUTPUT_DIR, "audio.wav")
    if not convert_to_wav(audio_mp3, audio_wav):
        return

    print("Step 3: Transcribing audio...")
    transcribed_text = transcribe_audio(audio_wav)
    if not transcribed_text:
        return
    print(f"Transcribed Text: {transcribed_text}")

    print(f"Step 4: Translating to {target_lang}...")
    translated_text = translate_text(transcribed_text, target_lang)
    if not translated_text:
        return
    print(f"Translated Text: {translated_text}")

    print("Step 5: Converting translated text to speech...")
    translated_audio = os.path.join(OUTPUT_DIR, "translated_audio.mp3")
    if not text_to_speech(translated_text, translated_audio, target_lang):
        return

    print("Step 6: Replacing audio in video...")
    if not replace_audio_in_video(video_file, translated_audio, output_file):
        return

    print(f"Process completed successfully! Output video: {output_file}")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    process_video(VIDEO_FILE, FINAL_VIDEO_FILE, TARGET_LANG)
