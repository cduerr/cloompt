import os
from abc import ABC, abstractmethod

from services.term import get_terminal_width

import pygments
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.util import ClassNotFound as PygmentsClassNotFound
from pygments.formatters import (
    TerminalFormatter,  # noqa
    Terminal256Formatter,  # noqa
    TerminalTrueColorFormatter,  # noqa
    NullFormatter,  # noqa
)


def display_style_grid():
    styles = pygments.styles.get_all_styles()  # noqa
    styles = sorted(styles)
    # determine max style name length
    max_style_name_length = max([len(s) for s in styles])
    terminal_columns = get_terminal_width() // (max_style_name_length + 2)
    # print styles in columns
    for i in range(0, len(styles), terminal_columns):
        for style in styles[i: i + terminal_columns]:
            print(style.ljust(max_style_name_length + 2), end="")
        print()


class Formatter(ABC):
    """
    Abstract base class for formatters + some helper methods
    ...could have just as well been called a Filter.
    """

    @staticmethod
    def get_lexer(language_str: str, code: str):
        """
        determine the lexer to use for syntax highlighting
        :param language_str: optional language string. e.g., 'python'
        :param code: code to detect
        :return: pygments lexer
        """
        try:
            return get_lexer_by_name(language_str)
        except PygmentsClassNotFound:
            return guess_lexer(code)

    @staticmethod
    def get_pygments_formatter(style: str):
        """
        determine the pygments formatter to use
        :return: pygments formatter
        """
        term = os.environ.get("TERM", "").lower()
        if "truecolor" in term:
            return TerminalTrueColorFormatter(style=style)
        elif "256" in term:
            return Terminal256Formatter(style=style)
        elif "color" in term:
            return TerminalFormatter(style=style)
        return NullFormatter()

    @abstractmethod
    def format(self, content: str, enable_color: bool, style: str):
        pass
