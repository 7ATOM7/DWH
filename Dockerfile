# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container to /app

#Update and install necessary packages
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /DWH

# Create the required directories
RUN mkdir ETL Scripts Logs Meta Data

# Copy the requirements.txt file into the Meta folder of the container
COPY requirements.txt /DWH/Meta/

# Install any dependencies
RUN pip install --no-cache-dir -r /DWH/Meta/requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY start.sh /DWH/

# Add the crontab file
#COPY crontab /etc/cron.d/python-job

# Give execution rights on the cron job
#RUN chmod 0644 /etc/cron.d/python-job

# Chrn Job settings.
#RUN echo "0 0 * * * mkdir -p /app/Logs/$(date +\%Y-\%m-\%d)" >> /etc/cron.d/python-job
#RUN echo "0 0 * * * touch /app/Logs/$(date +\%Y-\%m-\%d)/cron.log" >> /etc/cron.d/python-job


#CMD cron && tail -f /app/Logs/$(date +\%Y-\%m-\%d)/cron.log
ENTRYPOINT ["/bin/bash", "/DWH/start.sh"]