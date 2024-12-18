#!/bin/bash

for i in $(seq 1 100); do
    curl -s -o /dev/null "http://localhost:80/search?query=Weapon&limit=50"
done

echo "Done"

