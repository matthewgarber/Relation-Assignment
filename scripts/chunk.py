"""
Author: Matthew Garber
Term: Spring 2017
COSI 137b Information Extraction
Assignment #4

This program converts the base phrase chunks created by chunklink.pl into a
format similar to the POS-tagged text, each token/tag pair as '<word>_<tag>'.

To run:
    python chunk.py <raw-chunk-dir> <converted-chunk-dir>
"""

import os
import sys
from os.path import join as pjoin

def convert_raw_chunks(raw_dir, new_dir):
    """Converts each raw chunk file in raw_dir into a new file (with the same
    name) in new_dir.
    """
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    for filename in os.listdir(raw_dir):
        raw_file = open(pjoin(raw_dir, filename))
        new_file = open(pjoin(new_dir, filename), 'w')
        tokens = []
        for line in raw_file:
            if not line.startswith('#'):
                if line == '\n':
                    if len(tokens) > 0:
                        if not tokens[-1].endswith('O'):
                            tokens[-1] = tokens[-1] + '1'
                        new_file.write(' '.join(tokens))
                        tokens = []
                    new_file.write('\n\n')
                else:
                    _, _, tag, token, head, head_id = line.split()
                    if len(tokens) > 0 and (tag == 'O' or tag.startswith('B')):
                        if not tokens[-1].endswith('O'):
                            tokens[-1] = tokens[-1] + '1'
                    tokens.append('_'.join([token, tag]))
        raw_file.close()
        new_file.close()

if __name__ == '__main__':
    raw_dir = sys.argv[1]
    new_dir = sys.argv[2]
    convert_raw_chunks(raw_dir, new_dir)
