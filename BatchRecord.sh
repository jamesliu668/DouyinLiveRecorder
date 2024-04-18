#!/bin/bash

# 从目标文件中选取配置文件，并运行爬取任务
# 爬取任务总数量不超过 max_python_processes
# mac不支持shuf

# Maximum allowed number of Python processes
max_python_processes=15

# Check if at least two arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <config_directory>"
    exit 1
fi

# First argument is the directory containing .json files
config_directory="$1"

# Check the total number of running Python processes on the system
python_process_count=$(ps aux | grep python | grep -c "$config_directory")

# Check if the total number of Python processes exceeds the limit
if [ "$python_process_count" -ge "$max_python_processes" ]; then
    echo "Maximum number of Python processes reached. Exiting."
    exit 1
fi


# Check if the output directory exists, if not create it
if [ ! -d "$config_directory" ]; then
    echo "Error: $config_directory does not exist!"
    exit 1
fi

# List all .json files in the directory and shuffle them 
file_list=("$config_directory"/*.json) 
# shuf_files=($(shuf -e "${file_list[@]}")) # ony work in linux

# Shuffle the array and select the first 5 elements
random_indices=($(shuf -i 0-$((${#file_list[@]} - 1)) -n "$max_python_processes"))

# Loop through all .json files in the directory
for index in "${random_indices[@]}"; do
    configFile=("${file_list[$index]}")
    base_name=$(basename "$configFile" .json)
    log_name="$base_name.log"
    # Execute the Python script and redirect output to log file
    result=$(nohup python3 main.py "$configFile" >> logs/"$log_name" 2>&1 &)
    echo "Started recording $configFile"

    python_process_count=$(ps aux | grep python | grep -c "$config_directory")
    # Check if the counter exceeds the limit
    if [ "$python_process_count" -ge "$max_python_processes" ]; then
        echo "Python script execution limit reached. Exiting."
        break
    fi
done