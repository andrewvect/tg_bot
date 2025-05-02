#! /usr/bin/env bash

set -e
set -x

# Run migrations
alembic upgrade head


# Update the database words
# python app/scripts/parse_git_words.py

# # Update webhook
# python app/scripts/tg_webhook.py
