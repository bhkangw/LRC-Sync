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
    print(f"Processing SRT file: {srt_path}")  # Debug
    print(f"Absolute path: {os.path.abspath(srt_path)}")  # Debug
    
    if not os.path.exists(srt_path):
        print(f"Error: SRT file not found at {srt_path}")
        return {"lines": []}
        
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    print(f"Read {len(content)} lines")  # Debug
    print("First 10 lines of content:")  # Debug
    for i, line in enumerate(content[:10]):
        print(f"Line {i+1}: {line.rstrip()}")  # Debug

    if not content:
        print("Error: SRT file is empty")
        return {"lines": []}
        
    # Validate basic SRT format
    has_timestamps = False
    for line in content[:10]:  # Check first 10 lines
        if '-->' in line:
            has_timestamps = True
            break
    
    if not has_timestamps:
        print("Error: File doesn't appear to be in SRT format (no timestamps found in first 10 lines)")
        return {"lines": []}

    lines = []
    current_block = []
    
    def process_block(timestamp_line, text_lines):
        if not text_lines or not timestamp_line:
            return None
            
        # Clean and validate timestamp line
        if '-->' not in timestamp_line:
            return None
            
        # Clean up text lines first
        cleaned_lines = []
        for line in text_lines:
            line = line.strip()
            if line and not line.isdigit() and '-->' not in line:
                # Remove section headers and single quotes
                if not (line.startswith('[') and line.endswith(']')):
                    line = line.strip("'")
                    if line:
                        cleaned_lines.append(line)
        
        if not cleaned_lines:
            return None
            
        # Join cleaned lines with newlines
        text = '\n'.join(cleaned_lines)
        
        # Parse timestamp
        try:
            start_time = timestamp_line.split('-->')[0].strip()
            parts = re.split('[,:]', start_time)
            if len(parts) >= 4:  # Ensure we have h:m:s,ms format
                h, m, s = map(float, parts[:3])
                ms = float('0.' + parts[3]) if len(parts) > 3 else 0
                total_seconds = h * 3600 + m * 60 + s + ms
                
                # Format as [mm:ss.xx]
                minutes = int(total_seconds // 60)
                seconds = total_seconds % 60
                timestamp = f"[{minutes:02d}:{seconds:05.2f}]"
                
                print(f"Created entry: {timestamp} {text}")  # Debug
                return {
                    "timestamp": timestamp,
                    "text": text
                }
        except (ValueError, IndexError) as e:
            print(f"Error processing timestamp {start_time}: {e}")
            return None
            
        return None

    # Process content
    for line in content:
        line = line.rstrip('\n')
        
        if not line.strip():
            if current_block:
                # Find timestamp line (contains -->)
                timestamp_line = next((l for l in current_block if '-->' in l), None)
                if timestamp_line:
                    # Get text lines (everything after timestamp)
                    text_start = current_block.index(timestamp_line) + 1
                    text_lines = current_block[text_start:]
                    
                    entry = process_block(timestamp_line, text_lines)
                    if entry:
                        lines.append(entry)
                
                current_block = []
        else:
            current_block.append(line)
    
    # Process last block if exists
    if current_block:
        timestamp_line = next((l for l in current_block if '-->' in l), None)
        if timestamp_line:
            text_start = current_block.index(timestamp_line) + 1
            text_lines = current_block[text_start:]
            
            entry = process_block(timestamp_line, text_lines)
            if entry:
                lines.append(entry)
    
    if not lines:
        print("Warning: No valid LRC lines were generated")
        
    return {"lines": lines}

def cleanup_temp_files(file_paths: list):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}") 

def test_srt_to_lrc():
    """Test the SRT to LRC conversion with various cases"""
    # Create a temporary test SRT file
    test_content = """1
00:00:04,460 --> 00:00:07,180
Dust off the shoulders, heavyweight soldier

2
00:00:07,180 --> 00:00:09,580
Heart like boulders, world gettin' colder
Step through the struggle, hustlin' jumble

3
00:00:09,580 --> 00:00:12,060
[Verse]

4
00:00:12,060 --> 00:00:14,540
Fell nine times, tenth time rubble

5
00:00:14,540 --> 00:00:16,980
[Chorus]
Keep it movin', never losin'
Findin' light in all confusion

6
00:00:16,980 --> 00:00:19,340
'

7
00:00:19,340 --> 00:00:21,780
Challenges turnin', I'm learnin'"""

    # Create temporary file
    with NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        test_file = f.name

    try:
        # Convert and print result
        result = srt_to_lrc_json(test_file)
        print("Test SRT to LRC Conversion Result:")
        for entry in result["lines"]:
            print(f"{entry['timestamp']} {entry['text']}")
            
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)

if __name__ == "__main__":
    test_srt_to_lrc() 