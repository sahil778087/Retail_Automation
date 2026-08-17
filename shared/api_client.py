import time
import requests

from .config import (
    API_TIMEOUT,
    MAX_RETRIES
)

from .logger import get_logger


logger = get_logger()


def post(url, payload, headers):
    """
    Generic POST request helper.

    Handles:
    - Request timeout
    - Temporary network failures
    - Temporary server errors
    - Retry attempts
    """

    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            logger.info(
                f"API POST | Attempt {attempt}/{MAX_RETRIES} | "
                f"URL={url}"
            )

            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=API_TIMEOUT
            )

            response.raise_for_status()

            logger.info(
                f"API POST Successful | "
                f"Attempt={attempt} | "
                f"Status={response.status_code}"
            )

            return response.json()

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError
        ) as exc:

            last_exception = exc

            logger.warning(
                f"API POST Temporary Failure | "
                f"Attempt={attempt}/{MAX_RETRIES} | "
                f"Error={exc}"
            )

            if attempt == MAX_RETRIES:
                break

            retry_delay = 2 ** (attempt - 1)

            logger.info(
                f"API POST Retrying | "
                f"Next Attempt={attempt + 1}/{MAX_RETRIES} | "
                f"Delay={retry_delay}s"
            )

            time.sleep(retry_delay)

        except requests.exceptions.HTTPError as exc:

            logger.error(
                f"API POST HTTP Error | "
                f"Status={response.status_code} | "
                f"Error={exc}"
            )

            # HTTP errors are not automatically retried.
            raise

        except ValueError as exc:

            logger.error(
                f"API POST Invalid JSON Response | "
                f"Error={exc}"
            )

            raise

    logger.error(
        f"API POST Failed After {MAX_RETRIES} Attempts"
    )

    raise RuntimeError(
        f"API request failed after "
        f"{MAX_RETRIES} attempts."
    ) from last_exception