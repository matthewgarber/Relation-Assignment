"""
Author: Matthew Garber
Term: Spring 2017
COSI 137b Information Extraction
Assignment #4

This program extracts features from the given dataset writes a file in MALLET
input format, with one instance per line.

To run:
    python extract_features.py <features-filepath> <dataset-filepath>
"""

import re
import sys
from nltk import ParentedTree
from relation import Mention, Relation
from tree_util import add_depth

def file_to_sents(filename):
    """Extracts relevant values from the files corresponding to the given
    filename, and returns a list of sentences, with each word represented by
    a tuple of (<token>, <pos-tag>, <chunk-tag>).

    Args:
        filename: The base name of the input document.
    Returns:
        The documents sentences, represented by a list of lists of 3-tuples.
    """
    pos_filepath = 'data/postagged-files/' + filename + '.head.rel.tokenized.raw.tag'
    pos_text = open(pos_filepath).read()
    pos_sents = [line.split() for line in re.split('\n+', pos_text)]

    chunk_filepath = 'data/chunk-files/' + filename + '.head.rel.tokenized.raw.parse'
    chunk_text = open(chunk_filepath).read()
    chunk_sents = [line.split() for line in re.split('\n+', chunk_text)]

    sents = []
    for i in range(len(pos_sents)):
        pos_sent = pos_sents[i]
        chunk_sent = chunk_sents[i]
        sent = []
        for j in range(len(pos_sent)):
            if pos_sent[j].startswith('__'):
                word, pos = '_', '_'
            else:
                word, pos = pos_sent[j].split('_')[-2:]
            chunk_tag = chunk_sent[j].split('_')[-1]
            sent.append((word, pos, chunk_tag))
        if sent != []:
            sents.append(sent)
    return sents

def file_to_trees(filename):
    """Reads the parse trees in the given file and returns them as a list of
    ParentedTree objects.

    A depth attribute is added for each node in the full tree.

    Args:
        filename: The base name of the input document.
    Returns:
        A list of ParentedTree objects.
    """
    tree_filepath = 'data/parsed-files/' + filename + '.head.rel.tokenized.raw.parse'
    sent_trees = []
    with open(tree_filepath) as tree_file:
        for line in tree_file:
            if not line.startswith('\n'):
                tree = ParentedTree.fromstring(line)
                add_depth(tree)
                sent_trees.append(tree)
    return sent_trees
            
def extract_features(features_filepath, dataset_filepath):
    """Extracts features from the given dataset writes to the features file in
    MALLET input format, with one instance per line.
    """
    with open(dataset_filepath) as dataset_file:
        with open(features_filepath, 'w') as feat_file:
            last_doc_name = None
            sents = None
            rel_id = 0
            for line in dataset_file:
                values = line.split()
                if last_doc_name != values[1]:
                    last_doc_name = values[1]
                    sents = file_to_sents(last_doc_name)
                    sent_trees = file_to_trees(last_doc_name)
                rel = Relation(values, sents, sent_trees, rel_id)
                rel_id += 1
                feat_file.write(rel.to_string() + '\n')

if __name__ == '__main__':
    features_filepath = sys.argv[1]
    dataset_filepath = sys.argv[2]
    extract_features(features_filepath, dataset_filepath)

