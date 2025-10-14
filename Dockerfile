# Use a small Python image
FROM python:3.13-slim

# Don’t write .pyc, keep output unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir inside the container
WORKDIR /app

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Initialize the DB on container start if missing, then run the app
EXPOSE 5000
CMD [ "bash", "-lc", "python init_db.py && python app.py" ]
