# Use an official Python runtime as a parent image
FROM python:3.12-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Load environment variables from .env file (if it exists)
# This uses a simple shell command to export variables.
# For production, consider using Docker secrets or passing environment variables directly.
RUN if [ -f .env ]; then set -a && . ./.env && set +a; fi

# Expose the port the app runs on (if applicable)
# EXPOSE 8000

# Define environment variables (optional, can be used for things not in .env)
# ENV NAME World

# Run the application
CMD ["python", "your_app_name.py"]