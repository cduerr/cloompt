#!/usr/bin/env python
import os
import random
import sys
import logging
import readline  # noqa

from config import (
    OPENAI_DEFAULT_MODEL,
    DEFAULT_PYGMENTS_STYLE,
    LOGLEVEL,
    LOGLEVEL_LIB,
    HELP_ADDENDUM,
    OPENAI_MAX_TOKENS,
)
from services.context import (
    context_prune_all,
    context_reset,
    context_load,
    context_save,
    dialog_print,
    token_count,
)
from services.editor import edit_string
from services.formatters.code import CodeFormatter
from services.formatters.default import DefaultFormatter
from services.formatters.formatter import display_style_grid
from services.llm import query_chatgpt
from services.output import info, error, exception, warning
from services.proompt import (
    get_system_prompt,
    get_user_postfix_prompt,
    get_user_prefix_prompt,
    get_prompt_override,
)
from utils.decorators import cli_error_handler, require_openai_api_key
from utils.errors import PromptNotProvidedError, PromptTooLongError

import click


logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)
logging.getLogger("openai").setLevel(LOGLEVEL_LIB)


@click.command()
@click.option("-h", "--help", "help_", is_flag=True, help="Show this help.")
@click.option("-e", "--editor", is_flag=True, help="Open $EDITOR to edit prompt.")
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Interactive mode. (Implies --contextual, ignores --no-context)",
)
@click.option(
    "-m",
    "--model",
    default=OPENAI_DEFAULT_MODEL,
    help="Model to use (defaults to 'gpt-3.5-turbo').",
)
@click.option(
    "--temp",
    "--temperature",
    "temperature",
    default=1.0,
    help="Temperature (defaults to 1.0).",
)
@click.option("--list-styles", is_flag=True, help="List available pygments styles.")
@click.option("--no-color", "no_color", is_flag=True, help="Disable color output.")
@click.option(
    "--style", default=DEFAULT_PYGMENTS_STYLE, help="Pygments syntax-highlight style."
)
@click.option(
    "-c", "--contextual", is_flag=True, help="Maintain context for conversation."
)
@click.option(
    "-C",
    "--no-context",
    "no_context",
    is_flag=True,
    help="Disable context for conversation (overrides -c).",
)
@click.option(
    "--history",
    default=None,
    is_flag=False,
    flag_value="text",
    required=False,
    help="Show context history. Use `--history json` to show as json.",
)
@click.option(
    "--reset", "--reset-context", "reset_context", is_flag=True, help="Reset context."
)
@click.option(
    "-t",
    "--template",
    "--proompt",
    "prompt_template",
    default="system",
    required=False,
    help="Prompt template name (defaults to 'system')",
)
@click.option(
    "-T",
    "--no-template",
    "--no-proompt",
    "no_prompt_template",
    is_flag=True,
    help="Disable prompt templates (overrides -t only).",
)
@click.option(
    "-p",
    "--system-proompt",
    "system_prompt_override",
    default="",
    required=False,
    help="<path> or <str> System prompt file or string override."
    " (overrides --template for system prompt only)",
)
@click.option(
    "--prefix",
    "--prefix-proompt",
    "prefix_prompt_override",
    default="",
    required=False,
    help="<path> or <str> Prefix prompt file or string override."
    " (overrides --template for prefix prompt only)",
)
@click.option(
    "--postfix",
    "--suffix",
    "--postfix-proompt",
    "postfix_prompt_override",
    default="",
    required=False,
    help="<path> or <str> Postfix (user suffix) prompt file or string override."
    " (overrides --template for postfix prompt only)",
)
@click.option(
    "-x",
    "--code",
    "fmt_code",
    is_flag=True,
    help="code formatter- strips non-code from output when possible",
)
@click.argument("prompt", required=False, default="")
@cli_error_handler
@require_openai_api_key
def lm(
    help_,
    editor,
    interactive,
    model,
    temperature,
    list_styles,
    no_color,
    style,
    contextual,
    no_context,
    history,
    reset_context,
    prompt_template,
    no_prompt_template,
    system_prompt_override,
    prefix_prompt_override,
    postfix_prompt_override,
    fmt_code,
    prompt,
):
    """cloompt - the cli proompter"""
    prompt = prompt.strip()
    prompt_template = prompt_template.strip() if not no_prompt_template else ""
    style = style or DEFAULT_PYGMENTS_STYLE
    no_color = no_color if sys.stdout.isatty() else True
    contextual = (contextual and not no_context) or interactive
    temperature = float(temperature)
    history = history.lower() if history else None
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

    # show context history
    if history:
        dialog_print(
            context_load(),
            as_json=(history == "json"),
            enable_color=not no_color,
            style=style,
        )

    # reset context if requested and in contextual mode
    if reset_context:
        info("Context reset." if context_reset() else "No context to reset.")

    # exit if no prompt is provided and one of reset, list_styles, or help specified
    if not prompt and (reset_context or list_styles or help_ or history):
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

    # Load the prompt templates (proompts)
    user_prefix_prompt = get_user_prefix_prompt(prompt_template)
    user_postfix_prompt = get_user_postfix_prompt(prompt_template)
    system_prompt = get_system_prompt(prompt_template)

    # Load the proompt overrides (system, prefix, postfix prompts)
    # Load from file if these are valid paths, otherwise treat as strings.
    if system_prompt_override:
        system_prompt = get_prompt_override(system_prompt_override).strip()
    if prefix_prompt_override:
        user_prefix_prompt = get_prompt_override(prefix_prompt_override).strip()
    if postfix_prompt_override:
        user_postfix_prompt = get_prompt_override(postfix_prompt_override).strip()

    # Add system prompt to the dialog
    if system_prompt:
        dialog.append({"role": "system", "content": system_prompt})

    while True:
        # if we're interactive and no prompt is provided, prompt user.
        try:
            if interactive and not prompt:
                # Read user input from console (ignore empty lines)
                while True:
                    prompt = input("> ").strip()
                    if prompt:
                        break
                if prompt.lower() in ("exit", "quit", "stop", "q", "x", ":q", ":q!"):
                    break

            # Apply the prompt prefix/postfix
            modified_prompt = prompt
            if user_prefix_prompt:
                modified_prompt = user_prefix_prompt + "\n\n" + prompt
            if user_postfix_prompt:
                modified_prompt += "\n\n" + user_postfix_prompt

            # ensure the prompt <= OPENAI_MAX_TOKENS
            t_count = token_count(modified_prompt, model_name=model)
            if t_count > OPENAI_MAX_TOKENS:
                if not interactive:
                    raise PromptTooLongError()
                else:
                    warning(f"Prompt too long ({t_count} tokens > {OPENAI_MAX_TOKENS})")
                    continue

            # query chatgpt
            response_content_raw = query_chatgpt(
                modified_prompt, dialog, model=model, temperature=temperature
            )

            # Add the (unmodified) prompt and response to the dialog
            dialog.append({"role": "user", "content": prompt})
            dialog.append({"role": "assistant", "content": response_content_raw})

            # save the context
            if contextual:
                context_save(dialog)

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
