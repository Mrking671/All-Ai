# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8443 available to the world outside this container
EXPOSE 8443

# Define environment variable for the Telegram bot token (use Render's environment settings to set this)
ENV TELEGRAM_TOKEN=<your-token-here>

# Run bot.py when the container launches
CMD ["python", "bot.py"]
