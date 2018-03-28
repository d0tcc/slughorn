import logging
import os
import pickle
from datetime import datetime

log = logging.getLogger('slughorn')


class RuleGenerator:
    """
    A RuleGenerator object represents one attempt to generate a rule set from a list of extracted expressions.
    """

    def __init__(self, expressions, case_id):
        """
        Init method of the RuleGenerator Class

        :param expressions: Dictionary of excpression objects extracted from a user
        :param case_id: String representation of the case number
        """
        self.expressions = expressions
        self.case_id = case_id
        self.final_rules = []

    def generate_rules(self):
        """
        Starts the rule generation process.
        """
        for number in self.expressions['numbers']:
            appending_rule = "".join((["${}".format(digit) for digit in str(number)]))
            prepending_rule = "".join((["^{}".format(digit) for digit in str(number)[::-1]]))
            for rule_function in ['', 'l', 'u', 'c', 'r']:
                self.final_rules.append("{}{}".format(appending_rule, rule_function))
                self.final_rules.append("{}{}".format(prepending_rule, rule_function))

    def write_to_file(self, directory=''):
        """
        Writes generated rules to a file.

        :param directory: Optional directory where the file will be located
        """
        if not directory:
            directory = 'data/{}'.format(self.case_id)

        today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = os.path.join(directory, 'rules_{}.{}'.format(today, 'rules'))

        log.info("Writing generated rules to file")
        output = ''
        for word in self.final_passwords:
            output += str(word) + "\n"

        with open(file=file, mode='w+') as f:
            f.write(output)

        log.info("Successfully written rules to file {}".format(file))
