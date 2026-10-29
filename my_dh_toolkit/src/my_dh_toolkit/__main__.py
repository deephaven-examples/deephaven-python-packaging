"""Run my_dh_toolkit as a module: ``python -m my_dh_toolkit``.

This runs the query command. For the batch-process command, use the installed
``my-dh-toolkit-process`` entry point or call ``my_dh_toolkit.process:main``
directly.
"""

from my_dh_toolkit.query import main

if __name__ == "__main__":
    main()
