# settings specific to the django-registration-redux app

REGISTRATION_OPEN = True         # users can register
ACCOUNT_ACTIVATION_DAYS = 7      # one-week activation window
LOGIN_REDIRECT_URL = '/'         # redirect here after a successful log in
LOGIN_URL = '/accounts/login/'   # the page users are directed to if they are not logged in,
                                 # and are trying to access pages requiring authentication
REGISTRATION_EMAIL_HTML = False  # disable html emails (just use the txt version)
