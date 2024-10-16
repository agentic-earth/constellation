# Use the official Python image as the base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY utils.py .

COPY config.json .

# Expose port (default FastAPI port)
EXPOSE 8000

# Define the entry point
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
