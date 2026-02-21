"""FastAPI application that exposes backend DFT/HF calculations."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pydft.application.scf import list_preset_dicts, run_calculation_from_payload


class SCFParametersPayload(BaseModel):
    """JSON payload schema for SCF parameters."""

    r_max: float = Field(default=20.0, gt=0)
    num_points: int = Field(default=1200, ge=50)
    max_iterations: int = Field(default=200, ge=1)
    density_mixing: float = Field(default=0.3, gt=0, le=1)
    density_tolerance: float = Field(default=1e-6, gt=0)
    l_max: int = Field(default=1, ge=0)
    states_per_l: int = Field(default=4, ge=1)
    use_hartree: bool = True
    use_exchange: bool = True
    use_correlation: bool = True
    xc_model: Literal["LDA", "LSDA", "HF"] = "LDA"
    spin_polarization: float | None = Field(default=None, ge=-1, le=1)


class SCFRequest(BaseModel):
    """JSON payload schema for one SCF calculation request."""

    symbol: str | None = "He"
    atomic_number: int | None = Field(default=None, ge=1)
    electrons: int | None = Field(default=None, ge=1)
    parameters: SCFParametersPayload = Field(default_factory=SCFParametersPayload)


app = FastAPI(
    title="pyDFT backend API",
    description="Educational atomic LDA/LSDA/HF backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    """Health endpoint for UI and integration checks."""

    return {"status": "ok"}


@app.get("/api/v1/presets")
def presets() -> list[dict]:
    """Return bundled system presets."""

    return list_preset_dicts()


@app.post("/api/v1/scf")
def solve(request: SCFRequest) -> dict:
    """Run one SCF calculation and return serialized results."""

    try:
        result = run_calculation_from_payload(
            {
                "symbol": request.symbol,
                "atomic_number": request.atomic_number,
                "electrons": request.electrons,
                "parameters": request.parameters.model_dump(),
            }
        )
        return result.to_dict()
    except Exception as exc:  # pragma: no cover - keeps API error readable.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
