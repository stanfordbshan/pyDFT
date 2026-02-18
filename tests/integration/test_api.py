from __future__ import annotations

from fastapi.testclient import TestClient

from pydft.core.api import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scf_endpoint_runs_helium_case() -> None:
    response = client.post(
        "/api/v1/scf",
        json={
            "symbol": "He",
            "parameters": {
                "r_max": 18.0,
                "num_points": 500,
                "max_iterations": 120,
                "density_mixing": 0.35,
                "density_tolerance": 1e-5,
                "l_max": 1,
                "states_per_l": 4,
                "use_hartree": True,
                "use_exchange": True,
                "use_correlation": True,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["system"]["symbol"] == "He"
    assert payload["xc_model"] == "LDA"
    assert isinstance(payload["converged"], bool)
    assert payload["iterations"] <= 120
    assert len(payload["density"]) == 500
    assert len(payload["effective_potential"]) == 500


def test_scf_endpoint_runs_lsda_case() -> None:
    response = client.post(
        "/api/v1/scf",
        json={
            "symbol": "H",
            "parameters": {
                "r_max": 20.0,
                "num_points": 500,
                "max_iterations": 120,
                "density_mixing": 0.35,
                "density_tolerance": 1e-5,
                "l_max": 1,
                "states_per_l": 4,
                "use_hartree": True,
                "use_exchange": True,
                "use_correlation": False,
                "xc_model": "LSDA",
                "spin_polarization": 1.0,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["system"]["symbol"] == "H"
    assert payload["xc_model"] == "LSDA"
    assert len(payload["density_up"]) == 500
    assert len(payload["density_down"]) == 500
    assert len(payload["effective_potential_up"]) == 500
    assert len(payload["effective_potential_down"]) == 500
    assert payload["spin_up_electrons"] > payload["spin_down_electrons"]


def test_scf_endpoint_runs_hf_case() -> None:
    response = client.post(
        "/api/v1/scf",
        json={
            "symbol": "He",
            "parameters": {
                "r_max": 22.0,
                "num_points": 600,
                "max_iterations": 140,
                "density_mixing": 0.3,
                "density_tolerance": 1e-6,
                "xc_model": "HF",
                "spin_polarization": 0.0,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["system"]["symbol"] == "He"
    assert payload["xc_model"] == "HF"
    assert payload["converged"] is True
    assert len(payload["density"]) == 600
    assert payload["xc_energy"] < 0.0


def test_scf_endpoint_rejects_hf_outside_supported_scope() -> None:
    response = client.post(
        "/api/v1/scf",
        json={
            "symbol": "Li",
            "parameters": {
                "xc_model": "HF",
            },
        },
    )

    assert response.status_code == 400
    assert "supports at most 2 electrons" in response.json()["detail"]
