import re
import itertools

from django.template.defaultfilters import slugify


def generate_unique_slug(cls, string, max_length=-1):
    """
    Creates a slug with the appropriate maximum length.
    To ensure uniqueness, it adds a integer suffix to the slug if the
    "appropriate" slug is already used by some other object.

    Keyword arguments:
    cls        -- the class of the model
    string     -- the string to slugify
    max_length -- maximum length of the resulting slug. if negative, we will
                  use the max_length of the slug field of the cls
    """
    if max_length < 0:
        max_length = cls._meta.get_field('slug').max_length
    slug = orig = slugify(string)[:max_length]

    for x in itertools.count(1):
        if not cls.objects.filter(slug=slug).exists():
            break

        # truncate the original slug dynamically, minus 1 for the hyphen
        slug = "{0}-{1}".format(orig[:max_length - len(str(x)) - 1], x)

    return slug

def greek_to_english_letters(s):
    """
    Converts all greek letters to lowercase english letters.
    Useful for creating song slugs from greek song titles.
    """
    from_chars = 'αβγδεζηθικλμνξοπρσςτυφχψωάήέίόύώϊϋ'
    to_chars = 'abgdezh8iklmn3oprsstyfxqwaheioywiy'

    s = s.lower().translate(str.maketrans(from_chars, to_chars)).replace('q', 'ps')
    return s.replace('8', 'th').replace('3', 'ks').replace('oy', 'ou')

def parse_song(song):
    """
    Parse song and enclose every chord in span tags of class "chord".

    Chords are surrounded by @ symbols.
    So "lorem @G#dim7@ ipsum" should become "<span class="chord">G#dim7</span>".

    It will also strip empty lines from the end and beginning of the song.
    """
    song = song.strip('\n')
    return re.sub('(^|\s)@([\S]+)@(\s|$)', r'\1<span class="chord">\2</span>\3',
                  song)

def strip_whitespace_lines(string):
    """
    Remove whitespace lines from the beginning and the end of the string,
    as well as adjacent whitespace lines inside.
    """
    lines = [(l.strip() if not l.strip() else l) for l in string.splitlines()]

    # remove whitespace lines from beginning and end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    # remove any adjacent whitespace lines
    lines = [l[0] for l in itertools.groupby(lines)]

    return '\n'.join(lines)

def is_chord(s):
    """
    Return True, if the string represents a guitar chord.
    It will return True for invalid chords like B# as well.
    """
    return bool(re.match(r'^[A-G][#b]?(maj|m|aug|dim)?[67]?$', s))
