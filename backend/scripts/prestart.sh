#! /usr/bin/env bash

set -e
set -x

# Run migrations
alembic upgrade head


# Update the database
python app/scripts/parse_git_words.py
