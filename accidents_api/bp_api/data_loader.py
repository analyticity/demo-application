import json
from typing import List, Dict, Any, Optional
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import Point
from geopy.distance import geodesic
from pydantic import ValidationError

from bp_api.models.models import Feature
from bp_api.models.waze_model import WazeFileAttributes
from bp_api.models.accidents_model import AccidentsAttributes
from bp_api.utils.logger import logger
from bp_api.models.data_map import column_mapping

class DataLoader:
    """
    Centralized data loading and processing class for accident and Waze reports
    Implemented as a Singleton
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initialize instance variables
        """
        self._accident_data: Optional[List[Feature[AccidentsAttributes]]] = None
        self._accident_dataframe: Optional[pd.DataFrame] = None
        self._waze_data: Optional[List[WazeFileAttributes]] = None
        self._waze_dataframe: Optional[pd.DataFrame] = None

    @staticmethod
    def _transform_accident(accident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform accident data based on column mapping
        
        Args:
            accident (Dict[str, Any]): Raw accident data
        
        Returns:
            Dict[str, Any]: Transformed accident data
        """
        return {
            column_mapping[key]["name"]: column_mapping[key]["mapping"].get(
                str(value) if "." not in str(value) else str(value).split(".")[0], 
                value
            ) 
            for key, value in accident.items() 
            if key in column_mapping
        }

    def load_accidents_file(self, file_path: str = "bp_api/data/nehody.geojson") -> List[Feature[AccidentsAttributes]]:
        """
        Load and validate accident data from GeoJSON file
        
        Args:
            file_path (str): Path to the GeoJSON file
        
        Returns:
            List[Feature[AccidentsAttributes]]: Validated accident features
        """
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Accident file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Extract coordinates and create GeoDataFrame
        coordinates = [
            feature["geometry"]["coordinates"] for feature in data.get("features", [])
        ]
        gdf = gpd.GeoDataFrame(
            geometry=[Point(x, y) for x, y in coordinates],
            crs="EPSG:5514",
        ).to_crs(epsg=4326)

        # Validate and process features
        accidents = []
        for feature, geom in zip(data.get("features", []), gdf.geometry):
            accident_data = {
                "attributes": self._transform_accident(feature.get("properties", {})),
                "geometry": {
                    "x": geom.x,
                    "y": geom.y,
                },
            }

            try:
                validated_data = Feature[AccidentsAttributes](**accident_data)
                accidents.append(validated_data)
            except ValidationError as e:
                print(feature)
                logger.error(f"Validation Error: {e}")

        # Store data
        self._accident_data = accidents
        self._accident_dataframe = pd.json_normalize([
            {"attributes": accident.attributes.__dict__, "geometry": accident.geometry.__dict__} 
            for accident in accidents
        ])

        logger.info(f"Accidents data loaded - got {len(accidents)} accidents")
        return accidents

    def load_waze(self, file_path: str = "bp_api/data/processed_alerts.json") -> List[WazeFileAttributes]:
        """
        Load and validate Waze accident reports
        
        Args:
            file_path (str): Path to the Waze reports JSON file
        
        Returns:
            List[WazeFileAttributes]: Validated Waze accident reports
        """
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Waze reports file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Filter and validate accident reports
        accidents = []
        for report in data:
            if report['type'] != "ACCIDENT":
                continue
            
            try:
                validated_data = WazeFileAttributes(**report)
                accidents.append(validated_data)
            except ValidationError as e:
                logger.error(f"Validation Error: {e}")

        # Convert to DataFrame
        df = pd.DataFrame([accident.model_dump() for accident in accidents])
        
        # Flatten location column
        if 'location' in df.columns:
            df['x'] = df['location'].apply(lambda x: x['x'])
            df['y'] = df['location'].apply(lambda x: x['y'])
            df = df.drop(columns=['location'])

        # Store data
        self._waze_data = accidents
        self._waze_dataframe = df

        logger.info(f"Waze data loaded - got {len(accidents)} accident reports")
        return accidents

    def create_matched_tables(self, max_distance_meters=500, max_time_diff_minutes=(2*60)):
        police_df = self._accident_dataframe.copy()
        waze_df = self._waze_dataframe.copy()
        
        # Convert police date to datetime format first (date only)
        police_df['datetime'] = pd.to_datetime(police_df['attributes.datum'])
        police_df = police_df[police_df['datetime'].dt.year >= 2025]
        
        def parse_time_and_combine(row):
            date_part = row['datetime']
            time_str = row['attributes.cas']
            
            if pd.isna(time_str) or time_str is None:
                return date_part.replace(hour=0, minute=0, second=0)
            
            try:
                time_parts = time_str.split(':')
                if len(time_parts) == 2:
                    hour, minute = map(int, time_parts)
                    return date_part.replace(hour=hour, minute=minute, second=0)
                else:
                    return date_part.replace(hour=0, minute=0, second=0)
            except:
                return date_part.replace(hour=0, minute=0, second=0)
        
        # Apply the time parsing function
        police_df['datetime_with_time'] = police_df.apply(parse_time_and_combine, axis=1)
        
        # Convert Waze pubMillis to datetime
        waze_df['datetime'] = pd.to_datetime(waze_df['pubMillis'], unit='ms')
        
        logger.info(f"Processing {len(police_df)} police records and {len(waze_df)} Waze reports")
        
        waze_df['matching_police_id'] = None
        waze_df['match_distance'] = None
        waze_df['match_time_diff'] = None
        waze_df['match_score'] = None
        
        # Create spatial index for efficient querying
        from scipy.spatial import KDTree
        
        # Create KDTree from Waze coordinates
        waze_coords = waze_df[['y', 'x']].values
        waze_tree = KDTree(waze_coords)
        
        match_count = 0
        
        for police_idx, police_row in police_df.iterrows():
            police_id = police_row['attributes.id_nehody']
            police_coords = np.array([[police_row['geometry.y'], police_row['geometry.x']]])
            
            # Use the datetime with time information
            police_time = police_row['datetime_with_time']
            
            # Query KDTree to find Waze reports within max_distance
            potential_matches_indices = waze_tree.query_ball_point(
                police_coords[0], 
                r=max_distance_meters/111000
            )
            
            for waze_idx in potential_matches_indices:
                waze_row_idx = waze_df.index[waze_idx]
                waze_time = waze_df.iloc[waze_idx]['datetime']
                
                time_diff = abs((waze_time - police_time).total_seconds()) / 60
                
                if abs(time_diff) <= max_time_diff_minutes:
                    waze_coords_match = (waze_df.iloc[waze_idx]['y'], waze_df.iloc[waze_idx]['x'])
                    police_coords_match = (police_row['geometry.y'], police_row['geometry.x'])
                    distance = geodesic(waze_coords_match, police_coords_match).meters
                    
                    if distance <= max_distance_meters:
                        # Adjust match score to weigh time difference more heavily when time is available
                        time_weight = 10  # Default weight
                        if not pd.isna(police_row['attributes.cas']):
                            time_weight = 30  # Higher weight when actual time is available
                        
                        match_score = 1 / (1 + distance/100 + abs(time_diff)/time_weight)
                        
                        current_score = waze_df.at[waze_row_idx, 'match_score']
                        
                        if current_score is None or match_score > current_score:
                            waze_df.at[waze_row_idx, 'matching_police_id'] = police_id
                            waze_df.at[waze_row_idx, 'match_distance'] = distance
                            waze_df.at[waze_row_idx, 'match_time_diff'] = time_diff
                            waze_df.at[waze_row_idx, 'match_score'] = match_score
                            
                            if current_score is None:
                                match_count += 1
        
        # Filter to only matched waze reports if needed
        matched_waze_df = waze_df[waze_df['matching_police_id'].notnull()]
        
        logger.info(f"Found {match_count} matches between police reports and Waze alerts")
        logger.info(f"{len(matched_waze_df)} Waze reports matched to police data")
        
        self._waze_dataframe = waze_df

        return police_df, waze_df
    
    def get_accidents_data(self) -> Optional[List[Feature[AccidentsAttributes]]]:
        """
        Get loaded accident data
        
        Returns:
            Optional[List[Feature[AccidentsAttributes]]]: Loaded accident data
        """
        return self._accident_data

    def get_accidents_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get accidents DataFrame
        
        Returns:
            Optional[pd.DataFrame]: Accidents DataFrame
        """
        return self._accident_dataframe

    def get_waze_data(self) -> Optional[List[WazeFileAttributes]]:
        """
        Get loaded Waze data
        
        Returns:
            Optional[List[WazeFileAttributes]]: Loaded Waze accident reports
        """
        return self._waze_data

    def get_waze_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get Waze DataFrame
        
        Returns:
            Optional[pd.DataFrame]: Waze reports DataFrame
        """
        return self._waze_dataframe