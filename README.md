# Relation-Assignment

Term: Spring 2017  
COSI 137b Information Extraction  
Assignment #4: Relation Extraction

This program performs relation extraction on the included NYT data set using
MALLET, specifically MALLET's MaxEnt classifier. After extracting features
and training a classifier on the training set, the program will score the
classifier on the dev and test sets and print the results.

To run the full pipeline program:

    sh run.sh <mode>
    
If \<mode\> is 'chunk' the program will recreate the previously extracted chunks.
The scripts used for this, chunklink.pl, may not work with newer versions of
Perl without some effort.

If \<mode\> is anything else, the chunking process will be skipped.


### Directory Sctructure ###
The program expects the following directory structure:

    -data
        -chunk-files : Contains the extracted chunks for each document in BIO
                       format.
        -chunks-raw : Contains the output of chunklink.pl on the document parse
                      trees.
        -parsed-files : Contains the constituent parse trees for each document.
        -parsed-files-modified : Contains the parse trees modified so they can
                                 be read by chunklink.pl.
        -postagged-files : Contains the POS-tagged documents.
        -rel-devset.gold : The labeled dev set.
        -rel-devset.raw : The unlabeled dev set.
        -rel-testset.gold : The labeled test set.
        -rel-testset.raw : The unlabeled test set.
        -rel-trainset.gold : The labeled train set.
        
    -features : The output of the feature extraction scripts and the
                MALLET-formatted instances.
                
    -mallet : The complete MALLET package.
    
    -output : The output of MALLET and the output conversion script.
    
    -scripts
        -chunk.py : Converts the output of chunklink.py. See file documentation
                    for more details.
        -chunklink.py : Extracts chunk information from the converted consituent
                        parse trees.
        -convert_output.py : Converts the MALLET output into a format readable
                             by relation-evaluator.py. See file documentation
                             for more details.
        -convert_trees.py : Converts the parse trees to a format readable by
                            chunklink.pl. See file documentation for more details.
        -extract_features.py : Extracts features from the train, dev, or test set.
                               See file documentation for more details.
        -relation-evaluator.py : Evaluates classifier performance.
        -relation.py : A module containing classes for relation extraction.
                       See file documentation for more details.
        -tree_util.py : Contains function for interacting with NLTK trees.
                        See file documentation for more details.
                        
    -README.txt : This document.
    
    -run.sh : The pipeline program.