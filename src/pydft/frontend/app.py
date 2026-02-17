"""pywebview desktop launcher for the pyDFT frontend.

The frontend is intentionally thin: it only calls backend API endpoints.
"""

from __future__ import annotations

import argparse
import socket
import threading
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn


def _pick_free_port() -> int:
    """Return an available localhost TCP port."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_backend(port: int, timeout_seconds: float = 8.0) -> None:
    """Block until backend health endpoint is reachable."""

    deadline = time.time() + timeout_seconds
    endpoint = f"http://127.0.0.1:{port}/api/v1/health"

    while time.time() < deadline:
        try:
            with urlopen(endpoint, timeout=0.5) as response:
                if response.status == 200:
                    return
        except URLError:
            time.sleep(0.1)

    raise RuntimeError("Backend API server did not become ready in time")


def main() -> int:
    """Start local API server and open pywebview frontend."""

    parser = argparse.ArgumentParser(description="Run pyDFT pywebview frontend")
    parser.add_argument("--port", type=int, default=None, help="Optional fixed backend port")
    parser.add_argument("--debug", action="store_true", help="Enable pywebview debug mode")
    args = parser.parse_args()

    try:
        import webview
    except ImportError as exc:  # pragma: no cover - optional dependency path.
        raise SystemExit(
            "pywebview is not installed. Install frontend extras: pip install '.[frontend]'"
        ) from exc

    from pydft.backend.api import app as backend_app

    port = args.port or _pick_free_port()

    config = uvicorn.Config(backend_app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    _wait_for_backend(port)

    ui_path = Path(__file__).parent / "ui" / "index.html"
    api_base = f"http://127.0.0.1:{port}"
    window_url = f"{ui_path.as_uri()}?apiBase={api_base}"

    webview.create_window(
        title="pyDFT Educational Workbench",
        url=window_url,
        width=1200,
        height=820,
        min_size=(900, 640),
    )
    webview.start(debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
