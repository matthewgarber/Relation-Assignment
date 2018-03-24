"""
Author: Matthew Garber
Term: Spring 2017
COSI 137b Information Extraction
Assignment #4

This program converts the output from MALLET classification, along with its
corresponding unlabeled dataset, into a format that can be used by
relation-evaluator.py.

To run:
    python convert_output.py <mallet-output> <formatted-output> <unlabeled-dataset>
"""

import sys

def convert_output(mallet_output_filepath,
                   formatted_output_filepath,
                   dataset_filepath):
    """Converts MALLET classification output into the format of the
    train/dev/test datasets so it may be evaluated.
    """
    mallet_file = open(mallet_output_filepath)
    mallet_lines = mallet_file.readlines()
    mallet_file.close()

    dataset_file = open(dataset_filepath)
    dataset_lines = dataset_file.readlines()
    dataset_file.close()
    
    formatted_file = open(formatted_output_filepath, 'w')

    for i in range(len(mallet_lines)):
        mallet_line = mallet_lines[i]
        dataset_line = dataset_lines[i]
        
        if not mallet_line.startswith('\n'):
            label = get_most_likely_label(mallet_line)
            output_line = ' '.join([label, dataset_line])
            formatted_file.write(output_line)

    formatted_file.close()        

def get_most_likely_label(line):
    """Gets the mostly likely label of an instance from the given line of MALLET
    output.
    """
    values = line.split()[1:]
    best_label = None
    best_prob = None
    for i in range(0, len(values), 2):
        current_label = values[i]
        current_prob = float(values[i+1])
        if best_label == None or current_prob > best_prob:
            best_label = current_label
            best_prob = current_prob
    return best_label

if __name__ == '__main__':
    mallet_output_filepath = sys.argv[1]
    formatted_output_filepath = sys.argv[2]
    dataset_filepath = sys.argv[3]
    convert_output(mallet_output_filepath,
                   formatted_output_filepath,
                   dataset_filepath)
