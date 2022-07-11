from functools import wraps
from time import sleep

from plexapi.exceptions import BadRequest
from requests import ReadTimeout, RequestException
from trakt.errors import TraktInternalException

from plextraktsync.logging import logger


def retry(retries=5):
    """
    retry a call retries times

    :param retries: number of retries
    :return:
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            count = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except (
                        BadRequest,
                        ReadTimeout,
                        RequestException,
                        TraktInternalException,
                ) as e:
                    if count == retries:
                        logger.error(f"Error: {e}")
                        logger.error(
                            "API didn't respond properly, script will abort now. Please try again later."
                        )
                        logger.error(
                            f"Last call: {fn.__module__}.{fn.__name__}({args[1:]}, {kwargs})"
                        )
                        exit(1)

                    seconds = 1 + count
                    count += 1
                    logger.warning(
                        f"{e} for {fn.__module__}.{fn.__name__}(), retrying after {seconds} seconds (try: {count}/{retries})"
                    )
                    sleep(seconds)

        return wrapper

    return decorator