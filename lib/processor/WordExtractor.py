from lib.processor.Word import Word

import os
import re
import fastText
from datetime import datetime
import pycountry
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from wordfreq import zipf_frequency
from collections import defaultdict
import pickle
import logging

log = logging.getLogger('slughorn')

LANGUAGE_MODEL = fastText.load_model('lib/processor/models/lid.176.ftz')


def detect_language(text):
    """
    Detects the language of a text

    Detects the language of a text with fastText and returns the alpha_2 representation of a language (e.g. 'en')
    The model for language identification comes from fasttext:
    https://fasttext.cc/docs/en/language-identification.html

    k = 1 in the predict method returns only the most probable language
    """
    text = text.replace('\n', ' ')
    language_label, probability = LANGUAGE_MODEL.predict(text, k=1)
    language_code = language_label[0].replace('__label__', '')
    return language_code


def clean_text(text):
    """
    Removes special characters from text
    
    :param text: Text to be cleaned
    :return: Cleaned text
    """
    cleaned_text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)  # remove URLs
    bad_characters = ['„', '“', '`', "'", '´', ',', '.', '…', '‚', '‘', '‘', '’', '«', '»', '‹', '›']
    for character in bad_characters:
        cleaned_text = cleaned_text.replace(character, '')
    ugly_characters = ['-', '_', '+', '>', '<', '*', '/', ]
    for character in ugly_characters:
        cleaned_text = cleaned_text.replace(character, ' ')
    return cleaned_text


def remove_stopwords(text, language_code):
    """
    Removes stopwords from text

    Removes all stopwords in the language of the text and returns all words which are longer than 1 character
    together as a list
    :param text: Text the stopwords will be removed from
    :param language_code: Language Code (alpha_2, e.g. 'en') of the text
    :return: List of non-stopwords longer than 1 character
    """
    language_name = pycountry.languages.get(alpha_2=language_code).name.lower()
    stop_words = set(stopwords.words(language_name))
    stop_words.update(['``', "''"])  # add double quotes because of weird facebook encoding
    text = clean_text(text)
    words = word_tokenize(text, language=language_name)
    filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 1]
    return filtered_words


def calculate_exceptionalism(word_dict):
    """
    Detects how common the words are in their language using 'wordfreq'
    zipf_frequency returns the commonness of a word on a logarithmic scale, with 8 being the most common and 0 being 
    an unknown word. To get the exceptionalism of a word the value is substracted from 8.
        
    :param word_dict: dictionary of words
    :return: 
    """
    for language, words in word_dict.items():
        for word, attributes in words.items():
            attributes['exceptionalism'] = 8 - zipf_frequency(word, language, wordlist='large')  # calculate exceptionalism


def calculate_score(word_dict):
    """
    Calculates the score of each word.
    The score of word is the product of its exceptionalism and its number of occurrences. A higher value means that 
    the word is a better candidate for a password.
    
    :param word_dict: dictionary of words
    :return:
    """
    for language, words in word_dict.items():
        for word, attributes in words.items():
            attributes['score'] = attributes['exceptionalism'] * attributes['occurrences']  # calculate score


def combine_false_friends(word_dict):
    """
    Removes so-called False Friends from the dictionary of words.
    A False Friend is a word that appears in several languages, e.g. 'fast' in German and in English. The function 
    compares the exceptionalism of both appearances and adds the occurrences of the one with the lower exceptionalism 
    to the other one. This is done to ensure that the word appears on the top most position in the final password list 
    as necessary.
    
    :param word_dict: dictionary of words
    :return: 
    """
    for language1, words1 in word_dict.items():
        for language2, words2 in word_dict.items():
            if language1 == language2:
                continue
            else:
                for intersection in set(words1).intersection(set(words2)):
                    # TODO: more dynamic solution: higher_exceptionalism = max([words1, words2], key=...)
                    if words1[intersection]['exceptionalism'] > words2[intersection]['exceptionalism']:
                        words1[intersection]['occurrences'] += words2[intersection]['occurrences']
                        del words2[intersection]
                    else:
                        words2[intersection]['occurrences'] += words1[intersection]['occurrences']
                        del words1[intersection]


def create_final_word_list(word_dict):
    """
    Creates a list of Word objects from the dictionary of words and sorts it descending by score.
    
    :param word_dict: dictionary of words
    :return: A list of Word objects containing all information of the word_dict, sorted by score descending
    """
    final_word_list = []
    for language, words in word_dict.items():
        for word, attributes in words.items():
            final_word_list.append(Word(term=word,
                                        occurrences=attributes['occurrences'],
                                        exceptionalism=attributes['exceptionalism'],
                                        language=language,
                                        score=attributes['score']))
    final_word_list.sort(key=lambda x: x.score, reverse=True)
    return final_word_list



class WordExtractor:
    """
    A WordExtractor object represents one attempt to extract words from a list of posts.
    """

    def __init__(self, texts, case_id, final_word_list=[]):
        """
        Init method of the WordExtractor Class
        
        :param texts: List of texts from a user
        :param case_id: String representation of the case number
        :param final_word_list: Final word list, is empty at initialization (parameter only for testing purposes)
        """
        self.texts = texts
        self.case_id = case_id
        self.final_word_list = final_word_list

    def extract_words(self):
        """
        Starts the extraction process.
        
        Initializes a dictionary of words (extracted_words)
            example for extracted_words = {
                    'en': {
                        'Dog': {
                            'occurrences': 3,
                            'commonness: 3.5,
                            'score': 0
                        },
                        'fast': {
                            'occurrences': 2,
                            'commonness: 7.5,
                            'score': 0
                        }
                    },
                    'de': {
                        'Hund': {
                            'occurrences': 6,
                            'commonness: 3.5,
                            'score': 0
                        },
                        'fast': {
                            'occurrences': 1,
                            'commonness: 7.5,
                            'score': 0
                        }
                    }
            }
        
        Calls detect_language and remove_stopwords for every text and updates the results in extracted_words.
        Afterwards it calls calculate_exceptionalism, combine_false_friends, calculate_score and 
        create_final_word_list for the pre-processed dictionary of words.
        Sets the final word list (list ob Word objects) as self.final_word_list.
        :return:
        """

        extracted_words = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        def update_language_dict(words, language):
            """
            Helper function to update the extracted_words dictionary for every text.
            Increments the occurrences of each word.
            
            :param words: extracted words per single text
            :param language: the language of the text
            :return: 
            """
            for word in words:
                extracted_words[language][word]['occurrences'] += 1

        log.info("Removing stopwords from posts ...")
        for text in self.texts:
            language_code = detect_language(text)
            filtered_words = remove_stopwords(text, language_code)
            update_language_dict(filtered_words, language_code)

        log.info("Calculate exceptionalism of words ...")
        calculate_exceptionalism(extracted_words)
        log.info("Combine False Friends ...")
        combine_false_friends(extracted_words)
        log.info("Calculate score ...")
        calculate_score(extracted_words)
        log.info("Finished extraction of words!")
        self.final_word_list = create_final_word_list(extracted_words)

    def print_words(self):
        """
        Prints the words in the final word list
        
        :return: 
        """
        for word in self.final_word_list:
            print(word)

    def write_to_file(self, directory='', pickled=True):
        """
        Writes extracted words to a file.

        :param directory: Optional directory where the file will be located
        :param pickled: Whether the file should be a pickle (txt if False)
        """
        if not directory:
            directory = 'data/{}'.format(self.case_id)

        today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = os.path.join(directory, 'words_{}.{}'.format(today, ('pkl' if pickled else 'txt')))

        log.info("Writing extracted words to file")
        if pickled:
            pickle.dump(self.final_word_list, open(file, "wb"))
        else:
            output = ''
            for word in self.final_word_list:
                output += str(word) + "\n"

            with open(file=file, mode='w+') as f:
                f.write(output)

        log.info("Successfully written to file {}".format(file))


# test_texts = ["Nach aktuellen, auf DNA-Vergleichen beruhenden Verwandtschaftsanalysen sind diese traditionell "
#               "ausgehaltenen Gattungsgruppen ebenfalls keine geschlossenen Abstammungsgemeinschaften. Stattdessen "
#               "verteilen sich die „Füchse“ auf fast drei Kladen: eine Graufuchs-Klade, eine Rotfuchs-Klade und eine Klade "
#               "mit ausschließlich südamerikanischen Wildhunden.",
#               "Twelve species belong to the monophyletic group of Vulpes genus of true foxes. Approximately another "
#               "25 current or extinct species are always or sometimes called foxes; these fast foxes are either part of the "
#               "paraphyletic group of the South American foxes, or of the outlying group, which consists of bat-eared "
#               "fox, gray fox, and island fox.",
#               "Particularité de la langue française, son développement et sa codification ont été en partie l’œuvre de "
#               "groupes intellectuels, comme la Pléiade, ou d’institutions, comme l’Académie française."]
# extractor = WordExtractor(test_texts, 'TEST_CASE')
# extractor.extract_words()
# extractor.print_words()
