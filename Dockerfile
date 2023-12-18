# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the Python script and requirements.txt into the container
COPY main.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script once a minute using cron
CMD ["sh", "-c", "while true; do python main.py; sleep 60; done"]
