__author__ = 'riot'

class nmeaFilter(object):
    """Filters out sentences by given type
    """

    def __init__(self, sentencetype):
        self.sentencetype = sentencetype

    def filter(self, sentences):
        for sentence in sentences:

            if sentence['type'] == self.sentencetype:
                return sentence
