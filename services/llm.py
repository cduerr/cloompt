import openai

from config import OPENAI_DEFAULT_MODEL, OPENAI_READ_TIMEOUT, OPENAI_REQUEST_TIMEOUT


def query_chatgpt(dialog, model=OPENAI_DEFAULT_MODEL, temperature: float = 1.0) -> str:
    response = openai.ChatCompletion.create(
        model=model if model else OPENAI_DEFAULT_MODEL,
        messages=dialog,
        timeout=OPENAI_READ_TIMEOUT,
        request_timeout=OPENAI_REQUEST_TIMEOUT,
        temperature=temperature,
    )

    # return the raw response
    return response["choices"][0]["message"]["content"]
