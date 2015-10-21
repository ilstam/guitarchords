#!/usr/bin/env python3
# Populate the database with some meaningful data.

import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guitarchords.settings')
django.setup()

from chords.fixtures import populate_data

populate_data.populate()
