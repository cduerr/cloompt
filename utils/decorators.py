import os
import sys
from functools import wraps

import openai
from jinja2.exceptions import TemplateNotFound

from services.output import exception, warning, error
from config import DEBUG
from utils.errors import (
    PromptNotProvidedError,
    OpenAPIKeyNotFoundError,
    PromptTooLongError,
)


# decorator to wrap cli calls for error handling
def cli_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PromptTooLongError as e:
            exception(e)
            warning("Prompt too long.")
            sys.exit(7)
        except PromptNotProvidedError as e:
            exception(e)
            warning("No prompt provided.")
            sys.exit(6)
        except OpenAPIKeyNotFoundError as e:
            exception(e)
            warning("OPENAI_API_KEY environment variable must be set.")
            sys.exit(5)
        except NotImplementedError:
            warning("This feature is not implemented.")
            sys.exit(4)
        except openai.error.InvalidRequestError as e:
            exception(e)
            error(e)
            error("Invalid OpenAPI request.")
            sys.exit(3)
        except TemplateNotFound as e:
            exception(e)
            error(e)
            warning("Template not found.")
            sys.exit(2)
        except Exception as e:
            if DEBUG:
                raise e
            error("An unexpected error occurred.")
            error(e)
            sys.exit(1)

    return wrapper


# decorator to require openapi api key
def require_openai_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            raise OpenAPIKeyNotFoundError
        return func(*args, **kwargs)

    return wrapper
