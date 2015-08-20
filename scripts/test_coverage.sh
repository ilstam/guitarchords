#!/bin/env bash
# run tests and display coverage report

cd ..
coverage run --source='chords' --omit=chords/tests/*,chords/migrations/* manage.py test chords
coverage report
