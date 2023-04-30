import openai

from config import (
    OPENAI_DEFAULT_MODEL,
    OPENAI_READ_TIMEOUT,
    OPENAI_REQUEST_TIMEOUT,
    MAX_DIALOG_REQUEST_SIZE,
    OPENAI_MAX_TOKENS,
)
from services.context import dialog_token_count
from utils.errors import PromptTooLongError


def query_chatgpt(
    prompt, dialog_, model=OPENAI_DEFAULT_MODEL, temperature: float = 1.0
) -> str:
    dialog = dialog_.copy()
    dialog.append({"role": "user", "content": prompt})

    # trim dialog to MAX_DIALOG_REQUEST_SIZE messages
    dialog = dialog[-MAX_DIALOG_REQUEST_SIZE:]

    # Remove from top of dialog until the token count is <= OPENAI_MAX_TOKENS
    while dialog_token_count(dialog, model_name=model) > OPENAI_MAX_TOKENS:
        dialog = dialog[1:]

    if len(dialog) == 0:
        raise PromptTooLongError()

    response = openai.ChatCompletion.create(
        model=model if model else OPENAI_DEFAULT_MODEL,
        messages=dialog,
        timeout=OPENAI_READ_TIMEOUT,
        request_timeout=OPENAI_REQUEST_TIMEOUT,
        temperature=temperature,
    )

    # return the raw response
    return response["choices"][0]["message"]["content"]
