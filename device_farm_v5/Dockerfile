# Device Farm v5 - Production Dockerfile
# Optimized for Android device farm with USB devices and Appium

FROM ubuntu:22.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/android-sdk/platform-tools:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Python and pip
    python3.11 \
    python3.11-pip \
    python3.11-venv \
    python3.11-dev \
    # Android development tools
    openjdk-11-jdk \
    wget \
    unzip \
    curl \
    # USB and ADB dependencies
    usbutils \
    android-tools-adb \
    android-tools-fastboot \
    # Node.js for Appium
    nodejs \
    npm \
    # Additional utilities
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libudev-dev \
    # Display and X11 for UI automation
    xvfb \
    x11-utils \
    x11-xserver-utils \
    # Chrome dependencies
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libgconf2-dev \
    libxss1 \
    libappindicator3-1 \
    libindicator7 \
    gconf-service \
    libgconf2-4 \
    libpango1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Android SDK
RUN mkdir -p /opt/android-sdk && cd /opt/android-sdk && \
    wget -q https://dl.google.com/android/repository/platform-tools-latest-linux.zip && \
    unzip platform-tools-latest-linux.zip && \
    rm platform-tools-latest-linux.zip

# Set up Python environment
RUN python3.11 -m pip install --upgrade pip setuptools wheel

# Install Node.js dependencies globally
RUN npm install -g appium@2.1.3
RUN npm install -g appium-doctor

# Install Appium drivers
RUN appium driver install uiautomator2
RUN appium driver install xcuitest

# Create application directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r devicefarm && useradd -r -g devicefarm -s /bin/bash devicefarm

# Create required directories
RUN mkdir -p /app/data /app/logs /app/screenshots /app/config
RUN chown -R devicefarm:devicefarm /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Set proper permissions
RUN chown -R devicefarm:devicefarm /app

# Create udev rules for USB devices (Android debugging)
RUN echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"' > /etc/udev/rules.d/51-android.rules
RUN echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0666", GROUP="plugdev"' >> /etc/udev/rules.d/51-android.rules
RUN echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="22b8", MODE="0666", GROUP="plugdev"' >> /etc/udev/rules.d/51-android.rules
RUN echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0bb4", MODE="0666", GROUP="plugdev"' >> /etc/udev/rules.d/51-android.rules

# Add devicefarm user to plugdev group for USB access
RUN usermod -a -G plugdev devicefarm

# Expose ports for services
EXPOSE 5000 4723-4823 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Switch to non-root user
USER devicefarm

# Set up entrypoint
COPY docker/entrypoint.sh /app/entrypoint.sh
USER root
RUN chmod +x /app/entrypoint.sh
USER devicefarm

# Default command
CMD ["/app/entrypoint.sh"]