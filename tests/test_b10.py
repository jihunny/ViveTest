from __future__ import annotations

import math

from survival_tool import _b_time_from_weibull


def test_b10_known_values():
    # For rho=1 (exponential), B10 = lambda * (-ln(0.9))
    lam = 1000.0
    rho = 1.0
    b10 = _b_time_from_weibull(lam, rho, 0.10)
    assert math.isclose(b10, lam * (-math.log(0.9)), rel_tol=1e-9)


def test_b10_monotonicity():
    # B10 increases with lambda and decreases with rho when lambda fixed (generally)
    lam = 1000.0
    rho_low = 1.2
    rho_high = 2.0
    b10_low_rho = _b_time_from_weibull(lam, rho_low, 0.10)
    b10_high_rho = _b_time_from_weibull(lam, rho_high, 0.10)
    assert b10_low_rho > b10_high_rho

    lam2 = 1200.0
    b10_lam = _b_time_from_weibull(lam2, rho_low, 0.10)
    assert b10_lam > b10_low_rho

