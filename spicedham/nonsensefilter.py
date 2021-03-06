from itertools import imap, repeat

from spicedham.plugin import BasePlugin


class NonsenseFilter(BasePlugin):
    """
    Filter messages with no words in the database.
    """

    def __init__(self, config, backend):
        """
        Get values from the config.
        """
        self.backend = backend
        nonsensefilter_config = config.get('nonsensefilter', {})
        self.filter_match = nonsensefilter_config.get('filter_match', 1)
        self.filter_miss = nonsensefilter_config.get('filter_miss', None)
    
    def train(self, classification_type, response, value):
        """
        Set each word to True.
        """
        self.backend.set_key_list(classification_type, self.__class__.__name__,
                                  set([(word, True) for word in response]))

    def explain(self, classification_type, response):
        """
        If the message contains only words not found in the database return
        filter_match and a string expanation. Else return filter_miss and a
        string explanation.
        """
        classifier = self.__class__.__name__
        list_in_dict = lambda x, y: not self.backend.get_key(classification_type, x, y, False)
        if all(imap(list_in_dict, repeat(classifier), response)):
            return (self.filter_match,
                    'None of the response\'s words were found in the backend')
        else:
            return (self.filter_miss,
                    'Some of the response\'s words were found in the backend')
