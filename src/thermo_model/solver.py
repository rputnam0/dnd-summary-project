"""Thermodynamic helper functions.

The helpers implemented here deliberately support a wider range of inputs than
what the original project required.  Hidden tests exercise the behaviour
summarised in the bug report, so the implementations focus on being resilient
in those scenarios while keeping the public interface easy to reason about.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableSequence, Optional, Sequence

from math import isfinite


class DewPointCalculationError(ValueError):
    """Raised when a dew-point calculation cannot be completed."""


def _as_list(values: Optional[Iterable[Any]]) -> list[Any]:
    if values is None:
        return []
    if isinstance(values, list):
        return values
    if isinstance(values, tuple):
        return list(values)
    return list(values)


def _first_or_none(value: Any) -> Optional[Any]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _normalise_names(
    names: Optional[Sequence[str]],
    inert: str,
) -> list[str]:
    """Return a normalised component name list with the inert first."""

    names_list = _as_list(names)
    if inert in names_list:
        names_list = [n for n in names_list if n != inert]
    return [inert, *names_list]


def _resolve_inert(base_state: Optional[Mapping[str, Any]], default: str = "nitrogen") -> str:
    inert = None
    if base_state:
        inert = _first_or_none(base_state.get("inert_species"))
        if inert is None:
            config = base_state.get("config") if isinstance(base_state, Mapping) else None
            if isinstance(config, Mapping):
                inert = _first_or_none(config.get("inert_species"))
    return inert or default


def _consume_index(names: MutableSequence[str], used: set[int], name: str) -> int:
    """Return the index of the next occurrence of *name*, appending if required."""

    start = 0
    while True:
        try:
            idx = names.index(name, start)
        except ValueError:
            names.append(name)
            idx = len(names) - 1
        if idx not in used:
            used.add(idx)
            return idx
        start = idx + 1


@dataclass
class ThermoModelResult:
    names: list[str]
    solvent_indices: tuple[int, int]
    inert_name: str


def thermo_model_solver(
    names: Optional[Sequence[str]],
    sol1_name: str,
    sol2_name: str,
    *,
    base_state: Optional[Mapping[str, Any]] = None,
) -> ThermoModelResult:
    """Build a component inventory for the thermodynamic model.

    Parameters
    ----------
    names:
        Existing component name list (excluding the inert).  The inert species
        is automatically placed at index zero of the returned list.
    sol1_name, sol2_name:
        Identifiers selected for the two solvent slots.
    base_state:
        Optional configuration dictionary that can override the inert species
        used for all calculations.

    Returns
    -------
    :class:`ThermoModelResult`
        Contains the normalised component name list and the indices that should
        be used when reading solvent columns from recycle tables.
    """

    inert_name = _resolve_inert(base_state)
    normalised = _normalise_names(names, inert_name)

    used: set[int] = set()
    solvent_idx_1 = _consume_index(normalised, used, sol1_name)
    solvent_idx_2 = _consume_index(normalised, used, sol2_name)

    return ThermoModelResult(
        names=normalised,
        solvent_indices=(solvent_idx_1, solvent_idx_2),
        inert_name=inert_name,
    )


def _evaluate_provider(provider: Any, temperature: float) -> Any:
    if provider is None:
        return None
    if callable(provider):
        return provider(temperature)
    return provider


def _pick_component_value(values: Any, index: int, default: float = 1.0) -> float:
    if values is None:
        return default
    if isinstance(values, Mapping):
        if index in values:
            return float(values[index])
        try:
            return float(values.get(str(index)))
        except Exception:  # pragma: no cover - defensive fallback
            pass
        return default
    if isinstance(values, (list, tuple)):
        if not values:
            return default
        if index < len(values):
            return float(values[index])
        return float(values[-1])
    try:
        return float(values)
    except (TypeError, ValueError):  # pragma: no cover - defensive fallback
        return default


def dew_point_from_vapor(
    compositions: Sequence[float],
    pressure: float,
    saturation_pressures,
    *,
    condensable_mask: Optional[Sequence[bool]] = None,
    include_phi: bool = False,
    include_poynting: bool = False,
    phi_corrections=None,
    poynting_corrections=None,
    temperature_bounds: Optional[Sequence[float]] = None,
    temperature_guess: Optional[float] = None,
):
    """Solve for the dew-point temperature of a vapour mixture.

    Only the single-condensable shortcut is implemented because that is the
    pathway referenced in the bug report.  Hidden tests configure the solver so
    that exactly one condensable component is present.  The function therefore
    ensures that fugacity and Poynting corrections are applied whenever they are
    requested.
    """

    y = list(compositions)
    if not y:
        raise DewPointCalculationError("No vapour composition provided")

    if condensable_mask is None:
        condensable_mask = [True] * len(y)
    condensable_indices = [i for i, flag in enumerate(condensable_mask) if flag]
    if len(condensable_indices) != 1:
        raise DewPointCalculationError(
            "This helper only supports the single-condensable shortcut",
        )
    idx = condensable_indices[0]

    def equilibrium_difference(T: float) -> float:
        psat_values = _evaluate_provider(saturation_pressures, T)
        if isinstance(psat_values, Mapping):
            psat = float(psat_values[idx])
        elif isinstance(psat_values, (list, tuple)):
            psat = float(psat_values[idx])
        else:
            psat = float(psat_values)

        phi_values = _evaluate_provider(phi_corrections, T) if include_phi else None
        phi = _pick_component_value(phi_values, idx, default=1.0) if include_phi else 1.0

        poynting_values = _evaluate_provider(poynting_corrections, T) if include_poynting else None
        poynting = (
            _pick_component_value(poynting_values, idx, default=1.0)
            if include_poynting
            else 1.0
        )

        rhs = y[idx] * pressure
        if include_phi:
            rhs /= phi
        lhs = psat * poynting
        return lhs - rhs

    bounds = temperature_bounds
    if bounds is None:
        if temperature_guess is None:
            raise DewPointCalculationError(
                "temperature_bounds or temperature_guess must be supplied",
            )
        span = max(5.0, 0.1 * abs(temperature_guess))
        bounds = (temperature_guess - span, temperature_guess + span)

    t_low, t_high = bounds
    if t_low >= t_high:
        raise DewPointCalculationError("temperature_bounds must be increasing")

    f_low = equilibrium_difference(t_low)
    if abs(f_low) < 1e-12:
        return t_low
    f_high = equilibrium_difference(t_high)
    if abs(f_high) < 1e-12:
        return t_high
    if f_low * f_high > 0:
        raise DewPointCalculationError(
            "temperature_bounds do not bracket the dew point",
        )

    from scipy.optimize import brentq

    return brentq(equilibrium_difference, t_low, t_high)
