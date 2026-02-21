from __future__ import annotations

import pytest

from pydft.core.request_mapper import parse_request_payload


def test_parse_request_payload_accepts_lsda_settings() -> None:
    _system, params = parse_request_payload(
        {
            "symbol": "H",
            "parameters": {
                "xc_model": "lsda",
                "spin_polarization": 1.0,
            },
        }
    )

    assert params.xc_model == "LSDA"
    assert params.spin_polarization == 1.0


def test_parse_request_payload_ignores_spin_polarization_in_lda() -> None:
    _system, params = parse_request_payload(
        {
            "symbol": "He",
            "parameters": {
                "xc_model": "LDA",
                "spin_polarization": 0.4,
            },
        }
    )

    assert params.xc_model == "LDA"
    assert params.spin_polarization is None


def test_parse_request_payload_rejects_invalid_spin_polarization() -> None:
    with pytest.raises(ValueError):
        parse_request_payload(
            {
                "symbol": "Li",
                "parameters": {
                    "xc_model": "LSDA",
                    "spin_polarization": -1.2,
                },
            }
        )


def test_parse_request_payload_accepts_hf_settings() -> None:
    _system, params = parse_request_payload(
        {
            "symbol": "He",
            "parameters": {
                "xc_model": "HF",
                "spin_polarization": 0.0,
                "use_hartree": False,
                "use_exchange": False,
                "use_correlation": True,
            },
        }
    )

    assert params.xc_model == "HF"
    assert params.spin_polarization == 0.0
    # HF mode enforces pure HF terms.
    assert params.use_hartree is True
    assert params.use_exchange is True
    assert params.use_correlation is False
