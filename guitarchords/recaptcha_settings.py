# recaptcha settings

from .settings import PRODUCTION

NOCAPTCHA = True  # if True, use the new No Captcha reCaptcha

RECAPTCHA_PUBLIC_KEY = '6Le9nQ0TAAAAALp08H8WCEg3EVZzwWZ3d7xJ4JoN'

if PRODUCTION:
    RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']
else:
    RECAPTCHA_PRIVATE_KEY = '6Le9nQ0TAAAAAJl93EqP0M0loXz_EVe_KXLl7DzP'
