"""Module entrypoint for `python -m pydft.backend`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
