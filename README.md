# European Inflation, Employment & Income Analysis

End-to-end machine learning and data analysis project on European inflation, consumer prices, household income distribution, and employment dynamics across European countries.

The project builds clean quarterly panels from Eurostat data, performs exploratory data analysis, engineers macroeconomic features, and applies regression, classification, and clustering models to study inflation behaviour, crisis-period effects, and country/category-level differences.

## Project Scope

This project focuses on four main questions:

1. How do major crises show up in inflation and employment, and how heterogeneous are the effects across European countries?
2. How does household income distribution evolve over time, especially around crisis periods such as the Global Financial Crisis, COVID-19, and the post-2020 inflation surge?
3. Which COICOP consumer categories drove the post-2020 inflation surge across geographies?
4. Can machine learning models support inflation forecasting, high-inflation risk classification, and clustering of inflation archetypes?

## Data Sources

The project uses public Eurostat datasets:

- HICP price index  
  Monthly consumer price index, base year 2015.

- HICP inflation rate  
  Monthly percentage change, including COICOP consumer categories.

- Household disposable income  
  Annual income distribution by quantile groups.

- Employment / NACE sector data  
  Quarterly employment index by economic activity sector.

Raw data files are not stored in this repository. They should be downloaded from Eurostat and placed locally in `data_raw/`.

## Repository Structure

```text
euro-macro-inflation-income/
│
├── data_processed/          # Cleaned and processed panel datasets
├── data_raw/                # Local raw Eurostat files, not tracked by Git
├── metadata/                # Human-readable labels for geos, COICOP, NACE, quantiles
├── notebooks/               # Main analysis and modelling notebooks
├── reports/                 # Figures, outputs, reports, and presentation material
├── src/                     # Reusable helper functions and project modules
│
├── .gitignore
├── README.md
└── environment.yml
