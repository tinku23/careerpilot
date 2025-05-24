# Use an official Python runtime as a parent image
# Using a base image that is lighter is generally better for deployment
# 'python:3.11-slim-bookworm' is a good choice for Python 3.11 on Debian Bookworm
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Ensure you install build essentials if any packages require compilation (e.g., PyMuPDF)
# and poppler-utils for pdfplumber if it's not pre-installed in the base image.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \ # If you ever connect to PostgreSQL (good general dev dependency)
    poppler-utils \ # Essential for pdfplumber
    # Add any other system dependencies here if needed
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port that Streamlit runs on (default is 8501)
EXPOSE 8501

# Define the command to run your Streamlit app
CMD ["streamlit", "run", "app.py"]
