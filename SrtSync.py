#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 11:19:48 2024

@author: cubaix
"""
import argparse
import re
from CbxAligner import CbxAligner

class SrtSync:
    def __init__(self):
        self.aligner = CbxAligner()
        
    def toXml(self,srt):
        # Split into blocks first
        blocks = []
        current_block = []
        
        for line in srt.split('\n'):
            if line.strip():
                current_block.append(line)
            elif current_block:
                blocks.append(current_block)
                current_block = []
        if current_block:
            blocks.append(current_block)
            
        # Convert blocks to XML
        xml_blocks = []
        for block in blocks:
            if len(block) >= 3:  # Valid SRT block should have at least 3 lines
                block_num = block[0].strip()
                if block_num.isdigit():
                    timestamp = block[1].strip()
                    text = ' '.join(block[2:]).strip()
                    # Escape XML special characters in text only
                    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    xml_block = f'<time block="{block_num}" stamp="{timestamp}"/>{text}'
                    xml_blocks.append(xml_block)
        
        return '\n'.join(xml_blocks)
        
    def get_line_similarity(self, line1, line2):
        """Calculate similarity between two lines using character-level comparison"""
        line1 = line1.lower().strip()
        line2 = line2.lower().strip()
        
        if not line1 or not line2:
            return 0.0
        
        # Convert to sets of characters for comparison
        set1 = set(line1)
        set2 = set(line2)
        
        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        # Also check for exact substring matches
        if line1 in line2 or line2 in line1:
            return 0.9  # High confidence for substring matches
        
        return intersection / union

    def sync(self,pathSrt,pathTxt):
        self.pathSrt = pathSrt
        self.pathTxt = pathTxt
        
        print(f"Loading SRT from: {self.pathSrt}")
        # Load files
        with open(self.pathSrt, 'r', encoding='utf-8') as f:
            self.srt = f.read()
        print(f"SRT content preview:\n{self.srt[:500]}")
        
        print(f"Loading TXT from: {self.pathTxt}")
        with open(self.pathTxt, 'r', encoding='utf-8') as f:
            self.txt = f.read()
        print(f"TXT content preview:\n{self.txt[:500]}")
        
        # Parse original SRT timestamps with block numbers
        timestamps = {}  # Changed to dict to store block -> timestamp mapping
        srt_lines = {}  # Store original transcribed lines
        current_block = None
        current_text = None
        
        for line in self.srt.split('\n'):
            line = line.strip()
            if line.isdigit():
                current_block = int(line)
                current_text = None
            elif '-->' in line and current_block is not None:
                timestamps[current_block] = line
                print(f"Stored timestamp for block {current_block}: {line}")
            elif line and current_block is not None and '-->' not in line:
                if current_text is None:
                    current_text = line
                else:
                    current_text += " " + line
                srt_lines[current_block] = current_text
        
        print(f"Found {len(timestamps)} timestamps")
        
        # Convert SRT to XML while preserving timestamps
        print("Converting SRT to XML...")
        self.xml = self.toXml(self.srt)
        print(f"XML content preview:\n{self.xml[:500]}")
        
        # Split the lyrics text into lines, removing section headers and empty lines
        lyrics_lines = []
        for line in self.txt.split('\n'):
            line = line.strip()
            if line and not (line.startswith('[') and line.endswith(']')):
                lyrics_lines.append(line)
        
        # Create output SRT blocks
        output_lines = []
        counter = 1
        processed_blocks = set()  # Track which blocks we've processed
        
        # Skip the first block if it's an intro/adlib
        start_block = 1
        if 1 in srt_lines and "yeah" in srt_lines[1].lower():
            start_block = 2
        
        # First pass: direct matching of lyrics lines
        lyrics_index = 0
        for block_num in range(start_block, len(lyrics_lines) + start_block):
            if block_num in timestamps and lyrics_index < len(lyrics_lines):
                output_lines.extend([
                    str(counter),
                    timestamps[block_num],
                    lyrics_lines[lyrics_index],
                    ''
                ])
                processed_blocks.add(block_num)
                print(f"Added block {counter} with timestamp: {timestamps[block_num]} and text: {lyrics_lines[lyrics_index]}")
                counter += 1
                lyrics_index += 1
        
        # Second pass: check remaining transcribed lines for similarity with any lyrics line
        SIMILARITY_THRESHOLD = 0.7  # Adjust this threshold as needed
        
        for block_num in range(start_block, max(timestamps.keys()) + 1):
            # Skip blocks we've already processed
            if block_num in processed_blocks:
                continue
                
            if block_num in srt_lines and block_num in timestamps:  # Extra line
                transcribed_line = srt_lines[block_num]
                
                # Find best matching lyrics line
                best_match = None
                best_score = 0
                best_index = -1
                
                for i, lyrics_line in enumerate(lyrics_lines):
                    similarity = self.get_line_similarity(transcribed_line, lyrics_line)
                    if similarity > SIMILARITY_THRESHOLD and similarity > best_score:
                        best_score = similarity
                        best_match = lyrics_line
                        best_index = i
                
                if best_match:  # Only add if we found a match
                    output_lines.extend([
                        str(counter),
                        timestamps[block_num],  # Use the actual timestamp from transcription
                        best_match,  # Use the matching lyrics line instead of transcribed line
                        ''
                    ])
                    processed_blocks.add(block_num)
                    print(f"Added repeated line {counter} with timestamp: {timestamps[block_num]} and text: {best_match} (similarity: {best_score:.2f})")
                    counter += 1
        
        self.synced = '\n'.join(output_lines)
        print(f"\nFinal SRT content:\n{self.synced}")
        
        # Write output
        output_path = self.pathTxt+".srt"
        print(f"Writing to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.synced)
        print("Write complete")
        
    def test(self):
        self.sync("./data/KatyPerry-Firework.mp3.srt", "./data/KatyPerry-Firework.txt")

def format_text(text):
    return text.replace(',', ', ')

def main():
    parser = argparse.ArgumentParser(description="Synchronize SRT timestamps over an existing accurate transcription.")
    parser.add_argument('pathSrt', type=str, help="Path to the SRT file with good timestamps")
    parser.add_argument('pathTxt', type=str, help="Path to the TXT file with good text")
    parser.add_argument('lng', type=str, help="language", nargs='?')
    args = parser.parse_args()
    
    SrtSync().sync(args.pathSrt, args.pathTxt)

if __name__ == "__main__":
    main()