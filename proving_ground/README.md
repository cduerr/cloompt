### containerized proving-ground for ml-generated code

idea here is something like:

`echo "make a program that..." | cloompt | pg`

where `pg` invokes docker (smartly, see below) to run the generated code (piped/stdin) in a container.

challenge here is-
- possible to pipe through docker? if not, temp file?
- detecting the language, container provision code for each

going to avoid any attempts to virtually stage the active running environment.
