import re

from pygments import highlight

from services.formatters.formatter import Formatter


class DefaultFormatter(Formatter):
    @staticmethod
    def syntax_highlight_code_blocks(content: str, pygments_formatter) -> str:
        """
        syntax highlight code blocks
        :param content: (str) content to syntax highlight
        :param pygments_formatter: (pygments.formatter) pygments formatter
        :return: (str) content with syntax highlighted code blocks
        """
        content = re.sub(
            r"```([^\n]*)\n((?:.|\n)*?)```",
            lambda m: "```"
            + m.group(1)
            + "\n"
            + highlight(
                m.group(2),
                DefaultFormatter.get_lexer(m.group(1), m.group(2)),
                pygments_formatter,
            )
            + "```",
            content,
        )
        return content

    def format(self, content: str, enable_color: bool, style: str) -> str:
        # syntax-highlight content between triple backticks
        if enable_color:
            formatter = self.get_pygments_formatter(style)
            if formatter:
                content = self.syntax_highlight_code_blocks(content, formatter)

        # remove surrounding triple backticks & language string only
        # if the entire response is surrounded by triple backticks
        if content.startswith("```") and content.endswith("```"):
            content = re.sub(
                r"```([^\n]*)\n((?:.|\n)*?)```", lambda m: m.group(2), content
            )

        return content.strip()
