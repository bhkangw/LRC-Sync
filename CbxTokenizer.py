#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 10:43:12 2024

@author: cubAIx
"""

import re

class CbxToken:
    UNK = 0
    WORD = 1
    PUNCT = 2
    TAG = 3
    LINE_BREAK = 4
    SECTION_HEADER = 5
    WORD_WITH_APOSTROPHE = 6

    def __init__(self, token, index):
        # Handle section headers first
        if re.match(r'^\[.*\]$', token):
            self.kind = self.SECTION_HEADER
        # Handle line breaks
        elif token == '\n':
            self.kind = self.LINE_BREAK
        # Handle words with apostrophes (like gettin', ain't)
        elif re.match(r"^[\w']+$", token) and "'" in token:
            self.kind = self.WORD_WITH_APOSTROPHE
        # Original token types
        elif re.match(r'^<[^<>]*>$', token):
            self.kind = self.TAG
        elif re.match(r'^\w+$', token):
            self.kind = self.WORD
        elif re.match(r'^[^\w]$', token):
            self.kind = self.PUNCT
        else:
            self.kind = self.UNK
        
        self.token = token
        self.index = index
        
    def __repr__(self):
        return f"CbxToken(token={self.token}, kind={self.kind})"
    
    def __str__(self):
        return repr(self)

class CbxTokenizer:
    def tokenize_lyrics(self, text):
        # Split into lines first to preserve line structure
        lines = text.split('\n')
        tokens = []
        index = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle section headers as a single token
            if re.match(r'^\[.*\]$', line):
                tokens.append(CbxToken(line, index))
                index += 1
                continue
            
            # Tokenize the line
            line_tokens = re.findall(r"[\w']+|[^\w\s]|\s+", line)
            
            # Process tokens in the line
            for token in line_tokens:
                if token.strip():  # Skip pure whitespace
                    tokens.append(CbxToken(token, index))
                    index += 1
            
            # Add line break token
            tokens.append(CbxToken('\n', index))
            index += 1
        
        return tokens

    def tokenize_xml(self, text):
        # Keep original XML tokenization for backward compatibility
        tokens = re.findall(r'<[^<>]*>|\w+|&[a-zA-Z]+;|&#[0-9]+;|[^\w]', text)
        return [CbxToken(token, t) for t, token in enumerate(tokens) if token]

    def test_lyrics(self):
        # Test with a lyric example
        text = """[Verse]
Dust off the shoulders, heavyweight soldier
Heart like boulders, world gettin' colder
Step through the struggle, hustlin' jumble"""
        
        tokens = self.tokenize_lyrics(text)
        print("Lyric Tokens:")
        for t in tokens:
            print(f"[{t.kind}][{t.token}]")
        print("-----")

# CbxTokenizer().test();