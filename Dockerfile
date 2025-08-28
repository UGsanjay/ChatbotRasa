FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    default-mysql-client \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Train model if not exists
RUN if [ ! -d "models" ] || [ -z "$(ls -A models)" ]; then rasa train --fixed-model-name model; fi

# Expose port
EXPOSE $PORT

# Start Rasa server
CMD rasa run --enable-api --cors "*" --port $PORT --host 0.0.0.0
