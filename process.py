import os
from tempfile import NamedTemporaryFile
from pathlib import Path
from utils import download_mp3, srt_to_lrc_json, cleanup_temp_files
from transcribe import transcribe_audio
from SrtSync import SrtSync

def process_audio(audio_url: str, lyrics: str) -> dict:
    """Process audio URL and lyrics to generate synchronized LRC"""
    temp_files = []
    try:
        # Download MP3
        mp3_path = download_mp3(audio_url)
        temp_files.append(mp3_path)

        # Create temporary lyrics file
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as lyrics_file:
            lyrics_file.write(lyrics)
            lyrics_path = lyrics_file.name
            temp_files.append(lyrics_path)

        # Transcribe audio to get SRT
        whisper_srt = transcribe_audio(mp3_path)
        temp_files.append(whisper_srt)

        # Create output SRT path
        output_srt = mp3_path + ".synced.srt"
        temp_files.append(output_srt)

        # Synchronize
        syncer = SrtSync()
        syncer.sync(whisper_srt, lyrics_path)  # This will output to lyrics_path + ".srt"
        
        # Convert synchronized SRT to LRC JSON
        synced_srt = lyrics_path + ".srt"
        result = srt_to_lrc_json(synced_srt)  # Use the synchronized SRT file
        temp_files.append(synced_srt)  # Add to temp files for cleanup
        
        return result
    
    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files) 