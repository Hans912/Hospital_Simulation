# Hospital Simulation

This repository contains a Python script simulating the operations of a hospital using multithreading. The simulation includes various components such as doctors, nurses, different medical rooms, a receptionist, and an emergency room. The main purpose of the simulation is to showcase the flow of patients through different departments and the interaction between various hospital staff.

## Table of Contents

- [Setup](#setup)
- [Classes](#classes)
- [Simulation Overview](#simulation-overview)
- [Database Interaction](#database-interaction)
- [Graphs](#graphs)

## Setup

Before running the simulation, ensure that you have the necessary Python libraries installed. You can install them using:

```bash
pip install mysql-connector-python matplotlib
```

Make sure to set up a MySQL database with the appropriate credentials and update the connection details in the script accordingly.

## Classes

### `Hospital`
- Singleton class representing the hospital.
- Controls the opening and closing of the hospital.

### `MasterQueues`
- Manages various queues used in the hospital.

### `Doctor`, `Nurse`, `Cardiology`, `Radiology`, `Consultancy`, `Reception`, `EmergencyRoom`
- Different classes representing hospital staff and departments.

### `Patients`
- Represents patients entering the hospital, with random attributes.

## Simulation Overview

The simulation involves the following steps:

1. **Hospital Initialization**: Setting up the hospital, creating necessary database tables.
2. **Hospital Staff Initialization**: Creating doctors, nurses, and other medical staff.
3. **Patient Arrival**: Generating patients with random attributes and adding them to the reception queue.
4. **Multithreading Simulation**: Using threads to simulate the concurrent operation of different hospital components.
5. **Database Interaction**: Saving patient data to a CSV file and then transferring it to a MySQL database.

## Database Interaction

- The simulation saves patient data to CSV files (`hospital_OG.csv` and `emergency.csv`).
- The data is then loaded into MySQL tables (`og_patients` and `patients_emer`).

## Graphs

The script generates three graphs using Matplotlib:

1. **Count of Diseases of Original Hospital Patients**: Bar chart showing the distribution of diseases among original hospital patients.

2. **Count of Diseases of Emergency Patients**: Bar chart showing the distribution of diseases among emergency patients.

3. **Count of Severities of Emergency Patients**: Bar chart showing the distribution of severity levels among emergency patients.

## Running the Simulation

To run the simulation, execute the script in a Python environment:

```bash
python hospital_simulation.py
```

Ensure that you have a MySQL server running with the specified credentials and that the required Python libraries are installed.

Feel free to customize the script and adapt it to your specific use case or requirements.
