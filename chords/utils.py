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
