import os
import requests
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

def download_mp3(url: str) -> str:
    """Download MP3 from URL to a temporary file and return the path"""
    with NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
        return tmp_file.name

def srt_to_lrc_json(srt_path: str) -> dict:
    """Convert SRT file to LRC JSON format"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse SRT content
    lines = []
    pattern = r'(\d+:\d+:\d+[,.]\d+)\s*-->\s*\d+:\d+:\d+[,.]\d+\n((?:.*(?:\n|$))*)'
    matches = re.finditer(pattern, content)
    
    for match in matches:
        timestamp = match.group(1)
        text = match.group(2).strip()
        if not text:
            continue
            
        # Convert timestamp to milliseconds
        h, m, s = map(float, re.split('[,:]', timestamp))
        ms = int((h * 3600 + m * 60 + s) * 1000)
        
        # Split multi-line text into separate entries
        for line in text.split('\n'):
            if line.strip():
                lines.append({
                    "timestamp": ms,
                    "text": line.strip()
                })
    
    return {"lines": lines}

def cleanup_temp_files(file_paths: list):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}") 