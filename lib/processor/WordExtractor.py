import fastText
import pycountry
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

LANGUAGE_MODEL = fastText.load_model('./models/lid.176.ftz')

class WordExtractor:

    def __init__(self, texts):
        self.texts = texts

    def detect_language(self, text):
        """
        Detects the language of a text

        Detects the language of a text with fastText and returns the name of a language
        The model for language identification comes from fasttext:
        https://fasttext.cc/docs/en/language-identification.html

        k = 1 in the predict method returns only the most probable language
        """
        language_label, probability = LANGUAGE_MODEL.predict(text, k=1)
        language_abbrevation = language_label[0].replace('__label__', '')
        most_probable_language = pycountry.languages.get(alpha_2=language_abbrevation).name.lower()
        return most_probable_language

    def remove_stopwords(self):
        """
        Removes stopwords from texts

        Removes all stopwords in the language of the text and returns all words which are longer than 1 character
        together as a list
        :return:
        """
        result_list = []
        for text in self.texts:
            language = self.detect_language(text)
            stop_words = set(stopwords.words(language))
            words = word_tokenize(text)
            filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 1]
            result_list.extend(filtered_words)
        return result_list


    def count_occurrences(self):
        pass

    def estimate_commonness(self):
        pass

    def calculate_score(self):
        pass

test_texts = ["Nach aktuellen, auf DNA-Vergleichen beruhenden Verwandtschaftsanalysen sind diese traditionell "
              "ausgehaltenen Gattungsgruppen ebenfalls keine geschlossenen Abstammungsgemeinschaften. Stattdessen "
              "verteilen sich die „Füchse“ auf drei Kladen: eine Graufuchs-Klade, eine Rotfuchs-Klade und eine Klade "
              "mit ausschließlich südamerikanischen Wildhunden.",
              "Twelve species belong to the monophyletic group of Vulpes genus of true foxes. Approximately another "
              "25 current or extinct species are always or sometimes called foxes; these foxes are either part of the "
              "paraphyletic group of the South American foxes, or of the outlying group, which consists of bat-eared "
              "fox, gray fox, and island fox.",
              "Particularité de la langue française, son développement et sa codification ont été en partie l’œuvre de "
              "groupes intellectuels, comme la Pléiade, ou d’institutions, comme l’Académie française."]
extractor = WordExtractor(test_texts)
print(extractor.remove_stopwords())