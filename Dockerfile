# Use a more recent version of the base image
FROM surnet/alpine-wkhtmltopdf:3.12-0.12.6-small

# Set the working directory
WORKDIR /app

# Install python and pip
RUN apk add --no-cache python3 py3-pip

# Copy requirements and install dependencies
# This is done in a separate step to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the port environment variable
ENV PORT 80
EXPOSE 80

# Set the entrypoint for the container
ENTRYPOINT ["python3", "app.py"]