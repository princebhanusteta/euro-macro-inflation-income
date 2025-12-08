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


def _validQuarterRange():
    """
    Helper to get the canonical quarterly range for the project:
    2000Q1 to 2024Q4, inclusive.
    """
    return pd.period_range("2000Q1", "2024Q4", freq="Q-DEC")


def _aggregateMonthlyToQuarterlyMean(
    dfLong: pd.DataFrame,
    valueCol: str,
    groupingDims,
    monthPeriodCol: str = "timeMonth",
    quarterCol: str = "timeQuarter",
    countCol: str = "nMonths",
) -> pd.DataFrame:
    """
    Aggregate monthly values to quarterly means.

    For each (groupingDims, quarter) we compute the mean of available
    monthly values and record how many months were used.

    Parameters
    ----------
    dfLong : DataFrame
        Long monthly table with a Period[M] column (monthPeriodCol).
    valueCol : str
        Name of the numeric column to aggregate.
    groupingDims : list-like
        Dimension columns (e.g. ['freq', 'unit', 'coicop', 'geo']).
    monthPeriodCol : str
        Column with monthly periods.
    quarterCol : str
        Name of the quarterly period column to create.
    countCol : str
        Name for the column storing number of contributing months.

    Returns
    -------
    DataFrame
        Quarterly table with mean values and a month-count column.
    """
    df = dfLong.copy()

    # Map each month to its quarter (correct dt usage)
    df[quarterCol] = (
        df[monthPeriodCol]
        .dt.to_timestamp()        # period[M] -> Timestamp
        .dt.to_period("Q-DEC")    # -> period[Q-DEC]
    )

    # Restrict to canonical project range 2000Q1–2024Q4
    valid_quarters = _validQuarterRange()
    df = df[df[quarterCol].isin(valid_quarters)]

    group_cols = list(groupingDims) + [quarterCol]

    agg = (
        df.groupby(group_cols, dropna=False)[valueCol]
          .agg(["mean", "count"])
          .reset_index()
    )

    agg = agg.rename(columns={"mean": valueCol, "count": countCol})
    return agg

def makeHicpIndexQuarterly(hicpIndexLong: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate monthly HICP index to quarterly means for 2000Q1–2024Q4.

    Output columns include:
    - freq, unit, coicop, geo
    - timeQuarter (period[Q-DEC])
    - hicpIndex (quarterly mean)
    - nMonths (number of monthly observations used: 1–3)
    """
    groupingDims = ["freq", "unit", "coicop", "geo"]
    return _aggregateMonthlyToQuarterlyMean(
        hicpIndexLong,
        valueCol="hicpIndex",
        groupingDims=groupingDims,
        monthPeriodCol="timeMonth",
        quarterCol="timeQuarter",
        countCol="nMonths",
    )


def makeHicpInflationQuarterly(hicpInflationLong: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate monthly HICP inflation to quarterly means for 2000Q1–2024Q4.
    """
    groupingDims = ["freq", "unit", "coicop", "geo"]
    return _aggregateMonthlyToQuarterlyMean(
        hicpInflationLong,
        valueCol="hicpInflation",
        groupingDims=groupingDims,
        monthPeriodCol="timeMonth",
        quarterCol="timeQuarter",
        countCol="nMonths",
    )

def expandAnnualToQuarterly(
    dfAnnual: pd.DataFrame,
    yearCol: str = "timeYear",
    quarterCol: str = "timeQuarter",
) -> pd.DataFrame:
    """
    Expand an annual table to quarterly by repeating each row for Q1–Q4.

    Parameters
    ----------
    dfAnnual : DataFrame
        Long annual table with a Period[Y] column (yearCol).
    yearCol : str
        Name of the annual period column.
    quarterCol : str
        Name of the quarterly period column to create.

    Returns
    -------
    DataFrame
        Quarterly table with each annual observation repeated four times.
    """
    df = dfAnnual.copy()

    # Build Q1 of each year explicitly, e.g. "2000" -> "2000Q1"
    year_str = df[yearCol].astype("string")
    base_quarter = pd.PeriodIndex(year_str + "Q1", freq="Q-DEC")

    frames = []
    for offset in range(4):
        tmp = df.copy()
        tmp[quarterCol] = base_quarter + offset  # Q1, Q2, Q3, Q4
        frames.append(tmp)

    df_q = pd.concat(frames, ignore_index=True)

    # Restrict to canonical quarter range
    valid_quarters = _validQuarterRange()
    df_q = df_q[df_q[quarterCol].isin(valid_quarters)]

    return df_q


def makeIncomeQuarterly(incomeLong: pd.DataFrame) -> pd.DataFrame:
    """
    Expand annual income quantiles to quarterly frequency.

    Each (freq, quantile, indic_il, currency, geo, timeYear) row becomes
    four rows, one per quarter, for 2000Q1–2024Q4.
    """
    return expandAnnualToQuarterly(
        incomeLong,
        yearCol="timeYear",
        quarterCol="timeQuarter",
    )
def makeEmploymentQuarterly(employmentLong: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure employment table is restricted to the canonical quarter range.

    The input is already quarterly; we just drop any quarters outside
    2000Q1–2024Q4 if they exist.
    """
    df = employmentLong.copy()
    valid_quarters = _validQuarterRange()
    df = df[df["timeQuarter"].isin(valid_quarters)]
    return df
