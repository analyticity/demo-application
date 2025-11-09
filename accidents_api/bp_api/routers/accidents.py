from fastapi import APIRouter, Request
from bp_api.data_loader import DataLoader
import pandas as pd

from bp_api.utils.filter import get_filtered_df

router = APIRouter()
data_loader = DataLoader()

@router.get("/")
def get_police_accidents(request: Request):
    params = dict(request.query_params)
    accidents_df = get_filtered_df(data_loader.get_accidents_dataframe(), params)

    limit = 512 
    if "limit" in params:
        try:
            limit = int(params.pop("limit"))
        except ValueError:
            pass

    sorted_df = accidents_df.sort_values(by="attributes.datum", ascending=False).head(limit)
    waze_df = data_loader.get_waze_dataframe()

    result_data = []
    
    for _, row in sorted_df.iterrows():
        attributes = row.filter(like="attributes.").to_dict()
        geometry = {"x": row["geometry.x"], "y": row["geometry.y"]}

        attributes = {key.replace("attributes.", ""): value for key, value in attributes.items()}

        if "datum" in attributes and pd.notnull(attributes["datum"]):
            attributes["datum"] = attributes["datum"].isoformat()

        waze_matches = waze_df[waze_df['matching_police_id'] == attributes['id_nehody']]
        waze_matches_count = len(waze_matches)
        attributes["waze_matches_count"] = waze_matches_count

        attributes["matched_waze"] = waze_matches['uuid'].to_list()

        result_data.append({
            "attributes": attributes,
            "geometry": geometry,
        })

    return result_data
