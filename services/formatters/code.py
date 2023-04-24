import re

from services.formatters.formatter import Formatter


from pygments import highlight
from pygments.lexers import guess_lexer


class CodeFormatter(Formatter):
    def format(self, content: str, enable_color: bool, style: str) -> str:
        formatter = self.get_pygments_formatter(style)
        response: str = ""

        # check those that give us a language string
        code_blocks = re.findall(r"```([^\n]*)\n((?:.|\n)*?)```", content)

        # remove any code blocks with empty language strings
        code_blocks = [code_block for code_block in code_blocks if code_block[0]]

        if not code_blocks:
            response = (
                highlight(content, guess_lexer(content), formatter)
                if enable_color
                else content
            )

        else:
            for language, code_block in code_blocks:
                if enable_color:
                    code_block = highlight(
                        code_block, self.get_lexer(language, code_block), formatter
                    )
                response += f"{code_block}\n"

        return response.strip()
