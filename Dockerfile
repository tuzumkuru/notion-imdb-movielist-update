# Use the official Python image as a base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the application files into the container
COPY *.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script once a minute using cron
CMD ["sh", "-c", "while true; do python main.py; sleep 60; done"]
