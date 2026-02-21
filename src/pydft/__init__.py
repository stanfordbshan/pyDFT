"""pyDFT package.

The package is organized into:
- `pydft.core`: domain models and shared mapping utilities.
- `pydft.application`: transport-agnostic use-cases.
- `pydft.methods`: method-specific numerical implementations.
- `pydft.api`: HTTP adapter.
- `pydft.gui`: pywebview desktop frontend logic.
- `pydft.gui.assets`: static HTML/CSS/JS assets rendered by the GUI.
"""

__all__ = ["core", "application", "methods", "api", "gui"]
