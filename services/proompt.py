import os
import platform
from typing import Optional

from jinja2 import Environment, FileSystemLoader
import shellingham

from config import APP_NAME


prompt_folder = os.path.join(os.path.expanduser("~"), ".config", APP_NAME, "proompts")

# these are the jinja2 params for proompts
platform_name = f"{platform.system()} {platform.release()}"

try:
    shell_name, _ = shellingham.detect_shell()
except Exception:  # noqa
    shell_name = "bash"


def get_prompt(prompt: Optional[str] = None, suffix: Optional[str] = "") -> str:
    if not prompt:
        return ""

    user_prefix_prompt_path = (
        os.path.join(prompt_folder, f"{prompt}{suffix}.jinja2") if prompt else None
    )
    if user_prefix_prompt_path and os.path.exists(user_prefix_prompt_path):
        cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        env = Environment(loader=FileSystemLoader("/"))
        template = env.get_template(user_prefix_prompt_path)
        user_prefix_prompt = template.render(platform=platform_name, shell=shell_name)
        os.chdir(cwd)
        return user_prefix_prompt

    return ""


def get_user_prefix_prompt(prompt: Optional[str] = None) -> str:
    return get_prompt(prompt, ".prefix")


def get_user_postfix_prompt(prompt: Optional[str] = None) -> str:
    return get_prompt(prompt, ".postfix")


def get_system_prompt(prompt: Optional[str] = "system") -> str:
    return get_prompt(prompt)