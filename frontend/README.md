# MedStory Frontend

This is the frontend for the MedStory application, built with **Flutter**.

## Prerequisites

- Flutter SDK (Latest Stable)
- Dart SDK

## Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Get dependencies:
   ```bash
   flutter pub get
   ```

## Configuration

By default, the application connects to the backend at `http://localhost:8000`. 
If you need to change this, update `lib/main.dart` or look for build-time configuration options (if implemented).

## Running the App

### Web (Recommended for Development)

```bash
flutter run -d chrome
```

### Mobile

```bash
flutter run
```

## Testing

Run unit and widget tests:

```bash
flutter test
```
