# Sensor Analytics Dashboard

A modern telemetry analysis platform built with Python and Streamlit for visualizing and analyzing vehicle sensor data collected by an ESP32. The dashboard combines GPS, IMU (MPU6050), and environmental sensor (BME280) data to provide comprehensive trip analysis, driving behavior insights, and interactive data visualization.

This project was developed as part of a high school software engineering project and combines embedded systems, data analysis, databases, and modern web technologies into a practical telemetry application.

> **Note:** This is a fully functional prototype. Some components were intentionally simplified to focus on data processing, sensor integration, and visualization concepts.

---

# Features

- Interactive GPS route visualization
- Total distance calculation
- Average, minimum, and maximum speed analysis
- GPS accuracy and satellite statistics
- Elevation analysis
- Trip duration and timestamp tracking
- Automatic detection of hard braking
- Automatic detection of strong acceleration
- Left and right turn detection
- Strong impact detection
- Road vibration analysis
- Ride comfort classification
- Interactive speed and vibration charts
- Environmental monitoring (temperature, pressure, humidity)
- Short-term and full-trip analysis
- Event timeline with timestamps
- Trip comparison and selection
- Modern responsive dashboard interface

---

# Technologies

## Backend

- Python
- SQLite
- Pandas
- Custom Data Analysis Module

## Dashboard

- Streamlit
- Plotly
- Folium
- HTML
- CSS

## Embedded System

- ESP32
- GPS (NEO-6M)
- MPU6050
- BME280

---

# Known Limitations

As this project was developed as a high school prototype, several improvements would be required before deploying it in a production environment:

- Support for multiple vehicles and users
- Live telemetry streaming
- Cloud-based database integration
- Advanced statistical analysis and reporting
- Machine learning for driving behavior classification
- Export functionality for reports and datasets
- Improved scalability and performance optimization

---

# System Architecture

The system consists of four main components.

## ESP32 Sensor Platform

Collects GPS, motion, and environmental sensor data during a trip.

## Database

Stores all recorded telemetry data using SQLite for later analysis.

## Analysis Engine

Processes the collected sensor data, calculates statistics, detects driving events, and prepares the data for visualization.

## Dashboard

Provides an interactive interface for exploring trips, viewing statistics, analyzing driving behavior, and visualizing sensor data.

---

# Installation

### Clone the repository

```bash
git clone <repository-url>
cd sensor-analytics-dashboard
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the application

```bash
python main.py
```

The application automatically starts the Flask backend and launches the Streamlit dashboard.

---

# How It Works

1. The ESP32 records GPS, IMU, and environmental sensor data during a trip.
2. All measurements are stored in a SQLite database.
3. The analysis engine processes the collected telemetry data.
4. Driving events such as hard braking, acceleration, turns, and impacts are detected automatically.
5. Statistics and visualizations are generated from the processed data.
6. The Streamlit dashboard displays interactive maps, charts, and detailed trip information.

---

# Hardware Requirements

To recreate the project, the following hardware is required:

- ESP32 Development Board
- GPS Module (NEO-6M)
- MPU6050 Accelerometer and Gyroscope
- BME280 Environmental Sensor

---

# Implemented Features

- GPS route reconstruction
- Vehicle telemetry analysis
- Driving behavior detection
- Interactive Plotly visualizations
- OpenStreetMap route visualization
- Environmental sensor monitoring
- Trip statistics and comparison
- SQLite-based telemetry storage
- Responsive dark-themed dashboard

---

# Documentation

Additional technical documentation and source code are available throughout the repository.
