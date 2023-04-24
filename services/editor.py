import os
import subprocess
import tempfile


DEFAULT_EDITOR = "vi"


def edit_string(prompt: str) -> str:
    """
    Edit a string in the default editor.
    :param prompt: (str) string to edit
    :return: (str) edited string
    """
    editor = os.environ.get("EDITOR", DEFAULT_EDITOR)
    with tempfile.NamedTemporaryFile(suffix=".tmp", mode="w+") as tf:
        if prompt:
            tf.write(prompt)
            tf.flush()
        subprocess.call([editor, tf.name])
        with open(tf.name, "r") as edited_file:
            prompt = edited_file.read().strip()

    return prompt
