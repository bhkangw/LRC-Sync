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
        current_block = None
        for line in self.srt.split('\n'):
            if line.strip().isdigit():
                current_block = int(line.strip())
            elif '-->' in line and current_block is not None:
                timestamps[current_block] = line.strip()
                print(f"Stored timestamp for block {current_block}: {line.strip()}")
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
        
        # Create output SRT blocks, skipping the first block (adlib)
        output_lines = []
        counter = 1
        
        # Start from index 1 to skip the adlib block
        for i, timestamp_block in enumerate(timestamps.items(), start=1):
            block_num, timestamp = timestamp_block
            if block_num == 1:  # Skip the adlib block
                continue
                
            if i-1 < len(lyrics_lines):  # i-1 because we want to use 0-based index for lyrics
                output_lines.extend([
                    str(counter),
                    timestamp,
                    lyrics_lines[i-2],  # i-2 to account for both 0-based index and skipping adlib
                    ''
                ])
                print(f"Added block {counter} with timestamp: {timestamp} and text: {lyrics_lines[i-2]}")
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