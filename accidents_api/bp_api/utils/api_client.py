from typing import Type, TypeVar, Generic, Dict, Any, Optional, Union
from pydantic import BaseModel, ValidationError
import requests

# Define a type variable T to represent the schema type
T = TypeVar("T", bound=BaseModel)


class APIClient(Generic[T]):
    def __init__(self, url: str, schema: Type[T]):
        """
        Initializes the APIClient with the API URL and the expected schema for validation.

        :param url: API endpoint URL
        :param schema: Pydantic model class to validate the response
        """
        self.url = url
        self.schema = schema

    def get_data(self, params: Optional[Dict[str, Any]] = None) -> Union[T, None]:
        """
        Fetches data from the API, validates the response using the Pydantic model.

        :param params: Optional query parameters for the API request.
        :return: An instance of the schema or None if an error occurs.
        """

        default_params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "json",
            # "resultRecordCount": 1,
            "outSR": 4326,
            # "resultOffset": 0,
        }

        offset = params.get("resultOffset", 0)

        # merge default params with the provided config
        params = {**default_params, **(params or {})}

        response_data = []

        try:
            while True:
                params["resultOffset"] = offset
                response = requests.get(self.url, params=params)
                response.raise_for_status()

                data = response.json()

                # Validate response against the provided schema
                validated_data = self.schema(**data)
                response_data.append(validated_data)
                if not validated_data.exceededTransferLimit:
                    break
                offset += len(validated_data.features)

            resp_struct = response_data[0]
            for resp in response_data[1:]:
                resp_struct.features = resp_struct.features + resp.features

            return resp_struct

        except requests.exceptions.RequestException as req_error:
            print(f"Request failed: {req_error}")
        except ValidationError as val_error:
            print(f"Validation error: {val_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return None
