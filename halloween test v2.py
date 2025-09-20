import os
import time
import signal
import pyaudio
import numpy as np

ready = 0

# --- Morse setup (same as before) ---
MORSE_CODE_DICT = { 'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..',
    'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.',
    'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...',
    'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----','2': '..---','3': '...--','4': '....-','5': '.....',
    '6': '-....','7': '--...','8': '---..','9': '----.','0': '-----',
    ' ': ' '
}

UNIT = 0.1
DOT = UNIT
DASH = 3 * UNIT
LETTER_SPACE = 3 * UNIT
WORD_SPACE = 7 * UNIT

FREQ = 600
SAMPLE_RATE = 44100

PENALTY_TIME = 5  # seconds per Ctrl+C attempt

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_tone(duration, freq=FREQ):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = np.sin(freq * t * 2 * np.pi)
    return tone

def play_tone(stream, duration):
    samples = (generate_tone(duration) * 0.5).astype(np.float32)
    stream.write(samples.tobytes())

def play_silence(stream, duration):
    samples = np.zeros(int(SAMPLE_RATE * duration), dtype=np.float32)
    stream.write(samples.tobytes())

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(ch.upper(), '') for ch in text)

def penalty_handler(signum, frame):
    global in_penalty
    if in_penalty:
        return  # already penalizing
    in_penalty = True

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    print(f"\nCtrl+C detected! Waiting {PENALTY_TIME} seconds...")
    time.sleep(PENALTY_TIME)

    signal.signal(signal.SIGINT, penalty_handler)
    in_penalty = False

def play_morse(text):
    # Ignore Ctrl+C completely during playback
    old_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True)

    morse_code = text_to_morse(text)

    for char in morse_code:
        if char == '.':
            play_tone(stream, DOT)
            play_silence(stream, UNIT)
        elif char == '-':
            play_tone(stream, DASH)
            play_silence(stream, UNIT)
        elif char == ' ':
            play_silence(stream, LETTER_SPACE)

    play_silence(stream, WORD_SPACE)
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Restore handler after playback (back to penalty mode)
    signal.signal(signal.SIGINT, old_handler)

def safe_input(prompt=""):
    while True:
        try:
            return input(prompt)
        except EOFError:
            continue

    morse_code = text_to_morse(text)

    for char in morse_code:
        if char == '.':
            play_tone(stream, DOT)
            play_silence(stream, UNIT)
        elif char == '-':
            play_tone(stream, DASH)
            play_silence(stream, UNIT)
        elif char == ' ':
            play_silence(stream, LETTER_SPACE)

    play_silence(stream, WORD_SPACE)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    in_penalty = False
    signal.signal(signal.SIGINT, penalty_handler)  # penalty mode for guessing

    phrase = input("Enter a phrase to encode: ")
    clear_terminal()
    time.sleep(1)
    while ready == 0:
        readystate = safe_input("The phrase has been loaded. Once you are ready, press Enter.")
        if readystate == '':
            ready += 1
            clear_terminal()
            continue
        else:
            ready += 1
            clear_terminal()
            continue
    play_morse(phrase)

    while True:
        guess = safe_input("What was the encoded message? \nIf you need to listen to the Morse Code again, type Restart. \n")
        guess = guess.lower()
        if guess == 'playingfiddle':
            clear_terminal()
            print('Reset activated, restarting program...')
            os._exit(1)
        elif guess == 'restart':
            clear_terminal()
            time.sleep(1)
            play_morse(phrase)
            continue
        elif guess == phrase:
            clear_terminal()
            print("Correct! The code for this room is [CODE].")
            break
        else:
            clear_terminal()
            print("Incorrect. Please try again.")
            time.sleep(2)