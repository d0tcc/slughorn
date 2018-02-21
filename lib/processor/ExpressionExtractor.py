from lib.processor.ExpressionObjects import Word, Number
from lib.processor.external_libraries.germalemma.germalemma import GermaLemma
from lib.processor.util import URL_REGEX, VALID_UNICODES, ADDITIONAL_STOPWORDS

import logging
import pickle
from datetime import datetime
import click
import fastText
import os
import pycountry
import re
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordfreq import word_frequency, top_n_list

log = logging.getLogger('slughorn')

LANGUAGE_MODEL = fastText.load_model('lib/processor/models/lid.176.ftz')

with open('./lib/processor/models/nltk_german_classifier_data.pkl', 'rb') as f:
    tagger = pickle.load(f)

lemmatizer = GermaLemma(pickle='./lib/processor/external_libraries/germalemma/data/lemmata.pkl')


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
    cleaned_text = URL_REGEX.sub('', text)  # remove URLs
    ugly_characters = ['-', '_', '+', '>', '<', '*', '/', ]
    for character in ugly_characters:
        cleaned_text = cleaned_text.replace(character, ' ')

    #bad_characters = ['„', '“', '`', "'", '´', ',', '.', '…', '‚', '‘', '‘', '’', '«', '»', '‹', '›']
    # for character in bad_characters:
    #     cleaned_text = cleaned_text.replace(character, '')
    cleaned_text = "".join(i for i in cleaned_text if ord(i) in VALID_UNICODES)

    return cleaned_text


def remove_stopwords(text, language_code):
    """
    Removes stopwords from text

    Removes all stopwords in the language of the text and returns all words which are longer than 1 character
    together as a list
    :param text: Text the stopwords will be removed from
    :param language_code: Language Code (alpha_2, e.g. 'en') of the text
    :return: List of non-stopwords longer than 2 character
    """
    language_name = pycountry.languages.get(alpha_2=language_code).name.lower()
    stop_words = set(stopwords.words(language_name))
    stop_words.update(['``', "''"])  # add double quotes because of weird facebook encoding
    additional_stopwords = ADDITIONAL_STOPWORDS.get(language_name, [])
    stop_words.update(additional_stopwords)
    #text = clean_text(text)
    words = word_tokenize(text, language=language_name)
    filtered_strings = [word.lower() for word in words if word.lower() not in stop_words and len(word) > 2]
    return filtered_strings


def separate_words_and_numbers(strings):
    """
    Separates words and numbers into two lists.
    
    :param strings: List of strings.
    :return: One list of words and one list of numbers
    """
    filtered_words = []
    filtered_numbers = []
    for string in strings:
        if string.isdigit():
            filtered_numbers.append(string)
        else:
            filtered_words.append(string)
    return filtered_words, filtered_numbers


def lemmatize_words(text):
    """
    Lemmatizes german words, i.e. finds the base form ("Kühe" --> "Kuh", "gingen" --> "gehen")
    
    Uses a self trained german classifier to tag the components of a sentence into the categories 
    Nouns, Adverbs, Adjectives and Verbs
    
    :param text: Text
    :return: list of lemmatized words
    """
    word_list = text.split()
    tagged_words = tagger.tag(word_list)

    base_words = []

    for word in tagged_words:
        try:
            lemma = lemmatizer.find_lemma(word[0], word[1])
        except ValueError:
            lemma = word[0]
        base_words.append(lemma)
    return base_words


def calculate_exceptionalism(word_dict):
    """
    Detects how common the words are in their language using 'wordfreq'
    word_frequency returns the share the word has in the language, with 1 if there is only one word in the corpus and 0
    being an unknown word.
    The value is Min-Max scaled by dividing it by the value of the word with the highest commonness.
    To get the exceptionalism of a word the value is substracted from 1.
        
    :param word_dict: dictionary of words
    :return: 
    """
    # def get_highest_frequency(word_dict):
    #     """
    #     Returns the highest possible frequency of any word in all given langauges.
    #     The value is then used to Min-Max scale the frequency of words.
    #
    #     :param word_dict: dictionary of words
    #     :return: The highest frequency of the most common word in all languages
    #     """
    #     highest_frequency = 0.0
    #     for language in word_dict:
    #         try:
    #             frequency = word_frequency(top_n_list(language, wordlist='large', n=1)[0], language, wordlist='large')
    #             if frequency > highest_frequency:
    #                 highest_frequency = frequency
    #         except ValueError:
    #             pass
    #     return highest_frequency

    highest_frequency = 0.0
    highest_word = ""
    with click.progressbar(word_dict.items(), label='Calculating exceptionalism', show_eta=False) as bar:
        for language, words in bar:
            for word, attributes in words.items():
                frequency = word_frequency(word, language, wordlist='large')
                attributes['exceptionalism'] = frequency
                # save highest frequency for Min-Max Scaling
                if frequency > highest_frequency:
                    highest_frequency = frequency
                    highest_word = word

    # perform Min-Max Scaling (dividing by the maximum value appearing)
    click.echo("Highest Frequency (exc): {} {}".format(highest_frequency, highest_word))
    for language, words in word_dict.items():
        for word, attributes in words.items():
            attributes['exceptionalism'] = 1 - (attributes['exceptionalism'] / highest_frequency)


def calculate_frequency(word_dict):
    """
    Calculates how often the words is used in all postings of the target person.
    The amount of occurrences of every word is divided by the amount of all words together. This results in the share of
    this word.
    The value is Min-Max scaled by dividing it by the value of the word with the highest share.
    
    :param word_dict: dictionary of words
    :return: 
    """
    total_amount_words = 0
    for language, words in word_dict.items():
        for word, attributes in words.items():
            total_amount_words += attributes['occurrences']

    click.echo("total amount of words: {}".format(total_amount_words))
    highest_frequency = 0.0
    highest_word = ''
    with click.progressbar(word_dict.items(), label='Calculating frequency', show_eta=False) as bar:
        for language, words in bar:
            for word, attributes in words.items():
                frequency = attributes['occurrences'] / total_amount_words
                attributes['frequency'] = frequency
                # save highest frequency for Min-Max Scaling
                if frequency > highest_frequency:
                    highest_frequency = frequency
                    highest_word = word

    # perform Min-Max Scaling (dividing by the maximum value appearing)
    click.echo("Highest Frequency: {} {}".format(highest_frequency, highest_word))
    for language, words in word_dict.items():
        for word, attributes in words.items():
            attributes['frequency'] /= highest_frequency


def calculate_score(word_dict):
    """
    Calculates the score of each word.
    The score of word is the product of its exceptionalism and its number of occurrences. A higher value means that 
    the word is a better candidate for a password.
    
    :param word_dict: dictionary of words
    :return:
    """
    with click.progressbar(word_dict.items(), label='Calculating score', show_eta=False) as bar:
        for language, words in bar:
            for word, attributes in words.items():
                attributes['score'] = 0.5 * attributes['exceptionalism'] + 0.5 * attributes['frequency']


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
    with click.progressbar(word_dict.items(), label='Combining False Friends', show_eta=False) as bar:
        for language1, words1 in bar:
            for language2, words2 in word_dict.items():
                if language1 == language2:
                    continue
                else:
                    for intersection in set(words1).intersection(set(words2)):
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
    with click.progressbar(word_dict.items(), label='Creating final word list', show_eta=False) as bar:
        for language, words in bar:
            for word, attributes in words.items():
                final_word_list.append(Word(term=word,
                                            occurrences=attributes['occurrences'],
                                            frequency=attributes['frequency'],
                                            exceptionalism=attributes['exceptionalism'],
                                            language=language,
                                            score=attributes['score']))
    final_word_list.sort(key=lambda x: x.score, reverse=True)
    return final_word_list


def create_final_number_list(number_dict):
    """
    Creates a list of Number objects from the dictionary of words and sorts it descending by occurences.

    :param number_dict: dictionary of numbers
    :return: A list of Number objects containing all information of the number_dict, sorted by occurences descending
    """
    final_number_list = []
    with click.progressbar(number_dict.items(), label='Creating final number list', show_eta=False) as bar:
        for number, occurrences in bar:
            final_number_list.append(Number(number, occurrences))
    final_number_list.sort(key=lambda x: x.occurrences, reverse=True)
    return final_number_list


def ddint():
    return defaultdict(int)


def dd():
    return defaultdict(ddint)


class ExpressionExtractor:
    """
    A WordExtractor object represents one attempt to extract words and numbers from a list of posts.
    """

    def __init__(self, texts, case_id, final_expressions={}):
        """
        Init method of the WordExtractor Class
        
        :param texts: List of texts from a user
        :param case_id: String representation of the case number
        :param final_word_list: Final word list, is empty at initialization (parameter only for testing purposes)
        :param final_number_list: Final number list, is empty at initialization (parameter only for testing purposes)
        """
        self.texts = texts
        self.case_id = case_id
        self.final_expressions = final_expressions

    def extract_words_and_numbers(self):
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

        extracted_words = defaultdict(dd)
        extracted_numbers = defaultdict(int)

        def update_word_dict(words, language):
            """
            Helper function to update the extracted_words dictionary for every text.
            Increments the occurrences of each word.
            
            :param words: extracted words per single text
            :param language: the language of the text
            :return: 
            """
            for word in words:
                extracted_words[language][word]['occurrences'] += 1

        def update_number_dict(numbers):
            """
            Helper function to update the extracted_words dictionary for every text.
            Increments the occurrences of each word.

            :param numbers: extracted numbers per single text
            :return: 
            """
            for number in numbers:
                extracted_numbers[number] += 1

        log.debug("Filtering posts ...")
        with click.progressbar(self.texts, label='Filtering {} posts'.format(len(self.texts)), show_eta=True) as bar:
            for text in bar:
                language_code = detect_language(text)
                cleaned_text = clean_text(text)
                if language_code == 'de':
                    filtered_words = lemmatize_words(cleaned_text)
                    cleaned_text = " ".join(filtered_words)
                    #filtered_words = remove_stopwords(" ".join(filtered_words), language_code)
                filtered_strings = remove_stopwords(cleaned_text, language_code)
                filtered_words, filtered_numbers = separate_words_and_numbers(filtered_strings)

                update_number_dict(filtered_numbers)
                update_word_dict(filtered_words, language_code)

        pickle.dump(extracted_words, open('data/filtered_words.pkl', "wb"))
        pickle.dump(extracted_numbers, open('data/filtered_numbers.pkl', "wb"))

        # extracted_words = pickle.load(open('data/filtered_words.pkl', 'rb'))
        # extracted_numbers = pickle.load(open('data/filtered_numbers.pkl', 'rb'))

        log.debug("Calculating exceptionalism of words ...")
        calculate_exceptionalism(extracted_words)
        log.debug("Calculating frequency of words ...")
        calculate_frequency(extracted_words)
        log.debug("Combining False Friends ...")
        combine_false_friends(extracted_words)
        log.debug("Calculating score ...")
        calculate_score(extracted_words)

        final_word_list = create_final_word_list(extracted_words)
        final_number_list = create_final_number_list(extracted_numbers)
        self.final_expressions = {'words': final_word_list, 'numbers': final_number_list}
        log.info("Finished extraction of words and numbers!")

    def print_expressions(self):
        """
        Prints the words and numbers in the final expression list

        :return: 
        """
        for word in self.final_expressions['words']:
            print(word.term)
        for number in self.final_expressions['numbers']:
            print(number.number)

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
        file = os.path.join(directory, 'expressions_{}.{}'.format(today, ('pkl' if pickled else 'txt')))

        log.info("Writing extracted expressions to file")
        if pickled:
            with open(file, "wb") as f:
                pickle.dump(self.final_expressions, f)
        else:
            output = ''
            for word in self.final_expressions['words']:
                output += str(word) + "\n"
            for number in self.final_expressions['numbers']:
                output += str(number) + "\n"

            with open(file=file, mode='w+') as f:
                f.write(output)

        log.info("Successfully written to file {}".format(file))