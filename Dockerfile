# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first (to leverage Docker layer caching)
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY app/ .

# Ensure the container can read the .env file
COPY .env /app/.env

# Expose the Flask application port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=server.py  
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the Flask application
CMD ["python", "server.py"]
