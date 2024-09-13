#!/bin/bash
export server="test"
if [ ! -d .venv ]; then
    python3 -m venv .venv
    source .venv/bin/activate
else
    source .venv/bin/activate

for d in */; do
    echo "Installing requirements for $d"
    if [ -f "$d"/requirements.txt ]; then
        pip install -r "$d"/requirements.txt
        echo "Creating .env file for $d/.env.$server.sample"
        cp "$d"/".env.$server.sample" "$d"/.env
    fi
done
fi