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
        cp "$d"/".env.example.$server" "$d"/.env
    fi
done
fi