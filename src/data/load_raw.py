from pathlib import Path

import pandas as pd

from src.config import (
    DATA_RAW_DIR,
    METADATA_DIR,
    GEO_LABELS_FILE,
    COICOP_LABELS_FILE,
)


def loadEurostatTsv(fileName: str) -> pd.DataFrame:
    """
    Load a raw Eurostat TSV file from the data_raw directory.

    Parameters
    ----------
    fileName : str
        File name inside the data_raw directory, e.g.
        'hicp_index_cp00_cp12_2000_2025_geo36.tsv'.

    Returns
    -------
    pandas.DataFrame
        Raw wide-format Eurostat table. All columns are read as strings,
        ':' is treated as missing.
    """
    filePath = DATA_RAW_DIR / fileName

    if not filePath.exists():
        raise FileNotFoundError(f"File not found in data_raw: {filePath}")

    df = pd.read_csv(
        filePath,
        sep="\t",
        dtype=str,
        na_values=":",
    )
    return df


def loadHicpIndex() -> pd.DataFrame:
    """
    Load HICP price index (2015=100) for CP00–CP12, 2000–2025, 36 geos.
    """
    return loadEurostatTsv("hicp_index_cp00_cp12_2000_2025_geo36.tsv")


def loadHicpInflation() -> pd.DataFrame:
    """
    Load HICP monthly inflation rates (% change), CP00–CP12, 2000–2025, 36 geos.
    """
    return loadEurostatTsv("hicp_inflation_cp00_cp12_2000_2025_geo36.tsv")


def loadIncomeQuantiles() -> pd.DataFrame:
    """
    Load household income distribution by quantile (SHARE, TC), 2000–2024, 36 geos.
    """
    return loadEurostatTsv("income_quantiles_eur_2000_2024_geo36.tsv")


def loadEmploymentIndex() -> pd.DataFrame:
    """
    Load employment index (hours worked, 2015=100), NACE aggregates, 2000Q1–2024Q4, 36 geos.
    """
    return loadEurostatTsv(
        "employment_index_hours_nace_total_2000Q1_2024Q4_geo36.tsv"
    )


def loadGeoLabels() -> pd.DataFrame:
    """
    Load metadata table with GEO codes and human-readable labels.
    """
    return pd.read_csv(GEO_LABELS_FILE)


def loadCoicopLabels() -> pd.DataFrame:
    """
    Load metadata table with COICOP CP00–CP12 labels.
    """
    return pd.read_csv(COICOP_LABELS_FILE, sep="\t")
