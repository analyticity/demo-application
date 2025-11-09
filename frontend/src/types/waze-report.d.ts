type WazeReport = {
  country: string;
  city: string;
  reportRating: number;
  reportByMunicipalityUser: string;
  confidence: number;
  reliability: number;
  type: string;
  uuid: string;
  roadType?: number;
  roadTypeName: string;
  magvar: number;
  subtype?: string;
  street?: string;
  reportDescription?: string;
  published_at: string;
  finished: boolean;
  intersecting_street_indexes: number[];
  // coordinates of the report
  x: number;
  y: number;
  is_primary: boolean;
  event_id: number;
  related_reports: string[];
  distance_to_primary: number;
};

type MatchedWazeReport = WazeReport & {
  matching_police_id: string;
  match_distance: number;
  match_time_diff: number;
  match_score: number;
};
