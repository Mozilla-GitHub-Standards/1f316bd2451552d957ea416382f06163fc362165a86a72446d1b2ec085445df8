from spicedham.baseplugin import BasePlugin
from spicedham.basebackend import BaseBackend
from spicedham.baseconfig import BaseConfig
# Import for the side effect of getting access to subclasses
# TODO: This is gross
import spicedham.gottaimportthemall


class NoBackendFoundError(Exception):
    pass


class Spicedham(object):

    _classifier_plugins = []
    backend = None
    # Default config values
    config = {
        'backend': 'SqlAlchemyWrapper',
        'engine': 'sqlite:///./spicedham.db',
    }

    def all_subclasses(self, cls):
        subc = cls.__subclasses__()
        for d in list(subc):
            subc.extend(self.all_subclasses(d))
        return subc

    def __init__(self, config=None):
        """
        Load config, backend, and plugins
        """
        if config is not None:
            self.config = config
        self._load_backend()
        self._load_plugins()

    def _load_plugins(self):
        # In order to use the plugins config and backend must be loaded.
        self._classifier_plugins = []
        for plugin_class in self.all_subclasses(BasePlugin):
            self._classifier_plugins.append(
                plugin_class(self.config, self.backend))

    def _load_backend(self):
        try:
            get_name = lambda x: x.__name__ == self.config['backend']
            plugin_class = filter(get_name, self.all_subclasses(BaseBackend))
            plugin_class = plugin_class[0]
        except IndexError:
            raise NoBackendFoundError()
        self.backend = plugin_class(self.config)

    def train(self, training_data, match):
        """
        Calls each plugin's train function.
        `training_data` is an iterable of strings. `match` is a boolean
        indicating whether the training data should be matched.
        For instance, if you're filtering spam `match` will be True for spam,
        and False for a normal message.
        """
        for plugin in self._classifier_plugins:
            plugin.train(training_data, match)

    def classify(self, classification_data):
        """
        Calls each plugin's classify function and averages the results.
        `classification_data` is an iterable of strings.
        """
        average_score = 0
        total = 0
        for plugin in self._classifier_plugins:
            value = plugin.classify(classification_data)
            # Skip _plugins which give a score of None
            if value is not None:
                total += 1
                average_score += value
        # On rare occasions no _plugins will give scores. If so, return 0
        if total > 0:
            return float(average_score) / float(total)
        else:
            return 0
