# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app1

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    mesa-utils \
    libasound2-dev \
    gdal-bin \
    libgdal-dev \
    supervisor && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Create and activate a virtual environment
RUN python3 -m venv /opt/env
ENV PATH="/opt/env/bin:$PATH"

# Copy the requirements file into the container at /app
COPY requirements.txt /app1/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container at /app
COPY . /app1/

# Add configuration for Google Earth Engine JSON key
COPY earth-engine-cloud-471609-d2c7ef4caa59.json /app1/earth-engine-cloud-471609-d2c7ef4caa59.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app1/earth-engine-cloud-471609-d2c7ef4caa59.json

# Copy the supervisord script file
COPY all_commands.sh /app1/all_commands.sh
RUN chmod +x /app1/all_commands.sh

# Expose the port the app runs on
EXPOSE 8000

# Run all_commands
CMD ["/app1/all_commands.sh"]
