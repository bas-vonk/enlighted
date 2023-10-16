import logging
from collections.abc import Iterable

import requests
from requests.exceptions import ConnectionError, HTTPError

from minimal_footprint.db import upsert
from minimal_footprint.oauth2.oauth2 import OAuth2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class ETL:
    def __init__(
        self,
        engine,
        target_table,
        api_resource_url,
        api_request_query_params,
        etl_run_start_time,
        transform_function,
        is_stream,
        access_token=None,
        refresh_token_grant=None,
        authorization_code_grant=None,
    ):
        self.engine = engine
        self.target_table = target_table

        self.api_resource_url = api_resource_url
        self.api_request_query_params = api_request_query_params

        self.etl_run_start_time = etl_run_start_time
        self.transform_function = transform_function
        self.is_stream = is_stream

        self.access_token = access_token
        self.refresh_token_grant = refresh_token_grant
        self.authorization_code_grant = authorization_code_grant

    def get_token(self):
        if self.access_token:
            return self.access_token

        access_token = OAuth2.get_valid_token(self.engine, self.refresh_token_grant)
        if not access_token:
            logger.warning("No valid access/refresh token found. Authorize again.")
            return

        return access_token

    def extract(self, access_token):
        """Call API and return the JSON content as dictionary."""

        # Construct the headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept-Encoding": "identity",
        }
        if self.is_stream:
            headers["Accept"] = "text/event-stream"

        try:
            response = requests.get(
                self.api_resource_url,
                params=self.api_request_query_params,
                headers=headers,
                stream=self.is_stream,
            )
            response.raise_for_status()
        except HTTPError:
            logger.error(f"API call failed with message: {response.content}")
            return
        except ConnectionError as e:
            logger.error(f"API call failed with message: {str(e)}")
            return

        return response

    def transform(self, response) -> Iterable:
        return self.transform_function(response, self.etl_run_start_time)

    def load(self, row: dict):
        upsert(self.target_table, self.engine, row)

    def run(self):
        # Get valid access token
        access_token = self.get_token()

        # If no access token is found do nothing
        if not access_token:
            return

        # Extract the data from the source
        response = self.extract(access_token)

        # If the API call failed, do nothing
        if response is None or not response.status_code == 200:
            return

        # Transform the data. Capture this in a try/except block that catches
        # StopIteration to enable the use of generator transform functions
        for row in self.transform(response):
            # Load the data
            self.load(row)
