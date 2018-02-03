#!/usr/bin/env python
#
#
#
# This script is used to train a german tagger based on the TIGER corpus
# This tuturial (https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/)
# was used as instructions
#
# Change to the instructions: tagged_sents should be a list as suggested here:
# https://stackoverflow.com/a/48581326/7529379

import pickle

import nltk
import random

from lib.processor.external_libraries.ClassifierBasedGermanTagger.ClassifierBasedGermanTagger import \
    ClassifierBasedGermanTagger

corp = nltk.corpus.ConllCorpusReader('.', 'tiger_release_aug07.corrected.16012013.conll09',
                                     ['ignore', 'words', 'ignore', 'ignore', 'pos'],
                                     encoding='utf-8')

tagged_sents = list(corp.tagged_sents())
random.shuffle(tagged_sents)

# set a split size: use 90% for training, 10% for testing
split_perc = 0.1
split_size = int(len(tagged_sents) * split_perc)
train_sents, test_sents = tagged_sents[split_size:], tagged_sents[:split_size]

print("Training German Tagger ...")
tagger = ClassifierBasedGermanTagger(train=train_sents)
accuracy = tagger.evaluate(test_sents)
print(accuracy)
with open('models/nltk_german_classifier_data2.pkl', 'wb') as f:
    pickle.dump(tagger, f)
