from itertools import izip, cycle
from unittest import TestCase

from spicedham.bayes import Bayes
from spicedham import Spicedham


class TestBayes(TestCase):

    def test_classify(self):
        classification_type = 'type'
        sh = Spicedham()
        b = Bayes(sh.config, sh.backend)
        b.backend.reset()
        self._training(classification_type, b)
        alphabet = map(chr, range(97, 123))
        for letter in alphabet:
            p = b.classify(classification_type, letter)
            self.assertEqual(p, 0.5)

    def test_explain(self):
        sh = Spicedham()
        b = Bayes(sh.config, sh.backend)
        b.backend.reset()
        self._training(b)
        alphabet = map(chr, range(97, 123))
        for letter in alphabet:
            p, explanation = b.explain(letter)
            self.assertEqual(p, 0.5)
            self.assertEqual(type(explanation), unicode)

    def _training(self, classification_type, bayes):
        alphabet = map(chr, range(97, 123))
        reversed_alphabet = reversed(alphabet)
        messagePairs = izip(alphabet, reversed_alphabet)
        for message, is_spam in izip(messagePairs, cycle((True, False))):
            bayes.train(classification_type, message, is_spam)

    def test_train(self):
        classification_type = 'type'
        alphabet = map(chr, range(97, 123))
        sh = Spicedham()
        b = Bayes(sh.config, sh.backend)
        b.backend.reset()
        self._training(classification_type, b)
        for letter in alphabet:
            result = sh.backend.get_key(classification_type,
                                        b.__class__.__name__, letter)
            self.assertEqual(result, {'numTotal': 2, 'numSpam': 1})
            self.assertTrue(result['numTotal'] >= result['numSpam'])
