#!/bin/bash

# Activate virtual environment
source /opt/env/bin/activate

# Ensure /app/logs directory exists
mkdir -p /app1/logs

# Function to handle process termination
function terminate_processes {
    echo "Terminating processes..."
    pkill -f "python3 manage.py"
    pkill -f "daphne"
    exit
}

# Trap SIGTERM signal to gracefully terminate processes
trap terminate_processes SIGTERM

# Run Remote sensing script and handle errors
echo "Starting Remote sensing script..."
python3 manage.py testing &> /app1/logs/Remote_sensing.log &
if [ $? -ne 0 ]; then
    echo "Error starting Remote sensing script..."
    exit 1
fi



# Start Daphne server and handle errors
echo "Starting Django server..."
python3 manage.py runserver 0.0.0.0:8000 &> /app1/logs/django_server.log &
if [ $? -ne 0 ]; then
    echo "Error starting Django server"
    exit 1
fi

# Keep container running
wait