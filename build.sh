#!/usr/bin/env bash
set -e

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "Using Python standard library. No external pip dependencies required."
fi
