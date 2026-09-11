"""My Deephaven package for data processing.

This __init__ deliberately imports nothing that requires Deephaven: the CLI
entry points import this package before a Deephaven server is running, so the
package must be importable without one. The library API lives in the
`my_dh_toolkit.queries` and `my_dh_toolkit.utils` submodules.
"""

__version__ = "0.1.0"
