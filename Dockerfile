# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
# Gunicorn will run on this port
EXPOSE 8000

# Define environment variables.
# These should be overridden in the deployment environment (e.g., Azure App Service configuration).
ENV TENANT_ID="your_tenant_id"
ENV CLIENT_ID="your_client_id"
ENV CLIENT_SECRET="your_client_secret"
ENV SHAREPOINT_SITE_ID="your_site_id"
ENV DOC_LIBRARY_ID="your_library_id"

# Run server.py when the container launches using Gunicorn for production
# The --bind 0.0.0.0:8000 makes the app accessible from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server:app"]
