#!/bin/bash

# Check if at least two arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <config_directory>"
    exit 1
fi

# First argument is the directory containing .wav files
config_directory="$1"


# Check if the output directory exists, if not create it
if [ ! -d "$config_directory" ]; then
    echo "Error $config_directory not exist!"
    exit 1
fi


# Loop through all .wav files in the directory
for configFile in "$config_directory"/*.json; do
    log_name=$(basename "$configFile" .log)
    result=$(nohup python3 main.py "$configFile" > "$log_name" 2>&1 &)
    echo "开始录制$configFile"
done