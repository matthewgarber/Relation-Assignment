"""
Author: Matthew Garber
Term: Spring 2017
COSI 137b Information Extraction
Assignment #4

This program converts parse tree files in the given directory so they may be
read and chunked by chunklink.pl

To run:
    python convert_trees.py <parse-tree-dir> <converted-tree-dir>
"""

import os
import sys
from os.path import join as pjoin

def main(tree_dir, new_dir):
    """
    Converts each parse tree file in the given tree_dir into a file in new_dir
    (with the same name) that can be read and chunked by chunklink.pl. It
    essentially just adds a pair of parentheses around each tree.
    """
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    for filename in os.listdir(tree_dir):
        tree_file = open(pjoin(tree_dir, filename))
        new_file = open(pjoin(new_dir, filename), 'w')
        for line in tree_file:
            if line == '\n':
                new_file.write(line)
            else:
                new_line = '( ' + line[:-1] + ')\n'
                new_file.write(new_line)

if __name__ == '__main__':
    tree_dir = sys.argv[1]
    new_dir = sys.argv[2]
    main(tree_dir, new_dir)
    

