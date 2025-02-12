# Base Image
FROM python:3.11-slim

# Install dependencies for building SQLite
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install SQLite >= 3.35.0
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3420000.tar.gz \
    && tar -xzf sqlite-autoconf-3420000.tar.gz \
    && cd sqlite-autoconf-3420000 \
    && ./configure --prefix=/usr/local \
    && make && make install \
    && cd .. \
    && rm -rf sqlite-autoconf-3420000*

# Create a virtual environment
RUN python -m venv /antenv
ENV PATH="/antenv/bin:$PATH"

# Copy application code
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN crewai install

# Expose the port
EXPOSE 8000

# Set the working directory
WORKDIR /app/src/latest_ai_development

# Start the Panel server
CMD ["panel", "serve", "main.py", "--port", "8000", "--allow-websocket-origin=*", "--address=0.0.0.0"]
