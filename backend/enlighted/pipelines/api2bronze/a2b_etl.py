import logging
from collections.abc import Generator
from typing import Any, Dict, Optional, Union

import requests
from enlighted.oauth2.oauth2 import ClientCredentialsGrant
from enlighted.utils import now_hrf
from requests import Response
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    ReadTimeout,
    RequestException,
    Timeout,
)
from sqlalchemy.orm import Session

# Disable warnings for insecure requests (no https)
requests.packages.urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

REQUEST_TIMEOUT = (5, 10)


class BaseApi2BronzeETL:
    def __init__(
        self,
        session: Session,
        etl_run_start_time: int,
        is_stream: bool,
        access_token: str | None = None,
        client_credentials_grant: ClientCredentialsGrant | None = None,
        verify_ssl: bool = False,
    ) -> None:
        self.session = session

        self.etl_run_start_time = etl_run_start_time
        self.is_stream = is_stream
        self.verify_ssl = verify_ssl

        self.access_token = access_token
        self.client_credentials_grant = client_credentials_grant

    def get_token(self) -> Optional[str]:

        if self.access_token:
            return self.access_token

        if self.client_credentials_grant:
            return self.client_credentials_grant.get_valid_token()

        # If no access token nor a client credentials grant is provided, auth fails
        raise RuntimeError("Provide an access token or ClientCredentialsGrant object.")

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
                timeout=(REQUEST_TIMEOUT if not self.is_stream else None),
            )
            response.raise_for_status()
        except HTTPError:
            logger.error(f"API call failed with message: {response.content.decode()}")
            return None
        except ConnectionError as e:
            logger.error(f"API call failed with message: {str(e)}")
            return None
        except Timeout:
            logger.error("API call timed out.")
            return None
        except RequestException as e:
            logger.error("An error occurred:", e)
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
        api_request_query_params: Dict[str, Any] | None = None,
    ) -> None:
        """Do job."""
        logger.info(f"Job started at {now_hrf()}.")

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
