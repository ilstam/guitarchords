#!/usr/bin/env bash
# delte database and migration files

cd ..
if [ -f db.sqlite3 ]; then
	rm db.sqlite3
fi
rm chords/migrations/*.py
rm -rf chords/migrations/__pycache__
touch chords/migrations/__init__.py
