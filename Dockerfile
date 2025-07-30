# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies for LaTeX and PDF generation
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    latexmk \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/staticfiles /app/output /app/data /app/templates /app/logs

# Copy resume data files
COPY data/ /app/data/

# Copy LaTeX templates
COPY templates/ /app/templates/

# Copy configuration files
COPY config/ /app/config/

# Set permissions
RUN chmod -R 755 /app

# Create log files with proper permissions
RUN touch /app/logs/resume_genie.log /app/logs/errors.log /app/logs/ai_operations.log /app/logs/web_requests.log \
    && chmod 666 /app/logs/*.log

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=10)"

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]