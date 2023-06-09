import logging

# Dev
DEBUG = False

# App
APP_NAME = "cloompt"

# Not-yet user-configurable
OPENAI_REQUEST_TIMEOUT = 60
OPENAI_READ_TIMEOUT = 60
OPENAI_MAX_TOKENS = 4096
MAX_HISTORY_MESSAGE_COUNT = 500
MAX_DIALOG_REQUEST_SIZE = 20
PRUNE_CONTEXT_AFTER_DAYS = 10

# CLI/ENV Configurable
DEFAULT_PYGMENTS_STYLE = "monokai"
OPENAI_DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_EDITOR = "vi"

# Internal
LOGLEVEL = logging.DEBUG if DEBUG else logging.ERROR
LOGLEVEL_LIB = logging.ERROR if DEBUG else logging.CRITICAL
if DEBUG:
    import coloredlogs

    coloredlogs.install(
        fmt="%(asctime)s.%(msecs)03d %(hostname)s[%(process)d] "
        "%(message)s %(name)s %(levelname)s"  # noqa
    )

# Help
HELP_ADDENDUM = f"""Environment Variables:
    OPENAI_API_KEY 
        Required, set to your OpenAI API key
        $ export OPENAI_API_KEY="sk-..."
    CLOOMPT_OPTIONS 
        Optional, set to assign default options
        $ export CLOOMPT_OPTIONS="-t code -c -x"
    EDITOR environment variable may be set to override default editor ({DEFAULT_EDITOR})
        $ export EDITOR="nvim"
        
Proompt Templates:
    Proompt templates must reside in ~/.config/cloompt/proompts/ 
     
    ~/.config/cloompt/proompts/my_template.jinja2
    Use this to define a "system" user prompt for the dialog.
    
    ~/.config/cloompt/proompts/my_template.prefix.jinja2
    This template is prepended to the user prompt.
    
    ~/.config/cloompt/proompts/my_template.postfix.jinja2
    This template is appended to the user prompt."""
