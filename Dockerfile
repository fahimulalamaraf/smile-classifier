FROM python:3.10-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# Includes graphical libraries needed for OpenCV (libGL and libglib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    software-properties-common \
    gcc \
    libatlas-base-dev \
    libffi-dev \
    libglib2.0-0 \
    libhdf5-dev \
    libmariadb-dev \
    mariadb-client \
    wget \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add wait-for-it.sh script to the image
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Copy requirements.txt to the container
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port and define the default command
EXPOSE 8000
CMD ["python", "app.py"]