import re
import itertools

from django.template.defaultfilters import slugify


def greek_to_english(string):
    """
    Converts all greek letters to the corresponding english letters.
    Useful for creating song slugs from greek song titles.
    """
    GREEK_MAP = {
        'α':'a', 'β':'b', 'γ':'g', 'δ':'d', 'ε':'e', 'ζ':'z', 'η':'h',  'θ':'th',
        'ι':'i', 'κ':'k', 'λ':'l', 'μ':'m', 'ν':'n', 'ξ':'ks', 'ο':'o', 'π':'p',
        'ρ':'r', 'σ':'s', 'τ':'t', 'υ':'y', 'φ':'f', 'χ':'x', 'ψ':'ps', 'ω':'w',
        'ά':'a', 'έ':'e', 'ί':'i', 'ό':'o', 'ύ':'y', 'ή':'h', 'ώ':'w',  'ς':'s',
        'ϊ':'i', 'ΰ':'y', 'ϋ':'y', 'ΐ':'i',
        'Α':'A', 'Β':'B', 'Γ':'G', 'Δ':'D', 'Ε':'E', 'Ζ':'Z', 'Η':'H',  'Θ':'Th',
        'Ι':'I', 'Κ':'K', 'Λ':'L', 'Μ':'M', 'Ν':'N', 'Ξ':'Ks', 'Ο':'O', 'Π':'P',
        'Ρ':'R', 'Σ':'S', 'Τ':'T', 'Υ':'Y', 'Φ':'F', 'Χ':'X', 'Ψ':'Ps', 'Ω':'W',
        'Ά':'A', 'Έ':'E', 'Ί':'I', 'Ό':'O', 'Ύ':'Y', 'Ή':'H', 'Ώ':'W',  'Ϊ':'I',
        'Ϋ':'Y'
    }

    s = "".join(GREEK_MAP.keys())

    result = ''
    for piece in re.compile('[%s]|[^%s]+' % (s,s)).findall(string):
        if piece in GREEK_MAP:
            result += GREEK_MAP[piece]
        else:
            result += piece

    return result.replace('oy', 'ou').replace('OY', 'OU').replace('Oy', 'Ou')

def slugify_greek(string):
    return slugify(greek_to_english(string))

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
    slug = orig = slugify_greek(string)[:max_length]

    for x in itertools.count(1):
        if not cls.objects.filter(slug=slug).exists():
            break

        # truncate the original slug dynamically, minus 1 for the hyphen
        slug = "{0}-{1}".format(orig[:max_length - len(str(x)) - 1], x)

    return slug

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
