from fastapi import APIRouter, HTTPException, Request
from bp_api.data_loader import DataLoader
from bp_api.utils.filter import get_filtered_waze_df
import pandas as pd
import numpy as np
import json

router = APIRouter()
data_loader = DataLoader()

# Helper function to make dataframe JSON serializable
def clean_for_json(df):
    """Convert a DataFrame to a JSON-serializable format by handling non-JSON values."""
    df_copy = df.copy()

    df_copy = df_copy.replace({np.nan: None, np.inf: None, -np.inf: None})

    for col in df_copy.columns:
        if df_copy[col].dtype.kind in 'iufc':  # integer, unsigned integer, float, complex
            df_copy[col] = df_copy[col].apply(lambda x: x if x is None else x.item() if hasattr(x, 'item') else x)

    return df_copy

@router.get("/")
def get_waze_accidents(request: Request):
    waze_reports = get_filtered_waze_df(data_loader.get_waze_dataframe(), dict(request.query_params))

    # Limit to 256 reports and clean for JSON
    waze_reports_limited = waze_reports #.head(256)
    waze_reports_clean = clean_for_json(waze_reports_limited)

    return waze_reports_clean.to_dict(orient='records')

router.get("/by-police-id/{police_id}")
def get_waze_reports_by_police_id(police_id: str):
    """Get all Waze reports that match a specific police accident ID."""
    # First check if the police report exists
    accidents_df = data_loader.get_accidents_dataframe()
    police_report = accidents_df[accidents_df['attributes.id_nehody'] == police_id]

    if police_report.empty:
        raise HTTPException(status_code=404, detail=f"Police report with ID {police_id} not found")

    # Get all matching Waze reports
    waze_df = data_loader.get_waze_dataframe()

    # Check if the matching_police_id column exists
    if 'matching_police_id' not in waze_df.columns:
        return {"police_id": police_id, "waze_reports": [], "count": 0}

    matching_waze = waze_df[waze_df['matching_police_id'] == police_id]

    # Clean and format the results
    matching_waze_clean = clean_for_json(matching_waze)

    return {
        "police_id": police_id,
        "waze_reports": matching_waze_clean.to_dict(orient='records'),
        "count": len(matching_waze_clean)
    }

@router.get("/{uuid}")
def get_waze_report_by_uuid(uuid: str):
    waze_reports = data_loader.get_waze_dataframe()
    report = waze_reports[waze_reports['uuid'] == uuid]
    if report.empty:
        raise HTTPException(status_code=404, detail="Waze report not found")

    report_clean = clean_for_json(report)

    police_report = None
    if 'matching_police_id' in report_clean.columns and report_clean['matching_police_id'].iloc[0] is not None:
        police_id = report_clean['matching_police_id'].iloc[0]
        accidents_df = data_loader.get_accidents_dataframe()
        matching_police = accidents_df[accidents_df['attributes.id_nehody'] == police_id]
        if not matching_police.empty:
            police_report = clean_for_json(matching_police).to_dict(orient='records')[0]

    result = report_clean.to_dict(orient='records')[0]
    if police_report:
        result['matching_police_report'] = police_report

    return result