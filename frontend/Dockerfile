
# Stage 1: Build the Flutter Web App
FROM debian:latest AS build-env

# Install dependencies for Flutter
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Clone Flutter SDK
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter

# Set Flutter path
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Enable web support (it's enabled by default in stable, but good to be explicit/safe)
RUN flutter config --enable-web

# Run flutter doctor to download artifacts
RUN flutter doctor -v

# Set working directory
WORKDIR /app

# Copy pubspec files first for better caching
# Only copying pubspec.yaml as lock file might not exist yet in fresh checkout
COPY pubspec.yaml ./

# Get dependencies
RUN flutter pub get

# Copy the rest of the application code
COPY . .

# Build the web application
RUN flutter build web --release

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy build artifacts from previous stage
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
