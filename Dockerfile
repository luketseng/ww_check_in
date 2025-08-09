FROM seleniumbase/seleniumbase:latest

# Switch to root user to install packages
USER root

# Set timezone
RUN ln -snf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Copy and run ChromeDriver installation script
COPY init_chromedriver.sh /usr/local/bin/init_chromedriver.sh
RUN chmod +x /usr/local/bin/init_chromedriver.sh && \
    /usr/local/bin/init_chromedriver.sh

# Create app directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create log directory
RUN mkdir -p /app/logs

# Set permissions
RUN chmod +x /app/ww_check_in.py

# Default command
CMD ["python3", "ww_check_in.py"]