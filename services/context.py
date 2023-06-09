import json
import os
import time

import psutil
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from termcolor import cprint
import tiktoken

import config
from config import (
    PRUNE_CONTEXT_AFTER_DAYS,
    APP_NAME,
    OPENAI_DEFAULT_MODEL,
    MAX_HISTORY_MESSAGE_COUNT,
)
from services.formatters.formatter import Formatter
from services.output import debug


parent_pid = os.getppid()
context_folder = os.path.join(os.path.expanduser("~"), ".config", APP_NAME, "context")
context_file = os.path.join(context_folder, f"{parent_pid}.json")


def dialog_print(
    dialog: list[dict],
    as_json: bool = False,
    enable_color: bool = False,
    style: str = config.DEFAULT_PYGMENTS_STYLE,
) -> None:
    if as_json:
        raw_json = json.dumps(dialog, indent=4)
        if not enable_color:
            print(raw_json)
        else:
            formatter = Formatter.get_pygments_formatter(style)
            print(highlight(raw_json, get_lexer_by_name("json"), formatter))
    else:
        for message in dialog:
            role = message.get("role")
            content = message.get("content")
            if enable_color:
                cprint(
                    role,
                    "white"
                    if role == "user"
                    else "green"
                    if "assistant"
                    else "red"
                    if "system"
                    else "yellow",
                    end=": ",
                )
                cprint(content, "light_grey", end="\n")
            else:
                print(f"{role}: {content}")


def token_count(prompt: str, model_name: str = OPENAI_DEFAULT_MODEL) -> int:
    enc = tiktoken.encoding_for_model(model_name)
    return len(enc.encode(prompt))


def dialog_token_count(dialog: list[dict], model_name: str = OPENAI_DEFAULT_MODEL):
    dialog_json = json.dumps(dialog)
    t_count = 0
    for message in dialog:
        content = message.get("content")
        role = message.get("role")
        # Just counting the message length seems to be off, so we tack on
        # roles and brace count (which is still wrong, but closer- I think)
        t_count += token_count(content, model_name=model_name)
        t_count += token_count(role, model_name=model_name)
    t_count += dialog_json.count("{")
    t_count += dialog_json.count("}")
    return t_count


def context_reset() -> bool:
    if os.path.exists(context_file):
        os.remove(context_file)
        return True
    return False


def context_load() -> list:
    if os.path.exists(context_file):
        with open(context_file, "r") as f:
            return json.load(f)
    return []


def context_save(dialog_):
    dialog = dialog_.copy()

    # remove system messages
    dialog = [message for message in dialog if message.get("role") != "system"]

    # truncate dialog to max history message count
    dialog = dialog[-MAX_HISTORY_MESSAGE_COUNT:]

    # save dialog to file
    if not os.path.exists(os.path.dirname(context_file)):
        os.makedirs(os.path.dirname(context_file))
    with open(context_file, "w") as f:
        json.dump(dialog, f)


def context_prune_all() -> None:
    """
    Prune context folder of stale files.
    :return: None
    """
    if os.path.exists(context_folder):
        for file in os.listdir(context_folder):
            pid = int(file.split(".")[0])
            file_update_time = os.path.getmtime(os.path.join(context_folder, file))
            if not psutil.pid_exists(pid):
                debug(f"Deleting {file} from {context_folder} (pid {pid} not running)")
                os.remove(os.path.join(context_folder, file))
            elif time.time() - file_update_time > (
                PRUNE_CONTEXT_AFTER_DAYS * 24 * 60 * 60
            ):
                debug(f"Deleting {file} from {context_folder} (older than 30 days)")
                os.remove(os.path.join(context_folder, file))
