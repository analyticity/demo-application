from typing import Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_filtered_df(
    df: pd.DataFrame, filters: dict
) -> pd.DataFrame:
    start_date = pd.to_datetime(filters.get("startDate"), errors="coerce")
    end_date = pd.to_datetime(filters.get("endDate"), errors="coerce")

    if pd.notnull(start_date):
        start_date = start_date.to_datetime64()
    if pd.notnull(end_date):
        end_date = end_date.to_datetime64()

    # Filter by date range if both dates are provided
    if pd.notnull(start_date) and pd.notnull(end_date):
        df = df[
            (df["attributes.datum"] >= start_date) &
            (df["attributes.datum"] <= end_date)
        ]

    # Process dynamic filters
    for key, value in filters.items():
        if ":" not in key:
            continue 

        attribute, operator, _ = key.split(":", 2)
        attribute = "attributes." + attribute

        if attribute not in df.columns:
            logger.warning(f"Attribute {attribute} not in DataFrame, skipping.")
            continue

        if operator == "eq":
            df = df[df[attribute] == value]
        elif operator == "neq":
            df = df[df[attribute] != value]
        else:
            logger.warning(f"Unsupported operator {operator}, skipping.")

    return df


def get_filtered_waze_df(
    df: pd.DataFrame, filters: dict
) -> pd.DataFrame:
    start_date = pd.to_datetime(filters.get("startDate"), errors="coerce")
    end_date = pd.to_datetime(filters.get("endDate"), errors="coerce")

    if pd.notnull(start_date):
        start_date = start_date.to_datetime64()
    if pd.notnull(end_date):
        end_date = end_date.to_datetime64()

    # Filter by date range if both dates are provided
    if pd.notnull(start_date) and pd.notnull(end_date):
        df = df[
            (df["pubMillis"] >= start_date) &
            (df["pubMillis"] <= end_date)
        ]
    return df
