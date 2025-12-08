from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Core directories
DATA_RAW_DIR = PROJECT_ROOT / "data_raw"
DATA_INTERIM_DIR = PROJECT_ROOT / "data_interim"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data_processed"
METADATA_DIR = PROJECT_ROOT / "metadata"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Metadata file paths 
GEO_LABELS_FILE = METADATA_DIR / "geo_labels_36.csv"
COICOP_LABELS_FILE = METADATA_DIR / "coicop_cp00_cp12_labels.tsv"
NACE_LABELS_FILE   = METADATA_DIR / "nace_r2_agg_labels.csv"

# Fixed list of 36 geos used in the project
# Codes are consistent with geo_labels_36.csv
GEO_LIST_36 = [
    "AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK",
    "EA", "EA19", "EA20", "EE", "EL", "ES", "EU27_2020",
    "FI", "FR", "HR", "HU", "IE", "IS", "IT", "LT",
    "LU", "LV", "MT", "NL", "NO", "PL", "PT", "RO",
    "RS", "SE", "SI", "SK", "UK",
]
