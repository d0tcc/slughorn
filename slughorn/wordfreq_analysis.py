#!/usr/bin/env python
import pickle

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import wordfreq

# CASE_ID = ""
# FILE_NAME = ""
# words = wordfreq.random_words(lang='de', wordlist='large', nwords=100000, bits_per_word=12).split()
# expressions = pickle.load(open('/Users/ju/PycharmProjects/slughorn/data/{}/{}.pkl'.format(CASE_ID, FILE_NAME), 'rb'))
# words = expressions['words']
#words = [word.term for word in expressions['words']]
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


def evaluate_weights(words):
    frequencies = [word.frequency for word in words]
    exceptionalisms = [word.exceptionalism for word in words]
    scores = [word.score for word in words]

    plt.subplot(3, 1, 1)
    plt.hist(frequencies, bins=np.arange(min(frequencies), max(frequencies) + 1, step=0.01), facecolor='green', edgecolor='black',
             linewidth=0.8)

    plt.xlabel('Häufigkeiten')
    plt.ylabel('Anzahl der Wörter')
    plt.title('Histogramme der Häufigkeitsverteilung')
    plt.axis([0, 1, 0, 10])
    plt.grid(True)


    plt.subplot(3, 1, 2)
    plt.hist(exceptionalisms, bins=np.arange(min(exceptionalisms), max(exceptionalisms) + 1, step=0.01), facecolor='green',
             edgecolor='black',
             linewidth=0.8)

    plt.xlabel('Außergewöhnlichkeit')
    plt.ylabel('Anzahl der Wörter')
    plt.axis([0, 1, 0, 10])
    plt.grid(True)


    plt.subplot(3, 1, 3)
    plt.hist(scores, bins=np.arange(min(scores), max(scores) + 1, step=0.01), facecolor='green',
             edgecolor='black',
             linewidth=0.8)

    plt.xlabel('Score')
    plt.ylabel('Anzahl der Wörter')
    plt.axis([0, 1, 0, 30])
    plt.grid(True)

    plt.show()


def draw_password_cracking_times():
    n = range(0, 13)
    md5_times = [1.38681E-15, 1.3036E-13, 1.22538E-11, 1.15186E-09, 1.08275E-07, 1.01778E-05, 0.000956717, 0.089931435,
                 8.453554925, 794.634163, 74695.61132, 7021387.464, 660010421.6]
    md5_times = [time / 24 / 30 for time in md5_times]
    sha_times = [4.03917E-15, 3.79682E-13, 3.56901E-11, 3.35487E-09, 3.15358E-07, 2.96436E-05, 0.002786502, 0.261931141,
                 24.62152726, 2314.423563, 217555.8149, 20450246.6, 1922323181]
    sha_times = [time / 24 / 30 for time in sha_times]
    pdf_times = [1.08422E-09, 1.01917E-07, 9.58019E-06, 0.000900538, 0.084650551, 7.957151774, 747.9722667, 70309.39307,
                 6609082.949, 6212537972, 58397856936, 5.4894E+12, 5.16003E+14]
    pdf_times = [time / 24 / 30 for time in pdf_times]

    plt.plot(n, md5_times, '.r-', n, sha_times, '.b-', n, pdf_times, '.g-')
    plt.axis([0, 13, 0, 150])
    plt.xlabel('Passwortlänge (Anzahl der Zeichen)')
    plt.ylabel('Monate um alle Kombinationen zu probieren')
    plt.axhline(120, color='k')
    plt.axhline(12, color='k')
    plt.annotate('1 Jahr', xy=(13, 12), xytext=(13.1, 10))
    plt.annotate('10 Jahre', xy=(13, 120), xytext=(13.1, 118))

    red_patch = mpatches.Patch(color='red', label='MD5')
    blue_patch = mpatches.Patch(color='blue', label='SHA256')
    green_patch = mpatches.Patch(color='green', label='PDF')
    plt.legend(handles=[red_patch, blue_patch, green_patch])

    plt.show()

draw_password_cracking_times()
#evaluate_weights(words)
# show_zipf_plot(words)
# show_frequency_plot(words)
#show_feature_scaled_plot(words)
# for i in range(10):
#     print("ZIPF {}".format(i))
#     print(get_specific_zipf_word(words, i))
#

def draw_password_cracking_times():
    n = range(0, 13)
    md5_times = [1.38681E-15, 1.3036E-13, 1.22538E-11, 1.15186E-09, 1.08275E-07, 1.01778E-05, 0.000956717, 0.089931435,
                 8.453554925, 794.634163, 74695.61132, 7021387.464, 660010421.6]
    md5_times = [time / 24 / 30 for time in md5_times]
    sha_times = [4.03917E-15, 3.79682E-13, 3.56901E-11, 3.35487E-09, 3.15358E-07, 2.96436E-05, 0.002786502, 0.261931141,
                 24.62152726, 2314.423563, 217555.8149, 20450246.6, 1922323181]
    sha_times = [time / 24 / 30 for time in sha_times]
    pdf_times = [1.08422E-09, 1.01917E-07, 9.58019E-06, 0.000900538, 0.084650551, 7.957151774, 747.9722667, 70309.39307,
                 6609082.949, 6212537972, 58397856936, 5.4894E+12, 5.16003E+14]
    pdf_times = [time / 24 / 30 for time in pdf_times]

    f, (ax, ax2) = plt.subplots(2, 1, sharex=True)
    ax.plot(n, md5_times, '.r-', n, sha_times, '.b-', n, pdf_times, '.g-')
    ax2.plot(n, md5_times, '.r-', n, sha_times, '.b-', n, pdf_times, '.g-')
    ax.set_ylim(80, 300)  # outliers only
    ax2.set_ylim(0, 6)  # most of the data

    # hide the spines between ax and ax2
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop='off')  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    # plt.plot(n, md5_times, '.r-', n, sha_times, '.b-', n, pdf_times, '.g-')
    # plt.axis([0, 13, 0, 150])
    plt.xlabel('Passwortlänge (Anzahl der Zeichen)')
    plt.ylabel('Monate um alle Kombinationen zu probieren')
    # plt.axhline(120, color='k')
    # plt.axhline(12, color='k')
    # plt.annotate('1 Jahr', xy=(13, 12), xytext=(13.1, 10))
    # plt.annotate('10 Jahre', xy=(13, 120), xytext=(13.1, 118))

    red_patch = mpatches.Patch(color='red', label='MD5')
    blue_patch = mpatches.Patch(color='blue', label='SHA256')
    green_patch = mpatches.Patch(color='green', label='PDF')
    plt.legend(handles=[red_patch, blue_patch, green_patch])

#     plt.show()