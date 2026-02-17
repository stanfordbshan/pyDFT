"""Module entrypoint for `python -m pydft.core`."""

from .parser import main

if __name__ == "__main__":
    raise SystemExit(main())
