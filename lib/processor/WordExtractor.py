from lib.processor.Word import Word

import fastText
import pycountry
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from wordfreq import zipf_frequency
from collections import defaultdict

LANGUAGE_MODEL = fastText.load_model('./models/lid.176.ftz')


def detect_language(text):
    """
    Detects the language of a text

    Detects the language of a text with fastText and returns the alpha_2 representation of a language (e.g. 'en')
    The model for language identification comes from fasttext:
    https://fasttext.cc/docs/en/language-identification.html

    k = 1 in the predict method returns only the most probable language
    """
    language_label, probability = LANGUAGE_MODEL.predict(text, k=1)
    language_code = language_label[0].replace('__label__', '')
    return language_code


def clean_text(text):
    bad_characters = ['„', '“']
    for character in bad_characters:
        text = text.replace(character, '')
    return text


def remove_stopwords(text, language_code):
    """
    Removes stopwords from text

    Removes all stopwords in the language of the text and returns all words which are longer than 1 character
    together as a list
    :return:
    """
    result_list = []
    text = clean_text(text)
    language_name = pycountry.languages.get(alpha_2=language_code).name.lower()
    stop_words = set(stopwords.words(language_name))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 1]
    result_list.extend(filtered_words)
    return result_list


def calculate_exceptionalism(word_dict):
    for language, words in word_dict.items():
        for word, attributes in words.items():
            attributes['exceptionalism'] = 8 - zipf_frequency(word, language, wordlist='large')  # calculate exceptionalism


def calculate_score(word_dict):
    for language, words in word_dict.items():
        for word, attributes in words.items():
            attributes['score'] = attributes['exceptionalism'] * attributes['occurrences']  # calculate score


def combine_false_friends(word_dict):
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

    def __init__(self, texts):
        self.texts = texts
        self.final_word_list = []

    def extract_words(self):
        """
        example for
        extracted_words = {
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
        :return:
        """

        extracted_words = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        def update_language_dict(words, language):
            for word in words:
                extracted_words[language][word]['occurrences'] += 1

        for text in self.texts:
            language_code = detect_language(text)
            filtered_words = remove_stopwords(text, language_code)
            update_language_dict(filtered_words, language_code)

        calculate_exceptionalism(extracted_words)
        combine_false_friends(extracted_words)
        calculate_score(extracted_words)
        self.final_word_list = create_final_word_list(extracted_words)

    def print_words(self):
        for word in self.final_word_list:
            print(word)


test_texts = ["Nach aktuellen, auf DNA-Vergleichen beruhenden Verwandtschaftsanalysen sind diese traditionell "
              "ausgehaltenen Gattungsgruppen ebenfalls keine geschlossenen Abstammungsgemeinschaften. Stattdessen "
              "verteilen sich die „Füchse“ auf fast drei Kladen: eine Graufuchs-Klade, eine Rotfuchs-Klade und eine Klade "
              "mit ausschließlich südamerikanischen Wildhunden.",
              "Twelve species belong to the monophyletic group of Vulpes genus of true foxes. Approximately another "
              "25 current or extinct species are always or sometimes called foxes; these fast foxes are either part of the "
              "paraphyletic group of the South American foxes, or of the outlying group, which consists of bat-eared "
              "fox, gray fox, and island fox.",
              "Particularité de la langue française, son développement et sa codification ont été en partie l’œuvre de "
              "groupes intellectuels, comme la Pléiade, ou d’institutions, comme l’Académie française."]
extractor = WordExtractor(test_texts)
extractor.extract_words()
extractor.print_words()
