class Word:

    def __init__(self, term, occurrences=0, frequency=0.0, exceptionalism=0, language=None, score=0):
        self.term = term
        self.occurrences = occurrences
        self.frequency = frequency
        self.exceptionalism = exceptionalism
        self.language = language
        self.score = score

    def __repr__(self):
        return "Word({0}, occ: {1}, freq: {2:.5f}, exc: {3:.5f}, sco: {4:.5f})".format(self.term, self.occurrences, self.frequency, self.exceptionalism, self.score)


class Number:

    def __init__(self, number, occurrences=0):
        self.number = number
        self.occurrences = occurrences

    def __repr__(self):
        return "Number({0}, occ: {1})".format(self.number, self.occurrences)
