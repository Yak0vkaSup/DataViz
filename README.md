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

## Usage
To launch the dashboard, run the following command:

```bash
python main.py
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

## Analysis Report
1. Context

The dashboard provides an interactive visualization of real estate data in France, categorized by region, department, and communes, highlighting key metrics such as average price per square meter and geographic distributions. This report analyzes the main sections of the dashboard based on the visualizations provided.

2. Section Analysis (Example with the Île-de-France Region Selected)

- Interactive Choropleth Map 
  - The map highlights a notable variation in prices within the region. 
  - Central areas (like Paris) display significantly higher prices (data in red), while peripheral areas are less expensive (data in yellow or light orange).
- Pie Chart of Property Types
  - Displays the distribution of real estate types (apartments, houses, dependencies, etc.) in the Île-de-France region.
  - Apartments represent a significant share of transactions (34.4%), followed by houses (31.3%). Commercial and industrial properties occupy a smaller share (6.3%).
- Average Price Evolution Over Time
  - Analyzes the evolution of average prices per square meter over time and identifies trends using a moving average.
  - Prices show significant short-term variations, with notable spikes on certain dates. The 14-day moving average smooths fluctuations and reveals general trends. Overall, prices appear stable in recent periods, despite occasional anomalies.
- Price Distribution per Square Meter
  - Visualizes the distribution of prices per square meter in the Île-de-France region.
  - The distribution is asymmetric, with a mode around €3,000/m². A long tail to the right indicates high-end real estate with elevated prices. The majority of properties fall within an accessible price range (below €7,000/m²).

3. Synthèse

The choropleth map highlights significant disparities between Paris and its periphery, with much higher prices in central areas.
The Île-de-France region remains marked by strong segmentation in the real estate market.
LShort-term price variations call for deeper exploration of explanatory factors.
Most properties are in accessible price ranges, but a portion of the market is dominated by high-end properties.



## Copyright
We solemnly declare that the code provided was produced by us.