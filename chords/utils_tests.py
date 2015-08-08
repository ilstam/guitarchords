#!/usr/bin/env python
# unit tests for the utils.py functions

import unittest

import utils


class TestUtils(unittest.TestCase):
    def test_strip_whitespace_lines(self):
        """
        The strip_empty_lines() function should remove all empty lines from
        end and begging and any adjacent whitespace lines inside.
        """
        s1 = """


        some identation here


lorem ipsum

"""
        s2 = """        some identation here

lorem ipsum"""
        self.assertEqual(utils.strip_whitespace_lines(s1), s2)

    def test_song_parsing(self):
        """
        A song must have all its chords enclosed in span tags after parsing and
        all empty lines in the begging end the end must be stripped.
        """
        orig = """
      @Am@  @G#@
Lorem ipsum, lorem ipsum

"""
        result = """      <span class="chord">Am</span>  <span class="chord">G#</span>
Lorem ipsum, lorem ipsum"""
        self.assertEqual(utils.parse_song(orig), result)


if __name__ == '__main__':
    unittest.main()
