# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application's code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# --- FIX: Bind to IPv6 (::) as per your research ---
# Define the command to run the application
CMD ["uvicorn", "main:app", "--host", "::", "--port", "8000"]