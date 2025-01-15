import argparse
from pathlib import Path
import whisper
from whisper.utils import WriteSRT
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(srt_path), exist_ok=True)
        
        # Write SRT file using a file object
        writer = WriteSRT(os.path.dirname(srt_path))
        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            writer.write_result(result, srt_file)
            srt_file.flush()  # Ensure content is written
        
        # Verify the content and format
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"SRT file content preview (first 200 chars): {content[:200]}")
            
            # Validate SRT format
            if not content.strip():
                raise ValueError("SRT file was created but is empty")
            
            # Check for basic SRT format (timestamps with -->)
            if '-->' not in content:
                raise ValueError("Generated file doesn't appear to be in SRT format (no timestamps found)")
            
            # Log the full path to avoid confusion
            logger.info(f"Full SRT file path: {os.path.abspath(srt_path)}")
        
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
    
    

