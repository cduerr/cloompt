import logging
import sys

from config import DEBUG

"""
debug and exception are used for debugging/logging.
info, warning and error are used to provide user feedback.
- info should be used for standard output (stdout)
- warning should be used for invalid usage and the like (stderr)
- error should be used for errors the user should see (stderr)
"""

logger = logging.getLogger(__name__)


def print_stderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


debug = logger.debug if DEBUG else lambda *args, **kwargs: None
exception = logger.exception if DEBUG else lambda *args, **kwargs: None
error = logger.error if DEBUG else print_stderr
warning = logger.warning if DEBUG else print_stderr
info = logger.info if DEBUG else print
