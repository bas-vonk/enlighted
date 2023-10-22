import logging
from collections.abc import Generator
from typing import Any, Dict, Optional, Union

import requests
from requests import Response
from requests.exceptions import ConnectionError, HTTPError
from sqlalchemy.engine import Engine

from minimal_footprint.oauth2.oauth2 import (
    AuthorizationCodeGrant,
    RefreshTokenGrant,
    get_valid_token,
)

# Disable warnings for insecure requests (no https)
requests.packages.urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class BaseETL:
    def __init__(
        self,
        engine: Engine,
        etl_run_start_time: int,
        is_stream: bool,
        access_token: str | None = None,
        refresh_token_grant: RefreshTokenGrant | None = None,
        authorization_code_grant: AuthorizationCodeGrant | None = None,
        verify_ssl: bool = False,
    ) -> None:
        self.engine = engine

        self.etl_run_start_time = etl_run_start_time
        self.is_stream = is_stream
        self.verify_ssl = verify_ssl

        self.access_token = access_token
        self.refresh_token_grant = refresh_token_grant
        self.authorization_code_grant = authorization_code_grant

    def get_token(self) -> Optional[str]:
        if self.access_token:
            return self.access_token

        # Check whether a AuthorizationCodeGrant object is set
        if self.authorization_code_grant is not None:
            authorization_code_grant: AuthorizationCodeGrant = (
                self.authorization_code_grant
            )
        else:
            raise RuntimeError("Provide a AuthorizationCodeGrant object.")

        # Check whether a RefreshTokenGrant object is set
        if self.refresh_token_grant is not None:
            refresh_token_grant: RefreshTokenGrant = self.refresh_token_grant
        else:
            raise RuntimeError("Provide a RefreshTokenGrant object.")

        access_token = get_valid_token(
            self.engine, refresh_token_grant, authorization_code_grant
        )
        if not access_token:
            return None

        return access_token

    def extract(
        self,
        api_request_resource_url: str,
        api_request_query_params: Dict[str, Any] | None,
        access_token: str,
    ) -> Optional[Response]:
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
                url=api_request_resource_url,
                params=api_request_query_params,
                headers=headers,
                stream=self.is_stream,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
        except HTTPError:
            logger.error(f"API call failed with message: {response.content.decode()}")
            return None
        except ConnectionError as e:
            logger.error(f"API call failed with message: {str(e)}")
            return None

        return response

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        raise NotImplementedError

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        raise NotImplementedError

    def do_job(
        self,
        api_request_resource_url: str,
        api_request_query_params: Dict[str, Any] | None,
    ) -> None:
        # Get valid access token
        access_token = self.get_token()

        # If no access token is found do nothing
        if not access_token:
            return None

        # Extract the data from the source
        response = self.extract(
            api_request_resource_url, api_request_query_params, access_token
        )

        # If the API call failed, do nothing
        if response is None or not response.status_code == 200:
            return None

        # Transform the data. Capture this in a try/except block that catches
        # StopIteration to enable the use of generator transform functions
        for row in self.transform(response):
            # Load the data
            self.load(row)
