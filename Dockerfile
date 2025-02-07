FROM python:3.10-alpine

# Prevent Python from writing pyc files to disc and enable stdout/stderr logging.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /filesystem_crawler

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entireapplication code
COPY . .

# Export port 8000 for the FastAPI application
EXPOSE 8000

CMD ["uvicorn", "filesystem_crawler.main:app", "--host", "0.0.0.0", "--port", "8000" ]

