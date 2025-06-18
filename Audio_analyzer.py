import os
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.wave import WAVE


def inspect_mp3(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    # Using pydub
    audio = AudioSegment.from_file(file_path)
    print(f" File: {os.path.basename(file_path)}")

    if file_extension == '.mp3':
        mutagen_audio = MP3(file_path)
    elif file_extension == '.wav':
        mutagen_audio = WAVE(file_path)
    else:
        print(f"Unsupported file format: {file_extension}")
        return
    
    print(f"Duration      : {round(mutagen_audio.info.length, 2)} seconds")
    print(f"Channels     : {audio.channels}")
    print(f"Sample Rate  : {audio.frame_rate} Hz ({audio.frame_rate / 1000} kHz)")
    print(f"Sample Width : {audio.sample_width * 8} bits")
    print(f"Bitrate      : {mutagen_audio.info.bitrate / 1000} kbps")

# Example usage on all mp3 files in a folder
folder_path = "/Users/mokshith.salian/Documents/Bidirectional_voice/generic_voice/"

for file in os.listdir(folder_path):
    if file.endswith(".mp3"):
        inspect_mp3(os.path.join(folder_path, file))
    else:
        inspect_mp3(os.path.join(folder_path, file))
        
