#!/usr/bin/env python
import os
import random
import sys
import logging
import readline  # noqa - this is used implicitly by input()

from config import (
    OPENAI_DEFAULT_MODEL,
    DEFAULT_PYGMENTS_STYLE,
    LOGLEVEL,
    LOGLEVEL_LIB,
    HELP_ADDENDUM,
)
from services.context import (
    context_prune_all,
    context_reset,
    context_load,
    context_save,
)
from services.editor import edit_string
from services.formatters.code import CodeFormatter
from services.formatters.default import DefaultFormatter
from services.formatters.formatter import display_style_grid
from services.llm import query_chatgpt
from services.output import info, error, exception
from services.proompt import (
    get_system_prompt,
    get_user_postfix_prompt,
    get_user_prefix_prompt,
)
from utils.decorators import cli_error_handler, require_openai_api_key
from utils.errors import PromptNotProvidedError

import click


logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)
logging.getLogger("openai").setLevel(LOGLEVEL_LIB)


@click.command()
@click.option(
    "-h", "--help", "help_", is_flag=True, help="Show extended help and exit."
)
@click.option("-e", "--editor", is_flag=True, help="Open $EDITOR to edit prompt.")
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Interactive mode. (Implies --contextual, ignores --no-context)",
)
@click.option("-m", "--model", default=OPENAI_DEFAULT_MODEL, help="Model to use.")
@click.option("--list-styles", is_flag=True, help="List available pygments styles.")
@click.option("--no-color", "no_color", is_flag=True, help="Disable color output.")
@click.option(
    "--style", default=DEFAULT_PYGMENTS_STYLE, help="Pygments syntax-highlight style."
)
@click.option(
    "-c", "--contextual", is_flag=True, help="Maintain context for conversation."
)
@click.option(
    "--no-context",
    "no_context",
    is_flag=True,
    help="Disable context for conversation (overrides -c).",
)
@click.option(
    "--reset",
    "--reset-context",
    "reset_context",
    is_flag=True,
    help="Reset context and exit.",
)
@click.option(
    "-t",
    "--template",
    "--proompt",
    "prompt_template",
    required=False,
    help="Prompt template.",
)
@click.option(
    "--no-template",
    "--no-proompt",
    "no_proompt",
    is_flag=True,
    help="Disable prompt templates (overrides -t).",
)
@click.option(
    "-x",
    "--code",
    "fmt_code",
    is_flag=True,
    help="code formatter- strips non-code from output when possible",
)
@click.argument("prompt", required=False)
@cli_error_handler
@require_openai_api_key
def lm(
    help_,
    editor,
    interactive,
    model,
    list_styles,
    no_color,
    style,
    contextual,
    no_context,
    reset_context,
    prompt_template,
    no_proompt,
    fmt_code,
    prompt,
):
    """cloompt - the cli proompter"""
    prompt = prompt.strip() if prompt else ""
    style = style or DEFAULT_PYGMENTS_STYLE
    no_color = no_color if sys.stdout.isatty() else True
    contextual = (contextual and not no_context) or interactive
    dialog = []

    # maintenance 1 in 10 runs (randomly)
    if random.randint(1, 10) == 1:
        context_prune_all()

    # attempt to read prompt from piped stdin if no prompt is provided as an arg
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read()

    # help
    if help_:
        click.echo(click.get_current_context().get_help())
        info("\n" + HELP_ADDENDUM)

    # style help - list available styles in column format
    if list_styles:
        display_style_grid()

    # reset context if requested and in contextual mode
    if reset_context:
        info("Context reset." if context_reset() else "No context to reset.")

    # exit if no prompt is provided and one of reset, list_styles, or help specified
    if not prompt and (reset_context or list_styles or help_):
        sys.exit(0)

    # invoke editor
    if editor:
        prompt = edit_string(prompt)

    # raise error if no prompt is provided via stdin or argument
    if not prompt and not interactive:
        raise PromptNotProvidedError()

    # Load the context if one exists
    if contextual:
        dialog.extend(context_load())

    # Load the user prompt prefix/suffix (prompt_template)
    if not no_proompt:
        dialog.append({"role": "system", "content": get_system_prompt(prompt_template)})
    user_prefix_prompt = get_user_prefix_prompt(prompt_template)
    user_postfix_prompt = get_user_postfix_prompt(prompt_template)

    while True:
        # if we're interactive and no prompt is provided, prompt user.
        try:
            if interactive and not prompt:
                # Read user input from console (ignore empty lines)
                while True:
                    prompt = input("> ")
                    if prompt:
                        break
                if prompt.lower() in ("exit", "quit", "stop", "q", "x", ":q"):
                    break

            # Apply the prompt prefix/postfix
            if user_prefix_prompt:
                prompt = user_prefix_prompt + "\n\n" + prompt
            if user_postfix_prompt:
                prompt += "\n\n" + user_postfix_prompt

            # Add the user's most recent prompt to the dialog
            dialog.append({"role": "user", "content": prompt})

            # query chatgpt
            response_content_raw = query_chatgpt(dialog, model=model)

            # add the response to the dialog
            dialog.append({"role": "assistant", "content": response_content_raw})

            # save the context
            if contextual:
                context_save(dialog, not no_proompt)

            # format the response
            if fmt_code:
                formatter = CodeFormatter
            else:
                formatter = DefaultFormatter
            response_content_raw = formatter().format(
                content=response_content_raw, enable_color=not no_color, style=style
            )

            # print the response
            print(response_content_raw)

            # exit if not interactive
            if not interactive:
                break
        except Exception as e:
            if not interactive:
                raise
            exception(e)
            error(e)
            error("An unexpected error occurred. Please try again.")

        # clear prompt
        prompt = ""


if __name__ == "__main__":
    # read additional options from env, prepend to cargs
    env_options = os.environ.get("CLOOMPT_OPTIONS", "")
    if env_options:
        sys.argv[1:] = env_options.split() + sys.argv[1:]

    # go
    lm()
