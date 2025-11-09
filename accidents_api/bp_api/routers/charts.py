from fastapi import APIRouter, HTTPException, Query, Request
import pandas as pd
from bp_api.data_loader import DataLoader
from bp_api.utils.filter import get_filtered_df
from bp_api.utils.logger import logger

router = APIRouter()

import pandas as pd
import logging

logger = logging.getLogger(__name__)
data_loader = DataLoader()


@router.get("/accidents-by-attribute")
def get_accidents_chart_by_attribute(
    request: Request,
    attribute: str = Query(..., description="The attribute to group accidents by"),
):
    accidents_df = get_filtered_df(data_loader.get_accidents_dataframe(), dict(request.query_params))

    if f"attributes.{attribute}" not in accidents_df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Attribute '{attribute}' does not exist in accident data.",
        )

    grouped_data = accidents_df.groupby(f"attributes.{attribute}").size().to_dict()

    return grouped_data

@router.get("/period-summary")
def get_accidents_chart_by_attribute(
    request: Request,
):
    print(request.query_params)
    accidents_df = get_filtered_df(data_loader.get_accidents_dataframe(), dict(request.query_params))

    result_data = {
        "accident_count": len(accidents_df),  # Count number of accidents
        "fatalities_count": int(accidents_df["attributes.usmrceno_osob"].fillna(0).sum()),  # Sum fatalities
        "seriously_injured": int(accidents_df["attributes.tezce_zraneno_osob"].fillna(0).sum()),  # Sum serious injuries
        "light_injured": int(accidents_df["attributes.lehce_zraneno_osob"].fillna(0).sum()),  # Sum light injuries
    }

    return result_data


@router.get("/events-by-day")
def get_events_by_day():
    # Fetch and process police data
    police_data = data_loader.get_accidents_data()

    police_df = pd.DataFrame(police_data)
    police_df["datum"] = police_df["p2a"].dt.date
    police_event_counts = (
        police_df.groupby("datum").size().reset_index(name="police_count")
    )

    waze_data = [accident.attributes.__dict__ for accident in data_loader.get_waze_data().features]
    waze_df = pd.DataFrame(waze_data)
    waze_df["pubMillis"] = waze_df["pubMillis"].dt.date
    waze_event_counts = (
        waze_df.groupby("pubMillis").size().reset_index(name="waze_count")
    )
    waze_event_counts.rename(columns={"pubMillis": "datum"}, inplace=True)

    merged_counts = pd.merge(
        police_event_counts, waze_event_counts, on="datum", how="outer"
    ).fillna(0)

    merged_counts_dict = merged_counts.set_index("datum").to_dict(orient="index")

    return merged_counts_dict

@router.get("/accidents-by-month")
def accidents_by_month(request: Request):
    accidents_df = get_filtered_df(data_loader.get_accidents_dataframe(), dict(request.query_params))

    gdf = accidents_df.dropna(subset=["attributes.datum"])

    gdf["month"] = gdf["attributes.datum"].dt.month
    gdf["year"] = gdf["attributes.datum"].dt.year

    accidents_per_month_year = gdf.groupby(["month", "year"]).size().reset_index(name="count")

    result = {}
    for month in range(1, 13):
        month_data = accidents_per_month_year[accidents_per_month_year["month"] == month]
        if not month_data.empty:
            result[month] = {int(year): int(count) for year, count in zip(month_data["year"], month_data["count"])}
        else:
            result[month] = {}

    return result

@router.get("/heatmap-table")
def heatmap_table(request: Request):
    accidents_df = get_filtered_df(data_loader.get_accidents_dataframe(), dict(request.query_params))

    df = accidents_df.dropna(subset=["attributes.datum", "attributes.cas"])

    df["hour"] = pd.to_datetime(df["attributes.cas"], format="%H:%M").dt.hour
    df["day_of_week"] = df["attributes.datum"].dt.dayofweek

    heatmap_data = df.pivot_table(index="hour", columns="day_of_week", aggfunc="size", fill_value=0)

    heatmap_json = heatmap_data.to_dict(orient="index")

    return heatmap_json

@router.get("/filter-schema")
def get_filter_schema():
    df = data_loader.get_accidents_dataframe()
    attribute_columns = [col for col in df.columns if col.startswith('attributes.')]

    excluded_columns = ['id_nehody', 'datum', 'cas']

    attributes_json = {}

    for col in attribute_columns:
        # Skip excluded columns
        if col in excluded_columns or any(excluded in col for excluded in excluded_columns):
            continue

        # Remove the "attributes." prefix for the key
        key = col.replace('attributes.', '')

        unique_values = df[col].dropna().unique().tolist()

        attributes_json[key] = unique_values

    return attributes_json


@router.get("/timeline-chart")
def timeline_chart(request: Request):
    accidents_df = get_filtered_df(data_loader.get_accidents_dataframe(), dict(request.query_params))

    df = accidents_df.dropna(subset=["attributes.datum"])

    daily_counts = df.groupby(df["attributes.datum"].dt.date).size()

    timeline_data = [{"date": str(date), "incidents": int(count)} for date, count in daily_counts.items()]

    return timeline_data