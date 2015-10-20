#!/usr/bin/env python3
# Populate the database with some meaningful data.

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guitarchords.settings')
django.setup()

from chords.fixtures import populate_data

populate_data.populate()
