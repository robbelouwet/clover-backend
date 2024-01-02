# Use an official Python runtime as a base image
FROM python:3.9.18

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the files from the current directory into the container
COPY . .

# Expose the port that the Flask app runs on
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=app/start.py
ENV FLASK_RUN_HOST=0.0.0.0

# Command to run the application when the container starts
CMD ["python", "-m", "flask", "run"]