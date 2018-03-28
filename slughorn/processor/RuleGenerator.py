import logging
import os
from datetime import datetime

from slughorn.processor.util import BEST64_RULES

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
        self.final_rules.extend(BEST64_RULES)
        numbers = [number_object.number for number_object in self.expressions['numbers']] + list(range(101))

        for number in numbers:
            appending_rule = "".join((["${}".format(digit) for digit in str(number)]))
            prepending_rule = "".join((["^{}".format(digit) for digit in str(number)[::-1]]))
            for rule_function in ['l', 'u', 'c', 'C', 'r']:
                self.final_rules.append("{}{}".format(rule_function, appending_rule))
                self.final_rules.append("{}{}".format(rule_function, prepending_rule))

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
        for word in self.final_rules:
            output += str(word) + "\n"

        with open(file=file, mode='w+') as f:
            f.write(output)

        log.info("Successfully written rules to file {}".format(file))
