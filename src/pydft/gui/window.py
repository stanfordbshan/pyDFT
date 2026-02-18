"""pywebview desktop launcher for the pyDFT application."""

from __future__ import annotations

import argparse
from pathlib import Path

from .bridge import ThinkBridge


def main() -> int:
    """Open the desktop window and bind the Python-JS bridge API."""

    parser = argparse.ArgumentParser(description="Run pyDFT pywebview frontend")
    parser.add_argument("--debug", action="store_true", help="Enable pywebview debug mode")
    args = parser.parse_args()

    try:
        import webview
    except ImportError as exc:  # pragma: no cover - optional dependency path.
        raise SystemExit(
            "pywebview is not installed. Install frontend extras: pip install '.[frontend]'"
        ) from exc

    ui_path = Path(__file__).resolve().parent / "assets" / "index.html"

    webview.create_window(
        title="pyDFT Educational Workbench",
        url=ui_path.as_uri(),
        js_api=ThinkBridge(),
        width=1200,
        height=820,
        min_size=(900, 640),
    )
    webview.start(debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
