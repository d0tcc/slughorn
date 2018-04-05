import logging
import os
import pickle
from datetime import datetime

log = logging.getLogger('slughorn')


class WordListGenerator:
    """
    A WordListGenerator object represents one attempt to generate a word list from a list of extracted words.
    """

    def __init__(self, expressions, case_id):
        """
        Init method of the WordListGenerator Class

        :param expressions: Dictionary of expression objects extracted from a user
        :param case_id: String representation of the case number
        """
        self.expressions = expressions
        self.case_id = case_id
        self.final_word_list = []

    def generate_word_list(self):
        """
        Starts the password generation process.
        
        """
        for word in self.expressions['words']:
            self.final_word_list.append(word.term)
        # for number in self.expressions['numbers']:
        #     self.final_passwords.append(number.number)

    def write_to_file(self, directory='', pickled=False):
        """
        Writes generated word list to a file.

        :param directory: Optional directory where the file will be located
        :param pickled: Whether the file should be a pickle (txt if False)
        """
        if not directory:
            directory = 'data/{}'.format(self.case_id)

        today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = os.path.join(directory, 'word_list_{}.{}'.format(today, ('pkl' if pickled else 'txt')))

        log.info("Writing generated word_list to file")
        if pickled:
            with open(file, "wb") as f:
                pickle.dump(self.final_word_list, f)
        else:
            output = ''
            for word in self.final_word_list:
                output += str(word) + "\n"

            with open(file=file, mode='w+') as f:
                f.write(output)

        log.info("Successfully written to file {}".format(file))
