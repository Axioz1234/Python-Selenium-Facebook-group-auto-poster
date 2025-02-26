# Use the official Apify Python base image.
FROM apify/actor-python:3.9

# Install Chromium and its driver.
RUN apt-get update && apt-get install -y chromium chromium-driver

# Copy the requirements file and install Python dependencies.
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# Copy all actor files.
COPY . /usr/src/app
WORKDIR /usr/src/app

# Run the Python script.
CMD ["python", "main.py"]
