import os
import shutil


def get_terminal_width():
    """
    Get the width of the terminal in characters.
    :return: (int) terminal width
    """
    try:
        columns = int(os.environ.get("COLUMNS", 0))
    except ValueError:
        columns = 0
    if not columns:
        try:
            columns = shutil.get_terminal_size().columns
        except OSError:
            columns = 80
    return columns
