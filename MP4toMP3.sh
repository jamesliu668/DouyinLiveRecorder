#!/bin/bash

# Check if at least two arguments are provided
if [ "$#" -ne 2 ]; then
        echo "Usage: $0 <wav_directory> <mp3_directory>"
        exit 1
fi

# First argument is the directory containing .wav files
wav_directory="$1"

# Second argument is the output directory for the .mp3 files
mp3_directory="$2"

# Check if the output directory exists, if not create it
if [ ! -d "$mp3_directory" ]; then
    mkdir -p "$mp3_directory"
fi

# Loop through all .wav files in the directory
for wav_file in "$wav_directory"/*.mp4; do
    # Use basename to get the file name without the directory
    base_name=$(basename "$wav_file" .mp4)
    
    # Define the output file name
    mp3_file="$mp3_directory/$base_name.mp3"

    # Use ffprobe to get the bitrate and sample rate 
    # bitrate=$(ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$wav_file") 
    # sample_rate=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 "$wav_file") 
    # echo "Original Bitrate: $bitrate" 
    # echo "Original Sample Rate: $sample_rate Hz"
    
    # Convert .wav to .mp3 using FFmpeg
    # The -q:a 0 option tells FFmpeg to use the best quality setting for the MP3 files.
    # ffmpeg -i "$wav_file" -q:a 0 "$mp3_file"
    # bitrate 16k, sample rate 16k
    ffmpeg -i "$wav_file" -vn -ab 16K -ar 16000 "$mp3_file"
    
    echo "Converted $wav_file to $mp3_file"
    # bitrate=$(ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$mp3_file") 
    # sample_rate=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 "$mp3_file") 
    # echo "New Bitrate: $bitrate" 
    # echo "New Sample Rate: $sample_rate Hz"
done

echo "Conversion complete."
