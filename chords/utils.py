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
