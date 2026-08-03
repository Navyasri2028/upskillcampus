# run_once.py  ← create this file and run it once
import wave, struct, math, os

def create_beep(filename, frequency, duration, volume=0.5):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(num_samples):
            value = int(volume * 32767 *
                       math.sin(2 * math.pi * frequency * i / sample_rate))
            f.writeframes(struct.pack('<h', value))

os.makedirs("sounds", exist_ok=True)
create_beep("sounds/correct.wav",  1000, 0.3)
create_beep("sounds/wrong.wav",     400, 0.4)
create_beep("sounds/timeout.wav",   300, 0.6)
print("✅ Sound files created in sounds/ folder!")