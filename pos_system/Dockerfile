# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Expose the port Django will run on
EXPOSE 8000

# Run Django migrations and collect static files (as part of the entrypoint for Cloud Run)
# This is a common pattern for Cloud Run, but for larger projects, migrations might be run as a separate job.
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "pos_system.wsgi:application"]
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 pos_system.wsgi:application"]