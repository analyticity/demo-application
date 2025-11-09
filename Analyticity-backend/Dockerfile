# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY ./AnalyticityBackend ./AnalyticityBackend

# Set working dir to where main.py is
WORKDIR /app/AnalyticityBackend

# Expose FastAPI port
EXPOSE 8010

# Start FastAPI
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8010"]
