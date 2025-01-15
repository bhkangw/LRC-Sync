#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 10:23:19 2024

@author: cubAIx
"""

from CbxTokenizer import CbxTokenizer
from CbxTokenizer import CbxToken

class CbxAligner:
    # Cost constants
    _COST_INCREDIBLE = 1000000
    _COST_LINE_BREAK = 100  # High cost for breaking lines
    _COST_WORD_MISMATCH = 10
    _COST_APOSTROPHE_MISMATCH = 5  # Lower cost for matching words that differ only by apostrophe
    
    def __init__(self):
        self.tokenizer = CbxTokenizer()
        self.compressPosFactor = 1.0/1000000.0
    
    def syncMarks1to2(self, xml1, xml2):
        print("\nCbxAligner.syncMarks1to2:")
        print(f"Input XML1 preview:\n{xml1[:500]}")
        print(f"Input XML2 preview:\n{xml2[:500]}")
        
        pairs = self.alignXml(xml1, xml2)
        print(f"Number of aligned pairs: {len(pairs)}")
        print("First few pairs:")
        for i, p in enumerate(pairs[:5]):
            print(f"Pair {i}: {p[0]} -> {p[1]}")
        
        fused = []
        current_line = []
        
        for p in pairs:
            # Skip section headers
            if p[0] and p[0].kind == CbxToken.SECTION_HEADER:
                continue
            if p[1] and p[1].kind == CbxToken.SECTION_HEADER:
                continue
                
            # Handle line breaks
            if (p[0] and p[0].kind == CbxToken.LINE_BREAK) or (p[1] and p[1].kind == CbxToken.LINE_BREAK):
                if current_line:
                    # Join the current line with proper spacing
                    line_text = ""
                    for i, token in enumerate(current_line):
                        if i > 0 and token.kind not in [CbxToken.PUNCT] and current_line[i-1].kind not in [CbxToken.PUNCT]:
                            line_text += " "
                        line_text += token.token
                    fused.append(line_text)
                    print(f"Added fused line: {line_text}")
                    current_line = []
                continue
            
            # Add non-empty tokens to current line
            if p[1] is not None:
                current_line.append(p[1])
                print(f"Added token to line: {p[1].token}")
        
        # Handle any remaining tokens in the last line
        if current_line:
            line_text = ""
            for i, token in enumerate(current_line):
                if i > 0 and token.kind not in [CbxToken.PUNCT] and current_line[i-1].kind not in [CbxToken.PUNCT]:
                    line_text += " "
                line_text += token.token
            fused.append(line_text)
            print(f"Added final fused line: {line_text}")
        
        result = "\n".join(fused)  # Join lines with newlines
        print(f"\nFinal aligned result preview:\n{result[:500]}")
        return result
    
    def alignXml(self, xml1, xml2):
        toks1 = self.tokenizer.tokenize_lyrics(xml1)  # Use lyrics tokenizer
        toks2 = self.tokenizer.tokenize_lyrics(xml2)
        return self.alignToks(toks1, toks2)
        
    def alignToks(self, toks1, toks2):
        # Init matrix
        choices = [[0 for y in range(len(toks2) + 1)] for x in range(len(toks1) + 1)]
        costs = [[0 for y in range(len(toks2) + 1)] for x in range(len(toks1) + 1)]
        
        # Initialize first row and column
        for x in range(1, len(toks1) + 1):
            choices[x][0] = 1  # Left
            costs[x][0] = self._calculate_gap_cost(toks1[x-1])
        for y in range(1, len(toks2) + 1):
            choices[0][y] = 2  # Up
            costs[0][y] = self._calculate_gap_cost(toks2[y-1])
        
        # Fill the matrix
        for x in range(1, len(toks1) + 1):
            for y in range(1, len(toks2) + 1):
                tok1, tok2 = toks1[x-1], toks2[y-1]
                
                # Calculate costs for each possible move
                cost_diag = costs[x-1][y-1] + self._calculate_match_cost(tok1, tok2)
                cost_left = costs[x-1][y] + self._calculate_gap_cost(tok1)
                cost_up = costs[x][y-1] + self._calculate_gap_cost(tok2)
                
                # Choose the minimum cost move
                if cost_diag <= cost_left and cost_diag <= cost_up:
                    choices[x][y] = 0  # Diagonal
                    costs[x][y] = cost_diag
                elif cost_left <= cost_up:
                    choices[x][y] = 1  # Left
                    costs[x][y] = cost_left
                else:
                    choices[x][y] = 2  # Up
                    costs[x][y] = cost_up
        
        # Backtrack to get alignment
        return self._backtrack(choices, toks1, toks2)
    
    def _calculate_match_cost(self, tok1, tok2):
        # Skip cost calculation for section headers
        if tok1.kind == CbxToken.SECTION_HEADER or tok2.kind == CbxToken.SECTION_HEADER:
            return 0
            
        # Exact match
        if tok1.token.lower() == tok2.token.lower():
            return 0
            
        # Line break mismatch
        if tok1.kind == CbxToken.LINE_BREAK or tok2.kind == CbxToken.LINE_BREAK:
            return self._COST_LINE_BREAK
            
        # Word with/without apostrophe
        if (tok1.kind == CbxToken.WORD_WITH_APOSTROPHE and tok2.kind == CbxToken.WORD) or \
           (tok2.kind == CbxToken.WORD_WITH_APOSTROPHE and tok1.kind == CbxToken.WORD):
            return self._COST_APOSTROPHE_MISMATCH
            
        # Regular word mismatch
        return self._COST_WORD_MISMATCH
    
    def _calculate_gap_cost(self, tok):
        if tok.kind == CbxToken.SECTION_HEADER:
            return 0
        if tok.kind == CbxToken.LINE_BREAK:
            return self._COST_LINE_BREAK
        return self._COST_WORD_MISMATCH
    
    def _backtrack(self, choices, toks1, toks2):
        pairs = []
        x, y = len(toks1), len(toks2)
        
        while x > 0 or y > 0:
            if x > 0 and y > 0 and choices[x][y] == 0:  # Diagonal
                pairs.append((toks1[x-1], toks2[y-1]))
                x -= 1
                y -= 1
            elif x > 0 and choices[x][y] == 1:  # Left
                pairs.append((toks1[x-1], None))
                x -= 1
            else:  # Up
                pairs.append((None, toks2[y-1]))
                y -= 1
        
        return list(reversed(pairs))

    def test_lyrics(self):
        # Test with a lyric example
        text1 = """[Verse]
Dust off the shoulders, heavyweight soldier
Heart like boulders, world gettin' colder"""
        
        text2 = """[Verse]
Dust off the shoulders, heavyweight soldier
Heart like boulders, world getting colder"""
        
        result = self.syncMarks1to2(text1, text2)
        print("Aligned Result:")
        print(result)

# CbxAligner().test_lyrics()
