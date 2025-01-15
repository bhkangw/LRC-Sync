import argparse
from pathlib import Path
import whisper
from whisper.utils import WriteSRT
import os

modelSize = "large"

def transcribe_audio(audio_path: str, model_size: str = "large") -> str:
    """Transcribe audio file and return path to SRT file"""
    print(f"Loading Whisper model: {model_size} ...")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing: {audio_path} ...")
    result = model.transcribe(audio_path)
    
    print(result["text"])
    
    srt_path = audio_path + ".srt"
    print(f"Saving: {srt_path} ...")
    p = Path(audio_path)
    os.makedirs(p.parent, exist_ok=True)
    writer = WriteSRT(p.parent)
    writer(result, audio_path)
    
    return srt_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio file to SRT format.")
    parser.add_argument('pathMp3', type=str, help="Path to the MP3 file")
    parser.add_argument('modelSize', type=str, help="Whisper model size", nargs='?')
    args = parser.parse_args()
        
    if args.modelSize is not None:
        modelSize = args.modelSize
        
    transcribe_audio(args.pathMp3, modelSize)
    
    

