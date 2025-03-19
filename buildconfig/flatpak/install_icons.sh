#!/bin/bash

# Define the sizes you want to install
sizes=(16 32 48 64 128)

# Loop through each size and install the corresponding icon
for size in "${sizes[@]}"; do
    install -Dm755 "mods/tuxemon/gfx/icon_${size}.png" "/app/share/icons/hicolor/${size}x${size}/apps/icon.png"
done