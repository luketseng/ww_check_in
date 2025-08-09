FROM docker.io/seleniumbase/seleniumbase:latest

# Switch to root user (rootless build compatible)
USER root

# Rely on seleniumbase image's bundled Chrome/Chromedriver. No manual driver pinning.

# App directory
WORKDIR /app

# Install Python dependencies only (code will be bind-mounted at runtime)
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Optional: create logs dir (also bind-mounted at runtime)
RUN mkdir -p /app/logs

# Set default timezone via env (no dpkg-reconfigure to keep rootless-safe)
ENV TZ=Asia/Taipei

# Run headless in containers by default (can be overridden via env-file)
ENV HEADLESS=true

# Default command expects project mounted at /app
# CMD ["python3", "ww_check_in.py"]