#!/bin/env bash
# run tests and display coverage report

cd ..
coverage run --source='.' manage.py test chords
coverage report
