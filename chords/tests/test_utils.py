from django.test import TestCase, SimpleTestCase, RequestFactory

from chords import utils


class TestUtils(SimpleTestCase):
    def test_strip_whitespace_lines_strips_whitespace(self):
        """
        The strip_empty_lines() function should remove all empty lines from
        end and begging and any adjacent whitespace lines inside.
        """
        s1 = '  \t\n\n\t \tsome identation here\n\n\n\nlorem ipsum\n\n'
        s2 =         '\t \tsome identation here\n\nlorem ipsum'
        self.assertEqual(utils.strip_whitespace_lines(s1), s2)

    def test_strip_whitespace_lines_not_strip_no_whitespace_lines(self):
        """
        The strip_empty_lines() function should not remove any other adjacent
        lines except whitespace lines.
        """
        s = 'lorem ipsum\nlorem ipsum'
        self.assertEqual(utils.strip_whitespace_lines(s), s)
