# Stage 1: Build stage
# Use a Python image to build the application
FROM python:3.9-alpine AS build

# Install necessary build tools and dependencies
RUN apk update && apk add --no-cache \
    build-base \
    gcc \
    libpq-dev

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade "openpyxl>=3.0.10,<3.1"
RUN pip install --upgrade "xlsxwriter>=3.0.0"


# Copy the rest of the application code into the container
COPY . .

# Stage 2: Production stage
# Use a lightweight Python image for the final stage
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only the necessary parts from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/src/app /usr/src/app


# Expose port 8000 for the application
EXPOSE 8000

# Define the command to run the application
CMD ["sh", "run.sh"]

