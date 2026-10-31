# Power System Fault Detection and Simulation

## About the Project

This project was developed as part of my first-year B.Tech coursework for the subject **Basic Engineering**.

The project focuses on identifying and simulating different types of electrical faults in a three-phase power system. It uses voltage and current measurements from three phases to detect possible faults through a rule-based detection approach.

A Flask-based web interface allows users to enter electrical measurements, identify the detected fault, and visualize the corresponding voltage and current waveforms.

## Features

* Detection of different electrical faults using voltage and current measurements.
* Three-phase fault identification.
* Single line-to-ground fault detection.
* Double line-to-ground fault detection.
* Line-to-line fault detection.
* Open-circuit fault detection.
* Identification of normal operating conditions.
* Calculation of voltage drops and current changes.
* Visualization of voltage and current waveforms.
* Web-based interface for entering measurements and viewing results.

## Technologies Used

* Python
* Flask
* NumPy
* Matplotlib
* HTML
* CSS

## Project Structure

```text
Power-System-Fault-Detection/
│
├── app.py
├── config.py
├── detection.py
├── main.py
├── simulation.py
├── utils.py
├── visualization.py
├── requirements.txt
│
├── static/
│   └── Waveform Images
│
└── templates/
    ├── index.html
    └── result.html
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/rajvard1507/Fault-Detection-System.git
```

### 2. Navigate to the Project Directory

```bash
cd Fault-Detection-System
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Open the following address in your browser:

```text
http://127.0.0.1:5000/
```

## How It Works

1. Enter the initial and final voltage readings for all three phases.
2. Enter the initial and final current readings for all three phases.
3. Provide the neutral current reading.
4. Submit the measurements for fault detection.
5. The application analyzes the changes in voltage and current using predefined threshold-based rules.
6. The detected fault type and corresponding waveform visualization are displayed.

## Project Objective

The primary objective of this project is to understand the behaviour of three-phase electrical systems under normal and faulty operating conditions. It demonstrates how changes in electrical parameters can be used to identify different fault conditions and how these conditions can be represented visually.

## Academic Context

Developed as a first-year B.Tech project for the subject **Basic Engineering**.
