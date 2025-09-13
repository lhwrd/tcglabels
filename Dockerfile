FROM python:3.13

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Reflex app
COPY . .

# Build Reflex app for production
RUN reflex export

# Expose port
EXPOSE 3000

# Run the Reflex app
CMD ["reflex", "run", "--env", "prod"]
