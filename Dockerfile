# Use a smaller base image
FROM ubuntu:22.04
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Istanbul
ENV LC_ALL=tr_TR.UTF-8
ENV LANG=tr_TR.UTF-8

# Set the working directory in the container
WORKDIR /app

# Install dependencies and Chrome in one layer to keep image size smaller
RUN apt-get update && apt-get install -y \
     wget \
     gnupg \
     unzip \
     curl \
     libasound2 \
     libatk-bridge2.0-0 \
     libatk1.0-0 \
     libatspi2.0-0 \
     libcups2 \
     libdbus-1-3 \
     libdrm2 \
     libgbm1 \
     libgtk-3-0 \
     libnspr4 \
     libnss3 \
     libu2f-udev \
     libvulkan1 \
     libwayland-client0 \
     libxcomposite1 \
     libxdamage1 \
     libxfixes3 \
     libxkbcommon0 \
     libxrandr2 \
     locales \
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

#================
# Install Python
#================
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-setuptools python3-dev python3-tk
RUN alias python=python3
RUN echo "alias python=python3" >> ~/.bashrc
RUN apt-get -qy --no-install-recommends install python3.10
RUN rm /usr/bin/python3
RUN ln -s python3.10 /usr/bin/python3

#==========================
# Install useful utilities
#==========================
RUN apt-get update
RUN apt-get install -y xdg-utils


# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Command to run FastAPI and Streamlit
CMD ["sh", "-c", "uvicorn menu_crawler:app --host 0.0.0.0 --port 8000 & streamlit run Hotel_Analyst.py"]
