from __future__ import annotations

from fastapi.testclient import TestClient

from pydft.api.app import app
from pydft.application.scf import run_calculation_from_payload


client = TestClient(app)


def test_api_and_application_paths_are_consistent() -> None:
    payload = {
        "symbol": "He",
        "parameters": {
            "r_max": 20.0,
            "num_points": 500,
            "max_iterations": 140,
            "density_mixing": 0.3,
            "density_tolerance": 1e-6,
            "l_max": 1,
            "states_per_l": 4,
            "use_hartree": True,
            "use_exchange": True,
            "use_correlation": True,
            "xc_model": "LDA",
        },
    }

    direct = run_calculation_from_payload(payload).to_dict()
    response = client.post("/api/v1/scf", json=payload)
    assert response.status_code == 200
    via_api = response.json()

    assert via_api["system"] == direct["system"]
    assert via_api["xc_model"] == direct["xc_model"]
    assert abs(via_api["total_energy"] - direct["total_energy"]) < 1e-8
    assert len(via_api["density"]) == len(direct["density"])
