# Use an official Python runtime as a base image
FROM --platform=linux/amd64 python:3.9.18

# Copy all the files from the current directory into the container
COPY app/ app/
COPY dedicated-server.json dedicated-server.json
COPY entrypoint.sh entrypoint.sh
COPY start.py start.py
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app runs on
EXPOSE 5000

# Command to run the application when the container starts
CMD ["/bin/bash", "entrypoint.sh"]