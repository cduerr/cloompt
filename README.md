## cloompt

Cloompt is a simple CLI proompter. 

It's another CLI interface for OpenAI's ChatGPT with a couple bells and whistles.

---

### Things it does

- [x] Chat with ChatGPT
- [x] Optional session-based context (conversation/history)
- [x] prompt control (system prompt, prefix/suffix user input) w/ jinja2 templating
- [x] color syntax highlighting (& Pygments styles)
- [x] i/o redirection
- [x] interactive mode
- [x] specify default CLI options in $CLOOMPT_OPTIONS
- [x] prompt with your default $EDITOR

---

### Example use:

Talk to ChatGPT:
`$ lm "What is the meaning of life?"`

Generate a git commit message:
`$ echo "$(git diff HEAD | sed 1,2d)" | lm -t commit --no-context`

Write code:
`$ lm -x "write a Java program that displays the current time"`
`$ lm -t code -x "Perl program that translate C to Pascal" > translator.pl`

Explain code:
`$ cat translator.pl | lm -t explain`

```

---

### Quickstart for `fish` heads

The instructions will make the following commands (functions) available:

* `lm` - an alias to `cloompt.py`
* `lmc` - this invokes `lm` with the `code` proompt and `-x` option to filter for code. 
  Use it to prompt for code.
* `gcm` - this command looks at your git diff vs HEAD to generate a commit message. It 
  uses the `commit` proompt.

```sh

# To install with pipenv (recommended):
# First, be sure to place the cloompt/ folder where you'd like it to live permanently.
$ cd /path/to/where/you/cloned/cloompt
$ pipenv install

# Copy/symlink the fish functions in config/fish/functions/ to ~/.config/fish/functions/
# E.g.,
$ cp config/fish/functions/* ~/.config/fish/functions/

# Edit the fish functions (lm, lmc, gcm) to point to the correct path to cloompt.py & 
# Pipfile. Optionally, copy/symlink the prompts in config/cloompt/proompts/ to 
# ~/.config/cloompt/proompts/
# E.g.,
$ mkdir -p ~/.config/cloompt/proompts
$ cp config/cloompt/proompts/* ~/.config/cloompt/proompts/

# Export your OPENAI_API_KEY
$ set -Ux OPENAI_API_KEY=sk...

# Optional: enable conversation/context by default, and tweak your default options 
# as you'd like.
$ set -Ux CLOOMPT_OPTIONS "-c"

$ lm --help # to see all options
```

---

### Proompting

Proompt templates must reside in `~/.config/cloompt/proompts/`

- `proompt.jinja2`: system prompt for the dialog.
- `proompt.prefix.jinja2`: this template is prepended to the user prompt.
- `proompt.postfix.jinja2`: this template is appended to the user prompt.

`lm --proompt <prompt>`

Template params:

- `shell`: user's shell (e.g., `fish`)
- `platform`: user's platform (e.g., `Darwin`)

By default, the `system` proompt will be used. This is a system prompt 
engineering for general CLI assistance. You may safely delete or replace it.

---

### Context Dialogs / Conversations

Context (dialogs) are saved to ~/.config/cloompt/context/  and maintained automatically. 
Use `--reset` to flush the current session context.
