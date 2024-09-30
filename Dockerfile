# Use the official Python image from the Docker Hub
FROM python:3.12.5-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables (if any)
ENV PYTHONUNBUFFERED=1

# Define the command to run the application
CMD ["python", "main.py"]