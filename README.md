# Real Estate Dashboard - Python Project

## Description
This project was developed as part of the Python course at **ESIEE Paris**. The objective was to create an interactive dashboard using public open data to address a topic of public interest. Our chosen topic focuses on **real estate transactions in France**, leveraging the [Demandes de valeurs foncières géolocalisées (DVF)](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/) dataset provided by the French government. 

### Features
- **Heatmap**: Visualize price trends per square meter across French regions, departments, and communes.
- **Dynamic Line Chart**: Analyze price movements over time.
- **Histogram**: Display the distribution of property prices.
- **Pie Chart**: Show the proportion of different property types.

## Setup Instructions

### Step 1: Create the Virtual Environment
Use Conda to create a new virtual environment with Python 3.10:

```bash
conda create -n venv python=3.10
```

### Step 2: Activate the Environment
Activate the newly created environment:

```bash
conda activate venv
```

### Step 3: Install Dependencies
With the environment activated, install the project's dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Step 4: Download Data
Download necessary data from endpoints.

```bash
python get_data.py
```

### Step 5: Preprocess Data
Clean up data and save it inside data folder.

```bash
python preprocess_data.py
```

## Usage
To launch the dashboard, run the following command:

```bash
python .\src\app.py
```

Access the application in your web browser at `http://127.0.0.1:8050`.

## Data
The project utilizes the [Demandes de valeurs foncières géolocalisées (DVF)](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/) dataset, which includes:
- Property transaction details (e.g., sale price, type of property).
- Geolocated data (latitude and longitude).
- Enrichments and normalization for easier analysis.

## Developer Guide
To contribute or modify the project:
1. Ensure all dependencies are installed and your environment is set up.
2. Follow the structure provided in the `src/` directory for adding components or pages.
3. Use `config.py` for project-specific settings.
4. Document all changes thoroughly.