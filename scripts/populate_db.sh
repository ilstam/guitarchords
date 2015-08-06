#!/bin/env bash
# make db migrations, populate some data and create a superuser

cd ..
./manage.py makemigrations chords
./manage.py migrate
./populate_chords.py
./manage.py createsuperuser
