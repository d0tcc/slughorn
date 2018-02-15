from datetime import datetime
import os
import pickle
import logging

log = logging.getLogger('slughorn')


class PasswordGenerator:
    """
    A PasswordGenerator object represents one attempt to generate passwords from a list of extracted words.
    """

    def __init__(self, expressions, case_id, final_expressi=[]):
        """
        Init method of the PasswordGenerator Class

        :param words: List of Word objects extracted for a user
        :param case_id: String representation of the case number
        :param final_passwords: Final password list, is empty at initialization (parameter only for testing 
        purposes)
        """
        self.expressions = expressions
        self.case_id = case_id
        self.final_passwords = []

    def generate_passwords(self):
        """
        Starts the password generation process.
        DUMMY
        """
        # TODO DUMMY DUMMY DUMMY
        for word in self.expressions['words']:
            self.final_passwords.append(word.term)
        for number in self.expressions['numbers']:
            self.final_passwords.append(number.number)

    def write_to_file(self, directory='', pickled=False):
        """
        Writes generated passwords to a file.

        :param directory: Optional directory where the file will be located
        :param pickled: Whether the file should be a pickle (txt if False)
        """
        if not directory:
            directory = 'data/{}'.format(self.case_id)

        today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = os.path.join(directory, 'passwords_{}.{}'.format(today, ('pkl' if pickled else 'txt')))

        log.info("Writing generated passwords to file")
        if pickled:
            pickle.dump(self.final_passwords, open(file, "wb"))
        else:
            output = ''
            for word in self.final_passwords:
                output += str(word) + "\n"

            with open(file=file, mode='w+') as f:
                f.write(output)

        log.info("Successfully written to file {}".format(file))
