#!/usr/bin/env python
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import wordfreq
import pickle
from lib.processor.ExpressionObjects import Word

CASE_ID = ""
# words = wordfreq.random_words(lang='de', wordlist='large', nwords=100000, bits_per_word=12).split()
expressions = pickle.load(open('/Users/ju/PycharmProjects/slughorn/data/{}/expressions_2018-02-13_11-43-53.pkl'.format(CASE_ID), 'rb'))
words = [word.term for word in expressions['words']]
# print(len(words))


def show_frequency_plot(words):
    values = [wordfreq.word_frequency(word, 'de', wordlist='large') for word in words]

    plt.hist(values, bins=np.arange(min(values), max(values)+1, step=0.0001), facecolor='green')

    plt.xlabel('Relative Häufigkeit im Sprachgebrauch')
    plt.ylabel('Anzahl der Wörter')
    plt.title('Histogramm der Häufigkeitsverteilung')
    plt.axis([0, 0.035, 0, 300])
    plt.grid(True)

    plt.show()


def show_feature_scaled_plot(words):
    values = [(wordfreq.word_frequency(word, 'de', wordlist='large') / 0.03235936569296283) for word in words]

    plt.hist(values, bins=np.arange(min(values), max(values)+1, step=0.01), facecolor='green')

    plt.xlabel('Min-Max skalierte Häufigkeit im Sprachgebrauch')
    plt.ylabel('Anzahl der Wörter')
    plt.title('Histogramm der Häufigkeitsverteilung')
    plt.axis([0, 1.0, 0, 200])
    plt.grid(True)

    plt.show()


def show_zipf_plot(words):
    values = [wordfreq.zipf_frequency(word, 'de', wordlist='large') for word in words]

    plt.hist(values, bins=np.arange(min(values), max(values)+1, step=0.25), facecolor='green', edgecolor='black', linewidth=0.8)

    plt.xlabel('Zipf Häufigkeit im Sprachgebrauch')
    plt.ylabel('Anzahl der Wörter')
    plt.title('Histogramm der Häufigkeitsverteilung')
    plt.axis([0, 7, 0, 3000])
    plt.grid(True)

    plt.show()


def get_specific_zipf_word(words, zipf):
    pairs = [(word, wordfreq.zipf_frequency(word, 'de', wordlist='large')) for word in words]
    found_words = []
    for word, value in pairs:
        if (value > zipf - 0.1) and (value < zipf + 0.1):
            found_words.append((word, value))
    return found_words

# show_zipf_plot(words)
# show_frequency_plot(words)
show_feature_scaled_plot(words)
# for i in range(10):
#     print("ZIPF {}".format(i))
#     print(get_specific_zipf_word(words, i))
