# Author: Matthew Garber
# Term: Spring 2017
# COSI 137b Information Extraction
# Assignment #4: Relation Extraction
#
# To run the full pipeline program:
#	sh run.sh <mode>
#
# If <mode> is 'chunk' the program will recreate the previously extracted chunks.
# The scripts used for this, chunklink.pl, may not work with newer versions of
# Perl without some effort.
#
# If <mode> is anything else, the chunking process will be skipped.
#
#
# Features are extracted using the gold files for all datasets; this is allows
# for simpler code since the unlabeled datasets would require small but
# cumbersome adjustments in several parts of the program. The use of the gold
# datasets does not provide any additional information.


mode=$1

if [ $mode = 'chunk' ]; then
  echo 'Performing chunking...'
  # Convert parse trees for chunklink.pl.
  python scripts/convert_trees.py data/parsed-files data/parsed-files-modified
  # Create raw chunk directory.
  mkdir data/chunks-raw
  # Chunk each file.
  for f in data/parsed-files-modified/*; do
    IFS=/ read a b filename <<< "$f"
    perl -X scripts/chunklink.pl -N -p -f -c -t $f > data/chunks-raw/$filename
  done
  # Convert chunks to '<word>_<tag>' format.
  python scripts/chunk.py data/chunks-raw data/chunk-files
fi
  
# Extract features from train, dev, and test sets.
echo 'Extracting features...'
python scripts/extract_features.py features/rel-trainset.feats.gold data/rel-trainset.gold
python scripts/extract_features.py features/rel-devset.feats.gold data/rel-devset.gold
python scripts/extract_features.py features/rel-testset.feats.gold data/rel-testset.gold

# Train relation classifier.
echo 'Training classifier...'
mallet/bin/mallet import-file --input features/rel-trainset.feats.gold --output features/train.mallet
mallet/bin/mallet train-classifier --trainer MaxEnt --input features/train.mallet --output-classifier relation.classifier

# Classify dev and test sets.
echo 'Classifying and scoring...'
mallet/bin/mallet classify-file --input features/rel-devset.feats.gold --output output/rel-devset.mallet --classifier relation.classifier
mallet/bin/mallet classify-file --input features/rel-testset.feats.gold --output output/rel-testset.mallet --classifier relation.classifier

# Convert MALLET output for the dev and test sets.
python scripts/convert_output.py output/rel-devset.mallet output/rel-devset.tagged data/rel-devset.raw
python scripts/convert_output.py output/rel-testset.mallet output/rel-testset.tagged data/rel-testset.raw

# Evaluate results ---------- gold output
python scripts/relation-evaluator.py data/rel-devset.gold output/rel-devset.tagged
python scripts/relation-evaluator.py data/rel-testset.gold output/rel-testset.tagged

