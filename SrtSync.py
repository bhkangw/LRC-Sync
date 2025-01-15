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
        xml = "\n"+srt+"\n"
        xml = re.sub(r'[\n\r]+','\n',xml)
        xml = re.sub(r'&','&amp;',xml)
        xml = re.sub(r'<','&lt;',xml)
        xml = re.sub(r'>','&gt;',xml)
        xml = re.sub(r'\n([0-9]+)\n([0-9]+:[0-9]+:[0-9]+[,.][0-9]+ --&gt; [0-9]+:[0-9]+:[0-9]+[,.][0-9]+)\n'
                     ,r'<time id="\1" stamp="\2"/>'
                     ,xml)
        return xml
        
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
        
        # Parse original SRT timestamps
        timestamps = []
        current_timestamp = None
        for line in self.srt.split('\n'):
            if '-->' in line:
                timestamps.append(line.strip())
        print(f"Found {len(timestamps)} timestamps")
        
        # Convert SRT to XML while preserving timestamps
        print("Converting SRT to XML...")
        self.xml = self.toXml(self.srt)
        print(f"XML content preview:\n{self.xml[:500]}")
        
        # Align text while preserving timestamp markers
        print("Aligning text...")
        aligned_lines = self.aligner.syncMarks1to2(self.xml, self.txt).split('\n')
        print(f"Got {len(aligned_lines)} aligned lines")
        
        # Reconstruct SRT format with timestamps
        counter = 1
        output_lines = []
        
        # Pair each aligned line with a timestamp
        for i, line in enumerate(aligned_lines):
            if line.strip():  # Skip empty lines
                if i < len(timestamps):  # Make sure we have a timestamp
                    output_lines.extend([
                        str(counter),
                        timestamps[i],
                        line,
                        ''
                    ])
                    counter += 1
                    print(f"Added block {counter-1} with timestamp: {timestamps[i]}")
        
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


def main():
    parser = argparse.ArgumentParser(description="Synchronize SRT timestamps over an existing accurate transcription.")
    parser.add_argument('pathSrt', type=str, help="Path to the SRT file with good timestamps")
    parser.add_argument('pathTxt', type=str, help="Path to the TXT file with good text")
    parser.add_argument('lng', type=str, help="language", nargs='?')
    args = parser.parse_args()
    
    SrtSync().sync(args.pathSrt, args.pathTxt)

if __name__ == "__main__":
    main()