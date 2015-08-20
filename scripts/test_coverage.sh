#!/bin/env bash
# run tests and display coverage report

cd ..
coverage run --source='.' --omit=guitarchords/*,populate_chords.py,manage.py,chords/tests.py,chords/migrations/* manage.py test chords
coverage report
