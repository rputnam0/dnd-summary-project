from types import SimpleNamespace

import numpy as np
import pytest

from src.thermo_model import delta_h_vap, dew_point_from_vapor, thermo_model_solver


def test_dew_point_single_condensable_respects_corrections():
    y = [0.05, 0.95]
    pressure = 101325.0

    def psat(T):
        return [0.0, 1200.0 * (T - 260.0)]

    expected_psat = y[1] * pressure / (0.85 * 1.2)
    expected_temperature = 260.0 + expected_psat / 1200.0

    result = dew_point_from_vapor(
        y,
        pressure,
        psat,
        condensable_mask=[False, True],
        include_phi=True,
        include_poynting=True,
        phi_corrections=[1.0, 0.85],
        poynting_corrections=[1.0, 1.2],
        temperature_bounds=(expected_temperature - 20.0, expected_temperature + 20.0),
    )

    assert np.isclose(result, expected_temperature, rtol=1e-6, atol=1e-6)


def test_thermo_model_solver_tracks_duplicate_solvent_indices():
    state = {"inert_species": "argon"}
    result = thermo_model_solver(["water", "water"], "water", "water", base_state=state)

    assert result.names[0] == "argon"
    assert result.solvent_indices == (1, 2)


def test_delta_h_vap_mass_basis_falls_back_to_molar():
    chem = SimpleNamespace(Hvap_Tb=None, Hvap_Tbm=40000.0, MW=18.01528)
    value = delta_h_vap(chem, basis="mass")
    assert np.isclose(value, chem.Hvap_Tbm / chem.MW)

    chem_missing = SimpleNamespace(Hvap_Tb=None, Hvap_Tbm=None, MW=None)
    with pytest.raises(ValueError):
        delta_h_vap(chem_missing, basis="mass")
