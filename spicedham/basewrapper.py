from itertools import izip, repeat

class BaseWrapper(object):
    """
    A base class for backend plugins.
    """

    def reset(self):
        """
        Resets the training data to a blank slate.
        """
        raise NotImplementedError()


    def get_key(self, classifier, key, default=None):
        """
        Gets the value held by the classifier, key composite key.
        If it doesn't exist, return default.
        """
        raise NotImplementedError()


    def get_key_list(self, classifier, keys, default=None):
        """
        Given a list of key, classifier pairs get all values.
        If key, classifier doesn't exist, return default.
        Subclasses can override this to make more efficient queries for bulk
        requests.
        """
        return [self.get_key(classifier, key, default)
                for classifier, key in izip(repeat(classifier), keys)]


    def set_key_list(self, classifier, key_value_pairs):
        """
        Given a list of pairs of key, value  and a classifier set them all.
        Subclasses can override this to make more efficient queries for bulk
        requests.
        """
        return [self.set_key(classifier, key, value)
                for classifier, key, value
                in izip(repeat(classifier), key_value_pairs)]


    def set_key(self, classifier, key, value):
        """
        Set the value held by the classifier, key composite key.
        """
        raise NotImplementedError()
