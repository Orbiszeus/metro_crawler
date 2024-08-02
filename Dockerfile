# Use a smaller base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Istanbul
ENV LC_ALL=tr_TR.UTF-8
ENV LANG=tr_TR.UTF-8

# Set the working directory in the container
WORKDIR /app

# Install dependencies, Python, and Chrome in one layer to keep image size smaller
RUN apt-get update && apt-get install -y \
     wget \
     gnupg \
     unzip \
     curl \
     ca-certificates \
     fonts-liberation \
     libappindicator3-1 \
     libasound2 \
     libatk-bridge2.0-0 \
     libatk1.0-0 \
     libcups2 \
     libdbus-1-3 \
     libgdk-pixbuf2.0-0 \
     libnspr4 \
     libnss3 \
     libx11-xcb1 \
     libxcomposite1 \
     libxdamage1 \
     libxrandr2 \
     xdg-utils \
     locales \
     python3 \
     python3-pip \
     --no-install-recommends \
     && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
     && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
     && apt-get install ./google-chrome-stable_current_amd64.deb --yes \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

# Configure locale settings for Türkiye
RUN echo "LC_ALL=tr_TR.UTF-8" >> /etc/environment \
     && echo "LANG=tr_TR.UTF-8" >> /etc/environment \
     && locale-gen tr_TR.UTF-8

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Command to run FastAPI and Streamlit
CMD ["sh", "-c", "uvicorn menu_crawler:app --host 0.0.0.0 --port 8000 & streamlit run Hotel_Analyst.py"]
