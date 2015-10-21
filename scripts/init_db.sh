#!/usr/bin/env bash
# make db migrations, populate some data and create a superuser

../manage.py makemigrations chords
../manage.py migrate
echo ""
./populate_chords.py
echo ""
../manage.py createsuperuser
