# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy relay code
COPY relay.py .

# Expose TCP port
EXPOSE 5555

# Command to run relay
CMD ["python", "relay.py"]
