FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default environment variables
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT api_server:app 