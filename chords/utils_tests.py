#!/usr/bin/env python

import unittest

import utils


class TestUtils(unittest.TestCase):
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
