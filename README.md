# European Inflation, Consumer Prices & Household Income Analysis (2000–2024)

Repository for an end-to-end machine learning project on European inflation, consumer prices and household income for 36 European countries and aggregates (2000Q1–2024Q4).

Main goals:
- Build a clean quarterly panel from Eurostat data (HICP, income distribution, employment).
- Perform EDA and feature engineering.
- Train classification, regression and clustering models using scikit-learn.
- Prepare forecasts for 2025 to be evaluated and extended in the master’s project.

Notebooks structure:

1. `01_merge_raw_to_long.ipynb`  
   - Load raw Eurostat TSV files.
   - Convert to tidy long format.
   - Align all datasets to quarterly frequency (2000Q1–2024Q4).
   - Save quarterly tables to `data_interim/`.

2. `02_build_quarterly_panel.ipynb`  
   - Load quarterly tables from `data_interim/`.
   - Reindex to a complete geo × timeQuarter grid (including missing years like 2002 in income as explicit NaNs).
   - Merge HICP, income, and employment into a single **master quarterly panel**.
   - Save panel to `data_processed/master_quarterly_panel.parquet`.

3. `03_eda_quarterly_panel.ipynb`  
   - Exploratory data analysis on the master panel.
   - Visualisation, descriptive statistics, missingness patterns.

4. `04_models_forecasting.ipynb`  
   - Feature engineering for ML.
   - Modelling and forecasting tasks.
   - Backtests and comparison with realised 2025 data (when available).


