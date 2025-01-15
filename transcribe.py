import argparse
from pathlib import Path
import whisper
from whisper.utils import WriteSRT
import os
import logging
import sys

# Configure logging to output to stdout for Colab visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

modelSize = "large"

def transcribe_audio(audio_path: str, model_size: str = "large") -> str:
    """Transcribe audio file and return path to SRT file"""
    try:
        logger.info(f"Audio file path: {audio_path}")
        logger.info(f"Parent directory: {Path(audio_path).parent}")
        logger.info(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Starting transcription for: {audio_path}")
        result = model.transcribe(audio_path)
        
        logger.info(f"Transcription result: {result['text'][:100]}...")
        
        srt_path = audio_path + ".srt"
        logger.info(f"Attempting to save SRT to: {srt_path}")
        
        p = Path(audio_path)
        try:
            os.makedirs(p.parent, exist_ok=True)
            logger.info(f"Created/verified directory: {p.parent}")
        except Exception as e:
            logger.error(f"Failed to create directory {p.parent}: {str(e)}")
            raise
        
        writer = WriteSRT(p.parent)
        writer(result, audio_path)
        
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"SRT file was not created at expected path: {srt_path}")
            
        logger.info(f"Successfully created SRT file at: {srt_path}")
        return srt_path
        
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio file to SRT format.")
    parser.add_argument('pathMp3', type=str, help="Path to the MP3 file")
    parser.add_argument('modelSize', type=str, help="Whisper model size", nargs='?')
    args = parser.parse_args()
        
    if args.modelSize is not None:
        modelSize = args.modelSize
        
    transcribe_audio(args.pathMp3, modelSize)
    
    

