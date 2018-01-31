class Word:

    def __init__(self, term, occurrences=0, exceptionalism=0, language=None, score=0):
        self.term = term
        self.occurrences = occurrences
        self.exceptionalism = exceptionalism
        self.language = language
        self.score = score

    def __repr__(self):
        return "Word({}, occ: {}, comm: {}, sco: {})".format(self.term, self.occurrences, self.exceptionalism, self.score)