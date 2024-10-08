# Base image with Python 3.12
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application files
COPY . .

# Expose the ports used by Streamlit (8501) and FastAPI (8000)
EXPOSE 8501

# Ensure the bash script has executable permissions
RUN chmod +x ./run.sh

# Run the bash script
CMD ["./run.sh"]

