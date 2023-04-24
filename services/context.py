import json
import os
import time

import psutil

from config import PRUNE_CONTEXT_AFTER_DAYS, MAX_DIALOG_LENGTH, APP_NAME
from services.output import debug


parent_pid = os.getppid()
context_folder = os.path.join(os.path.expanduser("~"), ".config", APP_NAME, "context")
context_file = os.path.join(context_folder, f"{parent_pid}.json")


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


def context_save(dialog, prune_system_prompt: bool = False):
    if prune_system_prompt:
        dialog.pop(0)
    while len(dialog) > MAX_DIALOG_LENGTH:
        dialog.pop(0)
    if not os.path.exists(os.path.dirname(context_file)):
        os.makedirs(os.path.dirname(context_file))
    with open(context_file, "w") as f:
        json.dump(dialog, f, indent=4)
    return dialog


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
