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

        # Transcribe audio
        srt_path = transcribe_audio(mp3_path)
        temp_files.append(srt_path)

        # Synchronize
        syncer = SrtSync()
        syncer.sync(srt_path, lyrics_path)
        synced_srt = lyrics_path + ".srt"
        temp_files.append(synced_srt)

        # Convert to LRC JSON
        result = srt_to_lrc_json(synced_srt)
        
        return result
    
    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files) 