# =========================
# Stage 1: Build Flutter Web
# =========================
FROM debian:bookworm-slim AS build-env

ENV DEBIAN_FRONTEND=noninteractive
ENV TAR_OPTIONS="--no-same-owner"

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash flutter && \
    mkdir -p /usr/local/flutter && \
    chown -R flutter:flutter /usr/local/flutter

# Switch to non-root user
USER flutter

# Install Flutter
ARG FLUTTER_VERSION=3.38.5
RUN git clone https://github.com/flutter/flutter.git \
    --branch ${FLUTTER_VERSION} \
    --depth 1 \
    /usr/local/flutter

# Set PATH
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Pre-download Flutter web SDK
RUN flutter precache --web

WORKDIR /app

# Copy pubspec files
COPY --chown=flutter:flutter pubspec.yaml pubspec.lock* ./

# Get dependencies
RUN flutter pub get

# Copy rest of the app
COPY --chown=flutter:flutter . .

# Enable web platform and build
ARG API_URL
RUN flutter create . --platforms web && \
    flutter build web --release --dart-define=API_URL=${API_URL}

# =========================
# Stage 2: Nginx
# =========================
FROM nginx:alpine

# Copy built web files
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Copy nginx config (create one if you don't have it)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]