from typing import List

import pandas as pd


def _stripColumnWhitespace(dfWide: pd.DataFrame) -> pd.DataFrame:
    """
    Return a copy of dfWide with leading/trailing spaces stripped
    from all column names.
    """
    df = dfWide.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


def _parseNumericValues(values: pd.Series) -> pd.Series:
    """
    Keep only the numeric part of a value and drop Eurostat flags.

    Examples
    --------
    '3.5'   -> 3.5
    '3.5 b' -> 3.5
    '3.5p'  -> 3.5
    ':'     -> NaN
    """
    s = values.astype("string").str.strip()

    # ':' means no data
    s = s.replace(":", pd.NA)

    # Extract first numeric token (optional sign + digits + optional decimal)
    numeric_str = s.str.extract(r"([-+]?\d*\.?\d+)", expand=False)

    return pd.to_numeric(numeric_str, errors="coerce")


def splitKeyAndMeltToLong(
    dfWide: pd.DataFrame,
    valueName: str,
    timeColName: str = "timeStr",
) -> pd.DataFrame:
    """
    Split the first Eurostat key column into separate dimensions and
    melt wide time columns into a long format.

    Works for:
    - HICP:      freq,unit,coicop,geo\\TIME_PERIOD
    - Income:    freq,quantile,indic_il,currency,geo\\TIME_PERIOD
    - Employment:freq,unit,nace_r2,s_adj,na_item,geo\\TIME_PERIOD
    """
    dfWide = _stripColumnWhitespace(dfWide)

    # First column has the composite key
    keyColName = dfWide.columns[0]

    # Split "freq,unit,coicop,geo\\TIME_PERIOD" into dimension names
    dimPart, _ = keyColName.split("\\")
    dimNames: List[str] = dimPart.split(",")

    # Rename key column to something simple
    df = dfWide.rename(columns={keyColName: "key"}).copy()

    # Split key values (e.g. "M,I15,CP00,AT") into separate columns
    dimDf = df["key"].str.split(",", expand=True)
    dimDf.columns = dimNames

    # All remaining columns are time columns
    valueCols = [c for c in df.columns if c != "key"]

    # Attach dimension columns and melt
    dfCombined = pd.concat([dimDf, df[valueCols]], axis=1)

    dfLong = dfCombined.melt(
        id_vars=dimNames,
        var_name=timeColName,
        value_name=valueName,
    )

    # Clean time labels
    dfLong[timeColName] = dfLong[timeColName].astype(str).str.strip()

    # Keep only numeric part of the values (Option A)
    dfLong[valueName] = _parseNumericValues(dfLong[valueName])

    return dfLong


def addMonthlyPeriodColumn(
    dfLong: pd.DataFrame,
    timeColName: str = "timeStr",
    periodColName: str = "timeMonth",
) -> pd.DataFrame:
    """
    Convert 'YYYY-MM' strings into a pandas PeriodIndex with monthly frequency.
    """
    dfLong = dfLong.copy()
    dfLong[periodColName] = pd.PeriodIndex(dfLong[timeColName], freq="M")
    return dfLong


def addAnnualPeriodColumn(
    dfLong: pd.DataFrame,
    timeColName: str = "timeStr",
    periodColName: str = "timeYear",
) -> pd.DataFrame:
    """
    Convert 'YYYY' strings into a pandas PeriodIndex with annual frequency.
    """
    dfLong = dfLong.copy()
    dfLong[periodColName] = pd.PeriodIndex(dfLong[timeColName], freq="Y-DEC")
    return dfLong


def addQuarterlyPeriodColumn(
    dfLong: pd.DataFrame,
    timeColName: str = "timeStr",
    periodColName: str = "timeQuarter",
) -> pd.DataFrame:
    """
    Convert 'YYYY-Qx' strings into a pandas PeriodIndex with quarterly frequency.
    """
    dfLong = dfLong.copy()
    dfLong[timeColName] = dfLong[timeColName].astype(str).str.strip()
    dfLong[periodColName] = pd.PeriodIndex(dfLong[timeColName], freq="Q-DEC")
    return dfLong


# ---------- Dataset-specific wrappers ----------

def makeHicpIndexLong(rawHicpIndex: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw HICP index table to long monthly format.
    """
    dfLong = splitKeyAndMeltToLong(rawHicpIndex, valueName="hicpIndex")
    dfLong = addMonthlyPeriodColumn(dfLong)
    return dfLong


def makeHicpInflationLong(rawHicpInflation: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw HICP inflation table to long monthly format.
    """
    dfLong = splitKeyAndMeltToLong(rawHicpInflation, valueName="hicpInflation")
    dfLong = addMonthlyPeriodColumn(dfLong)
    return dfLong


def makeIncomeQuantilesLong(rawIncome: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw income quantiles table to long annual format.
    """
    dfLong = splitKeyAndMeltToLong(rawIncome, valueName="incomeValue")
    dfLong = addAnnualPeriodColumn(dfLong)
    return dfLong


def makeEmploymentIndexLong(rawEmployment: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw employment index table to long quarterly format.
    """
    dfLong = splitKeyAndMeltToLong(rawEmployment, valueName="employmentIndex")
    dfLong = addQuarterlyPeriodColumn(dfLong)
    return dfLong
