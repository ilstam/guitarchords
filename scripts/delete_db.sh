#!/bin/env bash
# delte database and migration files

cd ..
if [ -f db.sqlite3 ]; then
	rm db.sqlite3
fi
rm chords/migrations/*.py
touch chords/migrations/__init__.py
